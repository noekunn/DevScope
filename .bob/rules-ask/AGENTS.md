# Project Documentation Rules (Non-Obvious Only)

This file provides guidance for agents working in Ask mode.

## Non-Obvious Architecture Patterns
- **Strict unidirectional flow**: Analyzers → Graph → Semantic → Generators (reverse imports forbidden)
- **Neo4j singleton**: MUST use `get_instance()` - direct `__init__()` raises RuntimeError
- **Granite fallback**: Returns placeholder text if credentials missing (never raises exceptions)
- **Streamlit state**: ALL variables initialized in `app.py` before page navigation

## Hidden Implementation Details
- Neo4j schema uses `File`, `Function`, `Class`, `Module` labels (NOT `CodeElement`)
- Graph algorithms assume specific property names: `path`, `language`, `lines`, `complexity`
- Relationship types are hardcoded: `IMPORTS`, `CALLS`, `CONTAINS`, `DEPENDS_ON`, `BELONGS_TO`
- Pipeline stages in `orchestrate/pipeline.py` are designed for watsonx Orchestrate integration

## Counterintuitive Patterns
- Type hints use `Optional[Type]` not `Type | None` (Python 3.11+ but old-style hints)
- Error handling prefers `fallback_mode = True` over raising exceptions
- Streamlit pages numbered `01_`, `02_` not `1_`, `2_` (string sorting requirement)

## Mode Purpose
Ask mode is for explanations, documentation, and answering questions without making code changes.