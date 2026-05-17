"""
Graph Builder for DevScope.

Connects analyzers to Neo4j by:
- Running dependency and complexity analysis
- Creating nodes and relationships in Neo4j
- Detecting communities and assigning modules
- Providing summary statistics
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from ..analyzers import DependencyAnalyzer, ComplexityAnalyzer
from .neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Builds a knowledge graph from codebase analysis.
    
    Orchestrates:
    1. Dependency analysis (imports and calls)
    2. Complexity analysis (metrics and hotspots)
    3. Graph construction in Neo4j
    4. Community detection for module assignment
    """
    
    def __init__(self, neo4j_client: Optional[Neo4jClient] = None):
        """
        Initialize graph builder.
        
        Args:
            neo4j_client: Optional Neo4j client (uses singleton if not provided)
        """
        self.client = neo4j_client or Neo4jClient.get_instance()
        self.nodes_created = 0
        self.relationships_created = 0
        self.modules_detected = 0
    
    def build_graph(self, repo_path: str, clear_existing: bool = True) -> Dict[str, Any]:
        """
        Build complete knowledge graph from repository.
        
        Args:
            repo_path: Path to repository root
            clear_existing: Whether to clear existing graph data
            
        Returns:
            Summary dictionary with statistics
        """
        logger.info(f"Building knowledge graph for: {repo_path}")
        
        # Clear existing data if requested
        if clear_existing:
            logger.info("Clearing existing graph data...")
            self.client.clear_database()
        
        # Step 1: Run dependency analysis
        logger.info("Step 1/5: Running dependency analysis...")
        dep_analyzer = DependencyAnalyzer(repo_path)
        dep_results = dep_analyzer.analyze()
        
        # Step 2: Run complexity analysis
        logger.info("Step 2/5: Running complexity analysis...")
        complexity_analyzer = ComplexityAnalyzer(repo_path)
        complexity_results = complexity_analyzer.analyze()
        
        # Step 3: Create nodes from complexity analysis
        logger.info("Step 3/5: Creating nodes in graph...")
        file_node_map = self._create_nodes(complexity_results)
        
        # Step 4: Create relationships from dependency analysis
        logger.info("Step 4/5: Creating relationships in graph...")
        self._create_relationships(dep_results, file_node_map)
        
        # Step 5: Detect communities and assign modules
        logger.info("Step 5/5: Detecting communities...")
        communities = self._detect_and_assign_modules()
        
        # Generate summary
        summary = {
            'repo_path': repo_path,
            'nodes_created': self.nodes_created,
            'relationships_created': self.relationships_created,
            'modules_detected': len(communities),
            'files_analyzed': len(complexity_results),
            'import_edges': len(dep_results['imports']),
            'call_edges': len(dep_results['calls']),
            'complexity_summary': complexity_analyzer.get_summary(),
            'communities': communities[:5]  # Top 5 communities
        }
        
        logger.info(f"Graph building complete: {self.nodes_created} nodes, "
                   f"{self.relationships_created} relationships, "
                   f"{len(communities)} modules detected")
        
        return summary
    
    def _create_nodes(self, complexity_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Create nodes from complexity analysis results.
        
        Args:
            complexity_results: List of file metrics from ComplexityAnalyzer
            
        Returns:
            Mapping of file paths to node IDs
        """
        file_node_map = {}
        
        for file_metrics in complexity_results:
            file_path = file_metrics['file']
            
            # Determine language from file extension
            language = self._detect_language(file_path)
            
            # Create file node
            try:
                node_id = self.client.create_file_node(
                    path=file_path,
                    language=language,
                    lines=file_metrics['total_lines'],
                    complexity=file_metrics['avg_complexity'],
                    source_lines=file_metrics['source_lines'],
                    comment_lines=file_metrics['comment_lines'],
                    blank_lines=file_metrics['blank_lines'],
                    max_complexity=file_metrics['max_complexity'],
                    function_count=file_metrics['function_count'],
                    hotspot_count=file_metrics['hotspot_count']
                )
                
                file_node_map[file_path] = node_id
                self.nodes_created += 1
                
                # Create function nodes for this file
                for func in file_metrics['functions']:
                    try:
                        func_node_id = self.client.create_function_node(
                            name=func['name'],
                            file_path=file_path,
                            complexity=func['complexity'],
                            params=[],  # Parameters not extracted yet
                            lines=func['lines'],
                            is_hotspot=func['is_hotspot'],
                            rank=func['rank'],
                            lineno=func['lineno']
                        )
                        
                        # Create CONTAINS relationship from file to function
                        self.client.create_relationship(
                            source=file_path,
                            target=f"{file_path}::{func['name']}",
                            rel_type='CONTAINS',
                            properties={'type': 'function'}
                        )
                        
                        self.nodes_created += 1
                        self.relationships_created += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to create function node {func['name']}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Failed to create file node for {file_path}: {e}")
                continue
        
        return file_node_map
    
    def _create_relationships(self, dep_results: Dict[str, List[Dict]], 
                            file_node_map: Dict[str, str]):
        """
        Create relationships from dependency analysis results.
        
        Args:
            dep_results: Results from DependencyAnalyzer
            file_node_map: Mapping of file paths to node IDs
        """
        # Create import relationships
        for import_edge in dep_results['imports']:
            source = import_edge['source']
            target = import_edge['target']
            
            # Only create relationship if both nodes exist
            if source in file_node_map:
                try:
                    # Handle module imports (may not be in our codebase)
                    if target not in file_node_map:
                        # Create a module node for external dependency
                        module_id = self.client.create_module_node(
                            name=target,
                            description=f"External module: {target}"
                        )
                        file_node_map[target] = module_id
                        self.nodes_created += 1
                    
                    self.client.create_relationship(
                        source=source,
                        target=target,
                        rel_type='IMPORTS',
                        properties={
                            'import_type': import_edge['import_type'],
                            'imported_names': import_edge.get('imported_names', [])
                        }
                    )
                    self.relationships_created += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to create import relationship {source} -> {target}: {e}")
                    continue
        
        # Create call relationships
        for call_edge in dep_results['calls']:
            source_file = call_edge['source_file']
            target_function = call_edge['target_function']
            target_file = call_edge.get('target_file')
            
            if source_file in file_node_map:
                try:
                    # If we know the target file, create CALLS relationship
                    if target_file and target_file in file_node_map:
                        self.client.create_relationship(
                            source=source_file,
                            target=target_file,
                            rel_type='CALLS',
                            properties={'function': target_function}
                        )
                        self.relationships_created += 1
                    
                    # Also create DEPENDS_ON for stronger coupling
                    if target_file and target_file in file_node_map and target_file != source_file:
                        self.client.create_relationship(
                            source=source_file,
                            target=target_file,
                            rel_type='DEPENDS_ON',
                            properties={'reason': 'function_call'}
                        )
                        self.relationships_created += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to create call relationship: {e}")
                    continue
    
    def _detect_and_assign_modules(self) -> List[Dict[str, Any]]:
        """
        Detect communities and assign module labels.
        
        Returns:
            List of detected communities
        """
        try:
            communities = self.client.detect_communities()
            self.modules_detected = len(communities)
            
            # Assign module labels to nodes based on communities
            for i, community in enumerate(communities):
                module_name = f"Module_{i+1}"
                
                # Create a module node
                try:
                    self.client.create_module_node(
                        name=module_name,
                        description=f"Auto-detected module with {community['size']} files"
                    )
                    self.nodes_created += 1
                    
                    # Link files to module
                    for member in community.get('members', []):
                        if member:
                            try:
                                self.client.create_relationship(
                                    source=member,
                                    target=module_name,
                                    rel_type='BELONGS_TO',
                                    properties={'community_id': community.get('community_id', i)}
                                )
                                self.relationships_created += 1
                            except Exception as e:
                                logger.warning(f"Failed to link {member} to {module_name}: {e}")
                                continue
                                
                except Exception as e:
                    logger.warning(f"Failed to create module node {module_name}: {e}")
                    continue
            
            return communities
            
        except Exception as e:
            logger.error(f"Failed to detect communities: {e}")
            return []
    
    def _detect_language(self, file_path: str) -> str:
        """
        Detect programming language from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Language name
        """
        ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        return language_map.get(ext, 'unknown')
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get current graph statistics.
        
        Returns:
            Dictionary with graph metrics
        """
        return {
            'nodes_created': self.nodes_created,
            'relationships_created': self.relationships_created,
            'modules_detected': self.modules_detected
        }


# Example usage
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python graph_builder.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    builder = GraphBuilder()
    summary = builder.build_graph(repo_path)
    
    print("\n=== Graph Building Summary ===")
    print(json.dumps(summary, indent=2, default=str))

# Made with Bob
