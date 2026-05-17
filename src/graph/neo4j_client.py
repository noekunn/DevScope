"""
Neo4j Client for DevScope.

Provides a singleton Neo4j client with:
- Connection management with connection pooling
- Node and relationship creation methods
- Graph algorithms (PageRank, community detection, cycle detection)
- Impact analysis and onboarding path generation
- NetworkX fallback mode when Neo4j is unavailable
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import logging
from neo4j import GraphDatabase, Driver, Session
import networkx as nx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jClient:
    """
    Singleton Neo4j client for DevScope knowledge graph.
    
    Manages connections to Neo4j Aura and provides methods for:
    - Creating nodes (files, functions, classes, modules)
    - Creating relationships
    - Running graph algorithms
    - Impact analysis
    
    Falls back to NetworkX if Neo4j is unavailable.
    """
    
    _instance: Optional['Neo4jClient'] = None
    
    def __init__(self):
        """Initialize Neo4j client (use get_instance() instead)."""
        raise RuntimeError("Use Neo4jClient.get_instance() instead of constructor")
    
    @classmethod
    def get_instance(cls) -> 'Neo4jClient':
        """
        Get singleton instance of Neo4j client.
        
        Returns:
            Neo4jClient instance
        """
        if cls._instance is None:
            instance = cls.__new__(cls)
            instance._initialize()
            cls._instance = instance
        return cls._instance
    
    def _initialize(self):
        """Initialize the Neo4j client instance."""
        # Load credentials from environment
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', '')
        
        self.driver: Optional[Driver] = None
        self.connected = False
        self.fallback_mode = False
        
        # NetworkX fallback graph
        self.nx_graph = nx.DiGraph()
        
        # Try to connect
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.connected = True
            self.fallback_mode = False
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}. Using NetworkX fallback mode.")
            self.connected = False
            self.fallback_mode = True
            self.driver = None
    
    def is_connected(self) -> bool:
        """Check if connected to Neo4j."""
        return self.connected
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.connected = False
            logger.info("Neo4j connection closed")
    
    def clear_database(self):
        """
        Clear all nodes and relationships from the database.
        
        WARNING: This deletes all data!
        """
        if self.fallback_mode:
            self.nx_graph.clear()
            logger.info("Cleared NetworkX graph")
            return
        
        if not self.connected:
            raise RuntimeError("Not connected to Neo4j")
        
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("Cleared Neo4j database")
    
    def create_file_node(self, path: str, language: str, lines: int, 
                        complexity: float, **kwargs) -> str:
        """
        Create a file node in the graph.
        
        Args:
            path: File path relative to repo root
            language: Programming language (python, javascript, etc.)
            lines: Total lines of code
            complexity: Average complexity score
            **kwargs: Additional properties
            
        Returns:
            Node ID
        """
        properties = {
            'path': path,
            'language': language,
            'lines': lines,
            'complexity': complexity,
            'type': 'file',
            **kwargs
        }
        
        if self.fallback_mode:
            self.nx_graph.add_node(path, **properties)
            return path
        
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (f:CodeElement:File {
                    path: $path,
                    language: $language,
                    lines: $lines,
                    complexity: $complexity,
                    type: 'file'
                })
                RETURN elementId(f) as id
                """,
                **properties
            )
            return result.single()['id']
    
    def create_function_node(self, name: str, file_path: str, complexity: int,
                           params: List[str], **kwargs) -> str:
        """
        Create a function node in the graph.
        
        Args:
            name: Function name
            file_path: Path to file containing function
            complexity: Cyclomatic complexity
            params: List of parameter names
            **kwargs: Additional properties
            
        Returns:
            Node ID
        """
        properties = {
            'name': name,
            'file_path': file_path,
            'complexity': complexity,
            'params': params,
            'type': 'function',
            **kwargs
        }
        
        node_id = f"{file_path}::{name}"
        
        if self.fallback_mode:
            self.nx_graph.add_node(node_id, **properties)
            return node_id
        
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (f:CodeElement:Function {
                    name: $name,
                    file_path: $file_path,
                    complexity: $complexity,
                    params: $params,
                    type: 'function'
                })
                RETURN elementId(f) as id
                """,
                **properties
            )
            return result.single()['id']
    
    def create_class_node(self, name: str, file_path: str, methods_count: int,
                         **kwargs) -> str:
        """
        Create a class node in the graph.
        
        Args:
            name: Class name
            file_path: Path to file containing class
            methods_count: Number of methods in class
            **kwargs: Additional properties
            
        Returns:
            Node ID
        """
        properties = {
            'name': name,
            'file_path': file_path,
            'methods_count': methods_count,
            'type': 'class',
            **kwargs
        }
        
        node_id = f"{file_path}::{name}"
        
        if self.fallback_mode:
            self.nx_graph.add_node(node_id, **properties)
            return node_id
        
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (c:CodeElement:Class {
                    name: $name,
                    file_path: $file_path,
                    methods_count: $methods_count,
                    type: 'class'
                })
                RETURN elementId(c) as id
                """,
                **properties
            )
            return result.single()['id']
    
    def create_module_node(self, name: str, description: str, **kwargs) -> str:
        """
        Create a module node in the graph.
        
        Args:
            name: Module name
            description: Module description
            **kwargs: Additional properties
            
        Returns:
            Node ID
        """
        properties = {
            'name': name,
            'description': description,
            'type': 'module',
            **kwargs
        }
        
        if self.fallback_mode:
            self.nx_graph.add_node(name, **properties)
            return name
        
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (m:CodeElement:Module {
                    name: $name,
                    description: $description,
                    type: 'module'
                })
                RETURN elementId(m) as id
                """,
                **properties
            )
            return result.single()['id']
    
    def create_relationship(self, source: str, target: str, rel_type: str,
                          properties: Optional[Dict[str, Any]] = None):
        """
        Create a relationship between two nodes.
        
        Args:
            source: Source node identifier (path or ID)
            target: Target node identifier (path or ID)
            rel_type: Relationship type (IMPORTS, CALLS, CONTAINS, DEPENDS_ON)
            properties: Optional relationship properties
        """
        if properties is None:
            properties = {}
        
        if self.fallback_mode:
            self.nx_graph.add_edge(source, target, type=rel_type, **properties)
            return
        
        with self.driver.session() as session:
            # Match by path for files, by name for functions/classes
            session.run(
                f"""
                MATCH (s:CodeElement), (t:CodeElement)
                WHERE s.path = $source OR s.name = $source OR elementId(s) = $source
                AND t.path = $target OR t.name = $target OR elementId(t) = $target
                CREATE (s)-[r:{rel_type}]->(t)
                SET r += $properties
                """,
                source=source,
                target=target,
                properties=properties
            )
    
    def run_pagerank(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Run PageRank algorithm to find most critical files.
        
        Args:
            top_n: Number of top results to return
            
        Returns:
            List of files with their PageRank scores
        """
        if self.fallback_mode:
            if len(self.nx_graph.nodes()) == 0:
                return []
            
            pagerank = nx.pagerank(self.nx_graph)
            sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
            
            return [
                {
                    'node': node,
                    'score': score,
                    'properties': self.nx_graph.nodes[node]
                }
                for node, score in sorted_nodes[:top_n]
            ]
        
        with self.driver.session() as session:
            result = session.run(
                """
                CALL gds.pageRank.stream({
                    nodeProjection: 'CodeElement',
                    relationshipProjection: {
                        IMPORTS: {type: 'IMPORTS'},
                        CALLS: {type: 'CALLS'},
                        DEPENDS_ON: {type: 'DEPENDS_ON'}
                    }
                })
                YIELD nodeId, score
                MATCH (n:CodeElement)
                WHERE elementId(n) = nodeId
                RETURN n.path as path, n.name as name, n.type as type, score
                ORDER BY score DESC
                LIMIT $top_n
                """,
                top_n=top_n
            )
            
            return [dict(record) for record in result]
    
    def detect_communities(self) -> List[Dict[str, Any]]:
        """
        Detect communities (module clusters) in the codebase.
        
        Returns:
            List of communities with their members
        """
        if self.fallback_mode:
            if len(self.nx_graph.nodes()) == 0:
                return []
            
            # Use Louvain community detection
            communities = nx.community.louvain_communities(self.nx_graph.to_undirected())
            
            return [
                {
                    'community_id': i,
                    'members': list(community),
                    'size': len(community)
                }
                for i, community in enumerate(communities)
            ]
        
        with self.driver.session() as session:
            result = session.run(
                """
                CALL gds.louvain.stream({
                    nodeProjection: 'CodeElement',
                    relationshipProjection: {
                        IMPORTS: {type: 'IMPORTS', orientation: 'UNDIRECTED'},
                        DEPENDS_ON: {type: 'DEPENDS_ON', orientation: 'UNDIRECTED'}
                    }
                })
                YIELD nodeId, communityId
                MATCH (n:CodeElement)
                WHERE elementId(n) = nodeId
                RETURN communityId, collect(n.path) as members, count(*) as size
                ORDER BY size DESC
                """)
            
            return [dict(record) for record in result]
    
    def find_impact_radius(self, file_path: str, depth: int = 3) -> List[str]:
        """
        Find what breaks if a file changes (impact radius).
        
        Args:
            file_path: Path to the file
            depth: Maximum depth to traverse
            
        Returns:
            List of affected file paths
        """
        if self.fallback_mode:
            if file_path not in self.nx_graph:
                return []
            
            # Find all nodes reachable within depth
            affected = set()
            for node in nx.single_source_shortest_path_length(
                self.nx_graph, file_path, cutoff=depth
            ).keys():
                if node != file_path:
                    affected.add(node)
            
            return list(affected)
        
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = (start:CodeElement {path: $file_path})-[*1..$depth]->(affected:CodeElement)
                WHERE start <> affected
                RETURN DISTINCT affected.path as path
                """,
                file_path=file_path,
                depth=depth
            )
            
            return [record['path'] for record in result if record['path']]
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Detect circular dependencies in the codebase.
        
        Returns:
            List of cycles (each cycle is a list of file paths)
        """
        if self.fallback_mode:
            try:
                cycles = list(nx.simple_cycles(self.nx_graph))
                return cycles
            except:
                return []
        
        with self.driver.session() as session:
            # Find cycles using path matching
            result = session.run(
                """
                MATCH path = (n:CodeElement)-[*2..10]->(n)
                WHERE n.type = 'file'
                RETURN [node in nodes(path) | node.path] as cycle
                LIMIT 100
                """
            )
            
            cycles = [record['cycle'] for record in result]
            # Remove duplicates
            unique_cycles = []
            seen = set()
            for cycle in cycles:
                cycle_tuple = tuple(sorted(cycle))
                if cycle_tuple not in seen:
                    seen.add(cycle_tuple)
                    unique_cycles.append(cycle)
            
            return unique_cycles
    
    def get_onboarding_path(self, entry_file: str, role: str = "developer") -> List[Dict[str, Any]]:
        """
        Generate a guided traversal path for new developers.
        
        Args:
            entry_file: Starting file (e.g., main.py, app.py)
            role: Developer role (developer, frontend, backend, etc.)
            
        Returns:
            Ordered list of files to explore with context
        """
        if self.fallback_mode:
            if entry_file not in self.nx_graph:
                return []
            
            # Use BFS to create exploration path
            path = []
            visited = set()
            queue = [(entry_file, 0)]
            
            while queue and len(path) < 20:
                node, depth = queue.pop(0)
                if node in visited:
                    continue
                
                visited.add(node)
                node_data = self.nx_graph.nodes.get(node, {})
                
                path.append({
                    'file': node,
                    'depth': depth,
                    'complexity': node_data.get('complexity', 0),
                    'type': node_data.get('type', 'unknown')
                })
                
                # Add neighbors
                for neighbor in self.nx_graph.successors(node):
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))
            
            return path
        
        with self.driver.session() as session:
            # Create a breadth-first traversal path
            result = session.run(
                """
                MATCH path = (start:CodeElement {path: $entry_file})-[*0..5]->(n:CodeElement)
                WHERE n.type = 'file'
                WITH n, length(path) as depth, n.complexity as complexity
                ORDER BY depth, complexity
                RETURN DISTINCT n.path as file, depth, complexity, n.type as type
                LIMIT 20
                """,
                entry_file=entry_file
            )
            
            return [dict(record) for record in result]


# Example usage
if __name__ == "__main__":
    client = Neo4jClient.get_instance()
    
    if client.is_connected():
        print("✓ Connected to Neo4j")
    else:
        print("✗ Using NetworkX fallback mode")
    
    # Example operations
    # client.clear_database()
    # client.create_file_node("src/main.py", "python", 150, 5.2)
    # client.create_function_node("main", "src/main.py", 3, ["args"])
    # client.create_relationship("src/main.py", "src/utils.py", "IMPORTS")

# Made with Bob
