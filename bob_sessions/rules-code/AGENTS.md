# Project Coding Rules (Non-Obvious Only)

This file provides coding-specific guidance for agents working in Code mode.

## Critical Patterns
- **Layer dependency flow**: Analyzers → Graph → Semantic → Generators (unidirectional only)
  - ✅ `graph_builder.py` can import from `analyzers/`
  - ❌ `analyzers/` must NOT import from `graph/` or higher layers
- **Neo4j singleton**: MUST use `Neo4jClient.get_instance()` - direct `__init__()` raises RuntimeError
- **Granite fallback**: All LLM methods return placeholder text if credentials missing (no exceptions)

## Neo4j Schema (Hard Requirements)
Graph algorithms assume this exact schema:
- Node labels: `File`, `Function`, `Class`, `Module` (NOT `CodeElement`)
- File properties: `path`, `language`, `lines`, `complexity`
- Relationships: `IMPORTS`, `CALLS`, `CONTAINS`, `DEPENDS_ON`, `BELONGS_TO`

## Code Style (Discovered Patterns)
- Type hints: Use `Optional[Type]` for nullable params, not `Type | None`
- Logging: Module-level `logger = logging.getLogger(__name__)` in every file
- Error handling: Graceful fallback (set `fallback_mode = True`) over exceptions
- Docstrings: Google style with Args/Returns sections
- Imports: Standard lib → Third party → Local (separated by blank lines)

## Streamlit Specifics
- Pages MUST be numbered: `01_`, `02_`, `03_`, `04_` (not `1_`, `2_`)
- Use `st.session_state` for cross-page data sharing
- Initialize all state in `app.py` before page navigation

## Mode Restrictions
Code mode cannot access MCP or Browser tools. Use Advanced mode if these are needed.