# 🔍 DevScope — Intelligent Codebase Onboarding & Modernization Engine

> **DevScope builds a living knowledge graph of any codebase — turning code into answers. Ask any question. Get instant, graph-powered intelligence. Onboarding, modernization, and impact analysis — all from one queryable brain.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![Neo4j](https://img.shields.io/badge/Neo4j-Aura-008CC1.svg)](https://neo4j.com/cloud/aura/)
[![IBM watsonx](https://img.shields.io/badge/IBM-watsonx.ai-054ADA.svg)](https://www.ibm.com/watsonx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 The Problem

Developer onboarding costs companies **~$30,000 per hire** in lost productivity. New developers spend **3+ weeks** reading code, asking questions, and building mental models of unfamiliar codebases. Legacy modernization efforts stall because teams lack visibility into architectural dependencies.

## 💡 The Solution

DevScope is a **codebase intelligence platform** that automatically analyzes any repository and generates:

- 🏗️ **Architecture X-Ray** — Deep structural and complexity analysis
- 📚 **Smart Onboarding Guides** — Role-specific guides (Frontend/Backend/Fullstack/DevOps) powered by AI
- 🔄 **Modernization Roadmaps** — Prioritized technical debt and improvement plans
- 🕸️ **Knowledge Graph Explorer** — Interactive visualization with PageRank, community detection, and cycle analysis

---

## 🏛️ Three-Layer Intelligence Stack

```
Layer 3: SEMANTIC (IBM Granite via watsonx.ai)
  "This module handles user auth using JWT. It uses the Repository pattern.
   New backend devs should read auth_service.py first."

Layer 2: ALGORITHMIC (Neo4j Graph Algorithms)
  PageRank → critical files | Community detection → module clusters
  Impact radius → blast analysis | Cycle detection → circular deps

Layer 1: STRUCTURAL (AST + Radon Static Analysis)
  Import detection, call graphs, class hierarchies, complexity metrics
```

---

## 📸 Screenshots

### Main Dashboard — Quick Insights
After analysis, see your codebase health at a glance:
- Health Score (0-100)
- Total files analyzed
- Complexity hotspots
- Module clusters detected

### Codebase X-Ray
- Tech stack detection (Python, JavaScript, TypeScript, etc.)
- Architecture overview with graph node/relationship counts
- Complexity heatmap with color-coded bars

### Knowledge Graph Explorer
- Interactive Pyvis graph visualization
- 321+ nodes with dependency edges
- Filter by file type, highlight clusters
- Sidebar stats: nodes, edges, clusters, cycles

### Onboarding Hub
- Select your role: Frontend, Backend, Fullstack, or DevOps
- Get a personalized onboarding guide with:
  - Architecture overview
  - Critical files to read first (PageRank-ranked)
  - Key patterns & conventions
  - Suggested first PR

### Modernization Roadmap
- Health score breakdown
- Prioritized issues: Critical → High → Medium
- Effort estimates and suggested approaches
- Downloadable markdown roadmap

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Neo4j Aura account (free tier works) — [Sign up here](https://neo4j.com/cloud/aura-free/)
- IBM watsonx.ai account (optional, for semantic enrichment) — [Sign up here](https://www.ibm.com/watsonx)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/devscope.git
cd devscope

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see Configuration below)

# Run the dashboard
python -m streamlit run src/dashboard/app.py
```

### Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```env
# Neo4j Aura (required for full graph features)
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here

# IBM watsonx.ai (optional — enables semantic enrichment)
WATSONX_API_KEY=your-api-key-here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your-project-id-here
```

> **Note:** DevScope works without watsonx.ai credentials — semantic enrichment gracefully degrades to graph-only analysis.

---

## 🏗️ Architecture

```
devscope/
├── src/
│   ├── analyzers/              # Layer 1: Structural Analysis
│   │   ├── dependency_analyzer.py   # AST-based import/call detection
│   │   ├── complexity_analyzer.py   # Radon cyclomatic complexity
│   │   └── pattern_detector.py      # Design pattern recognition
│   ├── graph/                  # Layer 2: Knowledge Graph
│   │   ├── neo4j_client.py          # Neo4j Aura client + NetworkX fallback
│   │   ├── graph_builder.py         # Populates graph from analysis
│   │   └── graph_algorithms.py      # PageRank, communities, cycles
│   ├── semantic/               # Layer 3: AI Enrichment
│   │   ├── granite_client.py        # IBM Granite LLM via watsonx.ai
│   │   └── semantic_enricher.py     # Enriches graph with AI insights
│   ├── generators/             # Output Generation
│   │   ├── onboarding_generator.py  # Role-specific onboarding guides
│   │   ├── modernization_planner.py # Prioritized improvement roadmap
│   │   └── doc_generator.py         # Auto-documentation from analysis
│   ├── dashboard/              # Streamlit Frontend
│   │   ├── app.py                   # Main application + analysis pipeline
│   │   └── pages/
│   │       ├── 01_codebase_xray.py  # Architecture overview + complexity
│   │       ├── 02_onboarding_hub.py # Role selector → personalized guide
│   │       ├── 03_modernization.py  # Prioritized roadmap
│   │       └── 04_graph_explorer.py # Interactive graph browser
│   ├── orchestrate/            # Pipeline Orchestration
│   │   └── pipeline.py             # 5-stage analysis pipeline
│   └── utils/                  # Utilities
│       ├── config.py               # Centralized configuration
│       └── repo_scanner.py         # Git cloning + file traversal
├── skills/
│   └── analyze-codebase.md     # Bob IDE skill for repo analysis
├── slash-commands/
│   └── analyze.md              # Custom /analyze slash command
├── bob_sessions/               # Exported Bob IDE session reports
├── requirements.txt
├── .env.example
├── AGENTS.md                   # Generated by Bob /init
└── LICENSE                     # MIT
```

---

## 🔬 How It Works

### Analysis Pipeline

```
1. 📂 Input     → Local path or GitHub URL
2. 🔍 Scan      → Detect all source files (Python, JS/TS)
3. 📊 Analyze   → Dependency + complexity analysis (AST + Radon)
4. 🕸️ Build     → Construct knowledge graph (Neo4j / NetworkX)
5. 🤖 Enrich    → AI-powered semantic analysis (Granite LLM)
6. 📚 Generate  → Onboarding guides + modernization roadmap
7. 📈 Display   → Interactive Streamlit dashboard
```

### Graph Algorithms

| Algorithm | Purpose | Example Query |
|---|---|---|
| **PageRank** | Find most critical files | "What are the 5 most important files?" |
| **Community Detection** | Discover module clusters | "How is the codebase organized?" |
| **Cycle Detection** | Find circular dependencies | "Are there circular imports?" |
| **Impact Radius** | Blast radius analysis | "What breaks if I change auth.py?" |

---

## 🛠️ Built With

| Technology | Purpose |
|---|---|
| **IBM Bob IDE** | AI-assisted development environment |
| **IBM watsonx.ai** | Granite LLM for semantic code analysis |
| **Neo4j Aura** | Cloud-native graph database |
| **Streamlit** | Interactive dashboard framework |
| **NetworkX** | In-memory graph fallback |
| **Pyvis** | Interactive graph visualization |
| **Radon** | Python code complexity metrics |
| **GitPython** | Repository cloning and management |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **IBM Bob IDE** — AI-powered development environment
- **IBM watsonx.ai** — Enterprise AI platform with Granite models
- **Neo4j** — Graph database powering our knowledge graph
- **Streamlit** — Beautiful data apps in minutes

---

*Built with ❤️ using IBM Bob IDE for the IBM Bob Hackathon 2026*

<!-- Made with Bob -->
