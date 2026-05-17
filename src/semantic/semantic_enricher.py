"""
Semantic Enricher for DevScope.

Enriches Neo4j graph with LLM-powered semantic insights:
- Module summarization
- Architectural role identification
- Pattern detection
- Onboarding priority calculation
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from .granite_client import GraniteClient
from ..graph.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticEnricher:
    """
    Enriches knowledge graph with semantic insights from Granite LLM.
    
    Process:
    1. Get module clusters from Neo4j
    2. Read source files for each module
    3. Generate semantic summaries using Granite
    4. Update Neo4j nodes with enriched metadata
    5. Calculate onboarding priorities
    """
    
    def __init__(self, repo_path: str, neo4j_client: Optional[Neo4jClient] = None,
                 granite_client: Optional[GraniteClient] = None):
        """
        Initialize semantic enricher.
        
        Args:
            repo_path: Path to repository root
            neo4j_client: Optional Neo4j client (uses singleton if not provided)
            granite_client: Optional Granite client (creates new if not provided)
        """
        self.repo_path = Path(repo_path)
        self.neo4j_client = neo4j_client or Neo4jClient.get_instance()
        self.granite_client = granite_client or GraniteClient()
        
        self.modules_enriched = 0
        self.files_processed = 0
    
    def enrich_graph(self) -> Dict[str, Any]:
        """
        Enrich the entire knowledge graph with semantic insights.
        
        Returns:
            Summary dictionary with enrichment statistics
        """
        logger.info("Starting semantic enrichment...")
        
        # Step 1: Get module clusters from Neo4j
        logger.info("Step 1/4: Retrieving module clusters...")
        communities = self.neo4j_client.detect_communities()
        
        if not communities:
            logger.warning("No communities detected. Run graph_builder first.")
            return {
                'modules_enriched': 0,
                'files_processed': 0,
                'tokens_used': 0,
                'cost_estimate': 0.0,
                'error': 'No communities found'
            }
        
        # Step 2: Get PageRank scores for priority calculation
        logger.info("Step 2/4: Calculating PageRank scores...")
        pagerank_scores = self._get_pagerank_scores()
        
        # Step 3: Enrich each module
        logger.info(f"Step 3/4: Enriching {len(communities)} modules...")
        for i, community in enumerate(communities):
            try:
                self._enrich_module(community, pagerank_scores, i + 1)
                self.modules_enriched += 1
            except Exception as e:
                logger.error(f"Failed to enrich module {i+1}: {e}")
                continue
        
        # Step 4: Get usage statistics
        logger.info("Step 4/4: Collecting statistics...")
        usage_stats = self.granite_client.get_usage_stats()
        
        summary = {
            'modules_enriched': self.modules_enriched,
            'files_processed': self.files_processed,
            'tokens_used': usage_stats['total_tokens'],
            'cost_estimate': usage_stats['estimated_cost_usd'],
            'fallback_mode': usage_stats['fallback_mode']
        }
        
        logger.info(f"Semantic enrichment complete: {self.modules_enriched} modules, "
                   f"{self.files_processed} files, "
                   f"{usage_stats['total_tokens']} tokens, "
                   f"${usage_stats['estimated_cost_usd']:.4f} estimated cost")
        
        return summary
    
    def _get_pagerank_scores(self) -> Dict[str, float]:
        """
        Get PageRank scores for all files.
        
        Returns:
            Dictionary mapping file paths to PageRank scores
        """
        try:
            pagerank_results = self.neo4j_client.run_pagerank(top_n=1000)
            
            scores = {}
            for result in pagerank_results:
                file_path = result.get('path') or result.get('name')
                score = result.get('score', 0.0)
                if file_path:
                    scores[file_path] = score
            
            return scores
        except Exception as e:
            logger.warning(f"Failed to get PageRank scores: {e}")
            return {}
    
    def _enrich_module(self, community: Dict[str, Any], 
                      pagerank_scores: Dict[str, float], module_num: int):
        """
        Enrich a single module with semantic insights.
        
        Args:
            community: Community data from Neo4j
            pagerank_scores: PageRank scores for priority calculation
            module_num: Module number for naming
        """
        members = community.get('members', [])
        if not members:
            logger.warning(f"Module {module_num} has no members")
            return
        
        # Read source files
        file_contents = []
        avg_complexity = 0.0
        total_pagerank = 0.0
        
        for file_path in members[:10]:  # Limit to 10 files per module
            if not file_path:
                continue
            
            try:
                full_path = self.repo_path / file_path
                if full_path.exists() and full_path.is_file():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Limit file size
                        if len(content) > 5000:
                            content = content[:5000] + "\n... (truncated)"
                        file_contents.append(content)
                        self.files_processed += 1
                
                # Get PageRank score
                total_pagerank += pagerank_scores.get(file_path, 0.0)
                
            except Exception as e:
                logger.warning(f"Failed to read {file_path}: {e}")
                continue
        
        if not file_contents:
            logger.warning(f"No readable files in module {module_num}")
            return
        
        # Generate semantic summary
        logger.info(f"Generating summary for Module_{module_num} ({len(file_contents)} files)...")
        summary = self.granite_client.summarize_module(file_contents)
        
        # Calculate onboarding priority
        avg_pagerank = total_pagerank / len(members) if members else 0.0
        priority = self._calculate_priority(avg_pagerank, avg_complexity)
        
        # Update Neo4j module node
        module_name = f"Module_{module_num}"
        self._update_module_node(
            module_name=module_name,
            purpose=summary.get('purpose', 'Unknown'),
            architectural_role=summary.get('architectural_role', 'Unknown'),
            patterns=summary.get('patterns_detected', 'None'),
            key_insight=summary.get('key_insight', ''),
            onboarding_priority=priority,
            file_count=len(members),
            avg_pagerank=avg_pagerank
        )
        
        logger.info(f"Enriched {module_name}: {summary.get('architectural_role')} "
                   f"(priority: {priority})")
    
    def _calculate_priority(self, pagerank_score: float, complexity: float) -> str:
        """
        Calculate onboarding priority based on PageRank and complexity.
        
        Args:
            pagerank_score: Average PageRank score for module
            complexity: Average complexity score
            
        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        # High priority: High PageRank (important) OR high complexity (needs attention)
        if pagerank_score > 0.01 or complexity > 15:
            return 'high'
        # Medium priority: Moderate PageRank or complexity
        elif pagerank_score > 0.005 or complexity > 8:
            return 'medium'
        # Low priority: Low PageRank and complexity
        else:
            return 'low'
    
    def _update_module_node(self, module_name: str, purpose: str,
                           architectural_role: str, patterns: str,
                           key_insight: str, onboarding_priority: str,
                           file_count: int, avg_pagerank: float):
        """
        Update Neo4j module node with semantic metadata.
        
        Args:
            module_name: Name of the module node
            purpose: Plain-language description
            architectural_role: Role in system architecture
            patterns: Design patterns detected
            key_insight: Most important insight
            onboarding_priority: Priority level for onboarding
            file_count: Number of files in module
            avg_pagerank: Average PageRank score
        """
        if self.neo4j_client.fallback_mode:
            # In fallback mode, just log
            logger.info(f"Would update {module_name} with semantic data (fallback mode)")
            return
        
        try:
            with self.neo4j_client.driver.session() as session:
                session.run(
                    """
                    MATCH (m:Module {name: $module_name})
                    SET m.purpose = $purpose,
                        m.architectural_role = $architectural_role,
                        m.patterns = $patterns,
                        m.key_insight = $key_insight,
                        m.onboarding_priority = $onboarding_priority,
                        m.file_count = $file_count,
                        m.avg_pagerank = $avg_pagerank,
                        m.enriched = true
                    """,
                    module_name=module_name,
                    purpose=purpose,
                    architectural_role=architectural_role,
                    patterns=patterns,
                    key_insight=key_insight,
                    onboarding_priority=onboarding_priority,
                    file_count=file_count,
                    avg_pagerank=avg_pagerank
                )
        except Exception as e:
            logger.error(f"Failed to update module node {module_name}: {e}")
    
    def get_enriched_modules(self) -> List[Dict[str, Any]]:
        """
        Get all enriched modules with their semantic metadata.
        
        Returns:
            List of enriched module data
        """
        if self.neo4j_client.fallback_mode:
            logger.warning("Cannot retrieve modules in fallback mode")
            return []
        
        try:
            with self.neo4j_client.driver.session() as session:
                result = session.run(
                    """
                    MATCH (m:Module)
                    WHERE m.enriched = true
                    RETURN m.name as name,
                           m.purpose as purpose,
                           m.architectural_role as role,
                           m.patterns as patterns,
                           m.key_insight as insight,
                           m.onboarding_priority as priority,
                           m.file_count as file_count,
                           m.avg_pagerank as pagerank
                    ORDER BY m.onboarding_priority DESC, m.avg_pagerank DESC
                    """
                )
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Failed to retrieve enriched modules: {e}")
            return []


# Example usage
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python semantic_enricher.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    enricher = SemanticEnricher(repo_path)
    summary = enricher.enrich_graph()
    
    print("\n=== Semantic Enrichment Summary ===")
    print(json.dumps(summary, indent=2))
    
    # Show enriched modules
    modules = enricher.get_enriched_modules()
    print(f"\n=== Enriched Modules ({len(modules)}) ===")
    for module in modules:
        print(f"\n{module['name']} ({module['priority']} priority)")
        print(f"  Role: {module['role']}")
        print(f"  Purpose: {module['purpose'][:100]}...")

# Made with Bob
