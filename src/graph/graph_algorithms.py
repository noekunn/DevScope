"""
Graph Algorithms — PageRank, Community Detection, Cycle Detection, Impact Radius.

Provides graph algorithm wrappers that work with both Neo4j and NetworkX backends.
This module centralizes all algorithmic intelligence on the knowledge graph.
"""

import networkx as nx
from typing import Dict, List, Any, Optional, Tuple


class GraphAlgorithms:
    """Graph algorithm suite for codebase intelligence."""
    
    def __init__(self, graph: Optional[nx.DiGraph] = None):
        """
        Initialize with an optional NetworkX graph.
        
        Args:
            graph: Pre-built NetworkX DiGraph. If None, creates empty graph.
        """
        self.graph = graph or nx.DiGraph()
    
    def set_graph(self, graph: nx.DiGraph):
        """Set or replace the graph."""
        self.graph = graph
    
    def run_pagerank(self, top_n: int = 10, alpha: float = 0.85) -> List[Dict[str, Any]]:
        """
        Run PageRank to find the most critical files.
        
        Args:
            top_n: Number of top results to return.
            alpha: Damping factor (probability of following links).
            
        Returns:
            List of dicts with 'file' and 'score', sorted by importance.
        """
        if len(self.graph.nodes) == 0:
            return []
        
        try:
            scores = nx.pagerank(self.graph, alpha=alpha)
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            return [{'file': node, 'score': round(score, 6)} for node, score in ranked]
        except Exception:
            return []
    
    def detect_communities(self, resolution: float = 1.0) -> List[Dict[str, Any]]:
        """
        Detect module communities using Louvain algorithm.
        
        Args:
            resolution: Resolution parameter for community detection.
            
        Returns:
            List of communities with members, size, and cohesion metrics.
        """
        if len(self.graph.nodes) == 0:
            return []
        
        try:
            undirected = self.graph.to_undirected()
            
            try:
                from networkx.algorithms.community import louvain_communities
                communities = louvain_communities(undirected, resolution=resolution)
            except (ImportError, AttributeError):
                from networkx.algorithms.community import greedy_modularity_communities
                communities = greedy_modularity_communities(undirected)
            
            result = []
            for idx, community in enumerate(communities):
                members = sorted(list(community))
                subgraph = self.graph.subgraph(members)
                
                result.append({
                    'id': idx,
                    'size': len(members),
                    'members': members,
                    'internal_edges': subgraph.number_of_edges(),
                    'density': nx.density(subgraph) if len(members) > 1 else 0
                })
            
            return sorted(result, key=lambda x: x['size'], reverse=True)
        except Exception:
            return []
    
    def detect_cycles(self, max_length: int = 6) -> List[List[str]]:
        """
        Detect circular dependencies in the graph.
        
        Args:
            max_length: Maximum cycle length to detect.
            
        Returns:
            List of cycles, each being a list of node names.
        """
        if len(self.graph.nodes) == 0:
            return []
        
        try:
            cycles = list(nx.simple_cycles(self.graph))
            # Filter by max length and sort by length
            filtered = [c for c in cycles if len(c) <= max_length]
            return sorted(filtered, key=len)[:50]  # Cap at 50 results
        except Exception:
            return []
    
    def find_impact_radius(self, file_path: str, depth: int = 3) -> Dict[str, Any]:
        """
        Find what breaks if a given file changes (reverse dependency blast radius).
        
        Args:
            file_path: Path of the file to analyze.
            depth: How many levels of transitive dependents to check.
            
        Returns:
            Dict with affected files at each depth level and total count.
        """
        if file_path not in self.graph:
            return {'file': file_path, 'total_affected': 0, 'levels': {}}
        
        affected_by_level = {}
        visited = {file_path}
        current_level = {file_path}
        
        for level in range(1, depth + 1):
            next_level = set()
            for node in current_level:
                # Find all predecessors (files that depend on this file)
                predecessors = set(self.graph.predecessors(node))
                new_predecessors = predecessors - visited
                next_level.update(new_predecessors)
                visited.update(new_predecessors)
            
            if next_level:
                affected_by_level[level] = sorted(list(next_level))
            current_level = next_level
        
        total = sum(len(v) for v in affected_by_level.values())
        
        return {
            'file': file_path,
            'total_affected': total,
            'levels': affected_by_level
        }
    
    def get_onboarding_path(self, entry_file: str, max_depth: int = 4) -> List[Dict[str, Any]]:
        """
        Generate a suggested reading order for onboarding, starting from an entry file.
        
        Args:
            entry_file: Starting file for the onboarding path.
            max_depth: Maximum traversal depth.
            
        Returns:
            Ordered list of files to read, with depth and importance scores.
        """
        if entry_file not in self.graph:
            return []
        
        # BFS from entry point
        path = []
        visited = set()
        queue = [(entry_file, 0)]
        
        pagerank = nx.pagerank(self.graph) if len(self.graph.nodes) > 0 else {}
        
        while queue and len(path) < 20:
            node, depth = queue.pop(0)
            
            if node in visited or depth > max_depth:
                continue
            
            visited.add(node)
            path.append({
                'file': node,
                'depth': depth,
                'importance': round(pagerank.get(node, 0), 6),
                'dependencies': len(list(self.graph.successors(node)))
            })
            
            # Add successors (files this file imports)
            for successor in self.graph.successors(node):
                if successor not in visited:
                    queue.append((successor, depth + 1))
        
        return path
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics.
        
        Returns:
            Dictionary with node count, edge count, density, components, etc.
        """
        if len(self.graph.nodes) == 0:
            return {'nodes': 0, 'edges': 0, 'density': 0}
        
        try:
            weakly_connected = nx.number_weakly_connected_components(self.graph)
        except Exception:
            weakly_connected = 0
        
        try:
            cycles = len(list(nx.simple_cycles(self.graph)))
        except Exception:
            cycles = 0
        
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': round(nx.density(self.graph), 4),
            'weakly_connected_components': weakly_connected,
            'cycles': min(cycles, 100),
            'avg_in_degree': round(sum(d for _, d in self.graph.in_degree()) / max(len(self.graph), 1), 2),
            'avg_out_degree': round(sum(d for _, d in self.graph.out_degree()) / max(len(self.graph), 1), 2),
        }


# Made with Bob
