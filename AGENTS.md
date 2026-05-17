# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Build/Run Commands
```bash
# Run dashboard (main entry point)
streamlit run src/dashboard/app.py

# Run pipeline standalone
python -m src.orchestrate.pipeline /path/to/repo fullstack

# Install dependencies (requirements.txt not yet created)
pip install streamlit neo4j ibm-watsonx-ai pyvis networkx radon gitpython
```

## Critical Non-Obvious Patterns
- **Unidirectional layer flow**: Analyzers → Graph → Semantic → Generators (NEVER reverse)
  - ✅ `graph_builder.py` imports from `analyzers/`
  - ❌ `analyzers/` CANNOT import from `graph/` or higher
- **Neo4j singleton**: MUST use `Neo4jClient.get_instance()` - direct `__init__()` raises RuntimeError
- **Granite fallback**: All LLM methods return placeholder text if credentials missing (no exceptions)
- **Streamlit numbering**: Pages MUST be `01_`, `02_`, `03_`, `04_` (not `1_`, `2_`)
- **Session state init**: ALL state variables initialized in `app.py` before page navigation

## Code Style (Discovered Patterns)
- Type hints: Use `Optional[Type]` for nullable params, not `Type | None`
- Logging: Module-level `logger = logging.getLogger(__name__)` in every file
- Error handling: Graceful fallback (set `fallback_mode = True`) over exceptions
- Docstrings: Google style with Args/Returns sections
- Imports: Standard lib → Third party → Local (separated by blank lines)

## Neo4j Schema (Hard Requirements)
Graph algorithms assume this exact schema:
- Node labels: `File`, `Function`, `Class`, `Module` (NOT `CodeElement`)
- File properties: `path`, `language`, `lines`, `complexity`
- Relationships: `IMPORTS`, `CALLS`, `CONTAINS`, `DEPENDS_ON`, `BELONGS_TO`

## Environment Variables
All credentials via `.env` (never hardcode):
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`