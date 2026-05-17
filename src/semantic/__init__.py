"""
Semantic module for DevScope.

This module provides LLM-powered semantic enrichment:
- Granite client for watsonx.ai integration
- Semantic enricher for adding insights to graph nodes
"""

from .granite_client import GraniteClient
from .semantic_enricher import SemanticEnricher

__all__ = ['GraniteClient', 'SemanticEnricher']

# Made with Bob
