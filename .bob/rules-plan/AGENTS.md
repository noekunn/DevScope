# Project Architecture Rules (Non-Obvious Only)

This file provides guidance for agents working in Plan mode.

## Architecture Constraints
- **Strict layer separation**: Analyzers → Graph → Semantic → Generators (unidirectional only)
- **No circular dependencies**: Higher layers CANNOT import from lower layers (enforced by design)
- **Singleton pattern**: Neo4j client MUST use `get_instance()` - direct `__init__()` raises RuntimeError
- **Fallback design**: Both Neo4j and Granite have graceful fallback modes (no exceptions)

## Hidden Coupling
- Graph algorithms assume exact schema: `File`, `Function`, `Class`, `Module` labels
- Required properties: `path`, `language`, `lines`, `complexity` (algorithms break without these)
- Relationship types hardcoded: `IMPORTS`, `CALLS`, `CONTAINS`, `DEPENDS_ON`, `BELONGS_TO`
- Streamlit pages share state via `st.session_state` - MUST initialize ALL in `app.py`
- Semantic enricher requires complete graph structure before running (no partial enrichment)

## Performance Bottlenecks
- Neo4j connection MUST be established before any graph operations (no lazy init)
- Large codebases need pagination in graph queries (no built-in pagination yet)
- Pyvis graph visualization limited to ~500 nodes (browser performance)

## Critical Design Decisions
- Neo4j chosen for graph algorithms (PageRank, community detection, cycle detection)
- NetworkX fallback when Neo4j unavailable (limited algorithm support)
- Granite LLM for semantic understanding (returns placeholders if credentials missing)
- Pipeline stages designed for watsonx Orchestrate integration (OpenAPI-compatible)
- Type hints use `Optional[Type]` not `Type | None` (Python 3.11+ but old-style for compatibility)

## Mode Purpose
Plan mode is for planning, designing, and strategizing before implementation.