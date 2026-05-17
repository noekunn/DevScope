# Analyze Codebase Skill

## Description
This skill instructs Bob to perform a comprehensive codebase analysis on a target repository using DevScope's three-layer intelligence stack.

## Instructions

When asked to analyze a codebase, follow this pipeline:

### Step 1: Structural Analysis
- Scan all source files (Python, JavaScript, TypeScript)
- Parse import statements and function calls using AST
- Compute cyclomatic complexity using Radon
- Detect complexity hotspots (functions with complexity > 10)

### Step 2: Graph Construction  
- Create file nodes with language, lines, and complexity attributes
- Create function nodes with parameters and return types
- Create IMPORTS and CALLS relationships
- Run community detection to identify module clusters
- Run PageRank to find critical files

### Step 3: Semantic Enrichment
- For each module cluster, generate a plain-language description
- Identify architectural roles (data layer, API layer, UI layer, utility)
- Detect design patterns (Singleton, Factory, Observer, etc.)
- Assess onboarding priority based on PageRank + complexity

### Step 4: Output Generation
- Generate role-specific onboarding guide (Frontend/Backend/Fullstack/DevOps)
- Generate prioritized modernization roadmap
- Generate auto-documentation

## Usage
```
Analyze the codebase at [path or GitHub URL] and generate:
1. Architecture overview
2. Onboarding guide for a [role] developer
3. Modernization roadmap
```

## Context
- Uses: src/analyzers/, src/graph/, src/semantic/, src/generators/
- Output: Markdown reports viewable in Streamlit dashboard
- Dependencies: radon, networkx, neo4j, ibm-watsonx-ai
