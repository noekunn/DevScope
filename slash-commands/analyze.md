# /analyze — Custom Slash Command

## Description
Runs DevScope's full analysis pipeline on a repository.

## Usage
```
/analyze <repo_path_or_url> [--role frontend|backend|fullstack|devops]
```

## Examples
```
/analyze ./my-project
/analyze https://github.com/user/repo --role backend
/analyze C:\Users\dev\projects\app --role fullstack
```

## What It Does
1. **Scans** the repository for source files
2. **Analyzes** dependencies and complexity (AST + Radon)
3. **Builds** a knowledge graph (Neo4j or NetworkX)
4. **Enriches** with AI semantic analysis (Granite LLM)
5. **Generates** onboarding guide + modernization roadmap

## Output
- Architecture overview with module clusters
- Health score (0-100)
- Top critical files (PageRank-ranked)
- Role-specific onboarding guide
- Prioritized modernization roadmap

## Integration
This command triggers `src/orchestrate/pipeline.py:run_full_pipeline()` which chains all 5 analysis stages.
