"""
DevScope Analysis Pipeline for watsonx Orchestrate Integration.

This module defines the complete DevScope analysis pipeline as structured,
auditable stages suitable for watsonx Orchestrate workflow automation.

Each stage is designed to:
- Accept well-defined inputs
- Produce structured outputs
- Log all operations for auditability
- Work standalone or as part of the full pipeline
- Be exposable as watsonx Orchestrate tools via OpenAPI
"""

import logging
import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

# Import DevScope components
from ..analyzers import DependencyAnalyzer, ComplexityAnalyzer
from ..graph import GraphBuilder
from ..semantic import SemanticEnricher
from ..generators import OnboardingGenerator, ModernizationPlanner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _log_stage(stage_name: str, inputs: Dict[str, Any], outputs: Dict[str, Any]):
    """
    Log stage execution for auditability.
    
    Args:
        stage_name: Name of the pipeline stage
        inputs: Input parameters
        outputs: Output results
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'stage': stage_name,
        'inputs': inputs,
        'outputs': outputs
    }
    logger.info(f"Stage {stage_name} completed: {json.dumps(log_entry, default=str)}")


def stage_1_scan(repo_url: str) -> Dict[str, Any]:
    """
    Stage 1: Scan repository and create file manifest.
    
    Scans the repository to identify all source files and create
    a structured manifest for subsequent analysis stages.
    
    OpenAPI Schema:
        parameters:
          - name: repo_url
            in: body
            required: true
            schema:
              type: string
              description: Local path or GitHub URL to repository
              example: "/path/to/repo"
        responses:
          200:
            description: File manifest created successfully
            schema:
              type: object
              properties:
                file_count:
                  type: integer
                  description: Total number of files found
                files:
                  type: array
                  items:
                    type: object
                    properties:
                      path:
                        type: string
                      language:
                        type: string
                      size:
                        type: integer
    
    Args:
        repo_url: Local path or GitHub URL to the repository
        
    Returns:
        Dictionary containing:
        - file_count: Total number of files
        - files: List of file metadata
        - languages: Set of programming languages detected
        - repo_path: Resolved repository path
    """
    inputs = {'repo_url': repo_url}
    
    try:
        # Resolve repository path
        repo_path = Path(repo_url)
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_url}")
        
        # Scan for source files
        extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs'}
        files = []
        languages = set()
        
        for ext in extensions:
            for file_path in repo_path.rglob(f'*{ext}'):
                # Skip common ignore directories
                if any(ignore in file_path.parts for ignore in 
                      {'node_modules', '__pycache__', '.git', 'venv', 'dist', 'build'}):
                    continue
                
                relative_path = str(file_path.relative_to(repo_path))
                language = {
                    '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                    '.jsx': 'javascript', '.tsx': 'typescript', '.java': 'java',
                    '.go': 'go', '.rs': 'rust'
                }.get(ext, 'unknown')
                
                files.append({
                    'path': relative_path,
                    'language': language,
                    'size': file_path.stat().st_size
                })
                languages.add(language)
        
        outputs = {
            'file_count': len(files),
            'files': files,
            'languages': list(languages),
            'repo_path': str(repo_path)
        }
        
        _log_stage('stage_1_scan', inputs, {'file_count': len(files), 'languages': list(languages)})
        return outputs
        
    except Exception as e:
        logger.error(f"Stage 1 failed: {e}")
        raise


def stage_2_analyze(file_manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 2: Analyze code structure and complexity.
    
    Performs dependency analysis and complexity analysis on the
    files identified in the manifest.
    
    OpenAPI Schema:
        parameters:
          - name: file_manifest
            in: body
            required: true
            schema:
              type: object
              description: File manifest from stage 1
        responses:
          200:
            description: Structural analysis completed
            schema:
              type: object
              properties:
                dependencies:
                  type: object
                  description: Dependency analysis results
                complexity:
                  type: object
                  description: Complexity analysis results
                health_score:
                  type: integer
                  description: Overall codebase health score (0-100)
    
    Args:
        file_manifest: Output from stage_1_scan
        
    Returns:
        Dictionary containing:
        - dependencies: Import and call edges
        - complexity: Complexity metrics and hotspots
        - health_score: Overall health score (0-100)
    """
    inputs = {'file_count': file_manifest.get('file_count', 0)}
    
    try:
        repo_path = file_manifest['repo_path']
        
        # Run dependency analysis
        logger.info("Running dependency analysis...")
        dep_analyzer = DependencyAnalyzer(repo_path)
        dep_results = dep_analyzer.analyze()
        
        # Run complexity analysis
        logger.info("Running complexity analysis...")
        complexity_analyzer = ComplexityAnalyzer(repo_path)
        complexity_results = complexity_analyzer.analyze()
        complexity_summary = complexity_analyzer.get_summary()
        
        outputs = {
            'dependencies': {
                'import_count': len(dep_results['imports']),
                'call_count': len(dep_results['calls']),
                'imports': dep_results['imports'],
                'calls': dep_results['calls']
            },
            'complexity': complexity_summary,
            'health_score': complexity_summary['health_score'],
            'repo_path': repo_path
        }
        
        _log_stage('stage_2_analyze', inputs, {
            'import_count': len(dep_results['imports']),
            'health_score': complexity_summary['health_score']
        })
        return outputs
        
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}")
        raise


def stage_3_build_graph(structural_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 3: Build Neo4j knowledge graph.
    
    Constructs a knowledge graph from the structural analysis data,
    including nodes for files/functions and relationships for dependencies.
    
    OpenAPI Schema:
        parameters:
          - name: structural_data
            in: body
            required: true
            schema:
              type: object
              description: Structural analysis from stage 2
        responses:
          200:
            description: Knowledge graph built successfully
            schema:
              type: object
              properties:
                nodes_created:
                  type: integer
                relationships_created:
                  type: integer
                modules_detected:
                  type: integer
    
    Args:
        structural_data: Output from stage_2_analyze
        
    Returns:
        Dictionary containing:
        - nodes_created: Number of graph nodes
        - relationships_created: Number of graph edges
        - modules_detected: Number of module clusters
        - communities: Community detection results
    """
    inputs = {'health_score': structural_data.get('health_score', 0)}
    
    try:
        repo_path = structural_data['repo_path']
        
        # Build knowledge graph
        logger.info("Building knowledge graph...")
        graph_builder = GraphBuilder()
        graph_summary = graph_builder.build_graph(repo_path, clear_existing=True)
        
        outputs = {
            'nodes_created': graph_summary['nodes_created'],
            'relationships_created': graph_summary['relationships_created'],
            'modules_detected': graph_summary['modules_detected'],
            'communities': graph_summary.get('communities', []),
            'repo_path': repo_path
        }
        
        _log_stage('stage_3_build_graph', inputs, {
            'nodes_created': graph_summary['nodes_created'],
            'modules_detected': graph_summary['modules_detected']
        })
        return outputs
        
    except Exception as e:
        logger.error(f"Stage 3 failed: {e}")
        raise


def stage_4_enrich(graph_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 4: Enrich graph with AI-powered semantic insights.
    
    Uses IBM Granite LLM to add semantic understanding to the
    knowledge graph nodes, including module purposes and patterns.
    
    OpenAPI Schema:
        parameters:
          - name: graph_summary
            in: body
            required: true
            schema:
              type: object
              description: Graph summary from stage 3
        responses:
          200:
            description: Semantic enrichment completed
            schema:
              type: object
              properties:
                modules_enriched:
                  type: integer
                tokens_used:
                  type: integer
                cost_estimate:
                  type: number
                  format: float
    
    Args:
        graph_summary: Output from stage_3_build_graph
        
    Returns:
        Dictionary containing:
        - modules_enriched: Number of modules enriched
        - tokens_used: Total LLM tokens consumed
        - cost_estimate: Estimated cost in USD
        - enriched_modules: List of enriched module data
    """
    inputs = {'modules_detected': graph_summary.get('modules_detected', 0)}
    
    try:
        repo_path = graph_summary['repo_path']
        
        # Semantic enrichment
        logger.info("Enriching graph with AI insights...")
        semantic_enricher = SemanticEnricher(repo_path)
        enrichment_summary = semantic_enricher.enrich_graph()
        
        # Get enriched modules
        enriched_modules = semantic_enricher.get_enriched_modules()
        
        outputs = {
            'modules_enriched': enrichment_summary['modules_enriched'],
            'tokens_used': enrichment_summary['tokens_used'],
            'cost_estimate': enrichment_summary['cost_estimate'],
            'enriched_modules': enriched_modules,
            'repo_path': repo_path
        }
        
        _log_stage('stage_4_enrich', inputs, {
            'modules_enriched': enrichment_summary['modules_enriched'],
            'tokens_used': enrichment_summary['tokens_used']
        })
        return outputs
        
    except Exception as e:
        logger.error(f"Stage 4 failed: {e}")
        raise


def stage_5_generate_reports(semantic_data: Dict[str, Any], role: str = 'fullstack') -> Dict[str, Any]:
    """
    Stage 5: Generate onboarding guides and modernization plans.
    
    Creates role-specific onboarding guides and prioritized
    modernization roadmaps based on the enriched knowledge graph.
    
    OpenAPI Schema:
        parameters:
          - name: semantic_data
            in: body
            required: true
            schema:
              type: object
              description: Semantic data from stage 4
          - name: role
            in: query
            required: false
            schema:
              type: string
              enum: [fullstack, frontend, backend, devops]
              default: fullstack
              description: Developer role for onboarding guide
        responses:
          200:
            description: Reports generated successfully
            schema:
              type: object
              properties:
                onboarding_guide:
                  type: string
                  description: Markdown onboarding guide
                modernization_plan:
                  type: string
                  description: Markdown modernization roadmap
    
    Args:
        semantic_data: Output from stage_4_enrich
        role: Developer role (frontend/backend/fullstack/devops)
        
    Returns:
        Dictionary containing:
        - onboarding_guide: Markdown formatted guide
        - modernization_plan: Markdown formatted roadmap
        - role: Role used for guide generation
    """
    inputs = {
        'modules_enriched': semantic_data.get('modules_enriched', 0),
        'role': role
    }
    
    try:
        repo_path = semantic_data['repo_path']
        
        # Generate onboarding guide
        logger.info(f"Generating onboarding guide for role: {role}...")
        onboarding_gen = OnboardingGenerator(repo_path)
        onboarding_guide = onboarding_gen.generate_guide(role)
        
        # Generate modernization plan
        logger.info("Generating modernization roadmap...")
        modernization_planner = ModernizationPlanner(repo_path)
        modernization_plan = modernization_planner.generate_roadmap()
        
        outputs = {
            'onboarding_guide': onboarding_guide,
            'modernization_plan': modernization_plan,
            'role': role,
            'guide_length': len(onboarding_guide),
            'plan_length': len(modernization_plan)
        }
        
        _log_stage('stage_5_generate_reports', inputs, {
            'role': role,
            'guide_length': len(onboarding_guide),
            'plan_length': len(modernization_plan)
        })
        return outputs
        
    except Exception as e:
        logger.error(f"Stage 5 failed: {e}")
        raise


def run_full_pipeline(repo_url: str, role: str = 'fullstack') -> Dict[str, Any]:
    """
    Execute the complete DevScope analysis pipeline.
    
    Chains all 5 stages together to perform end-to-end codebase
    analysis and generate comprehensive reports.
    
    OpenAPI Schema:
        parameters:
          - name: repo_url
            in: body
            required: true
            schema:
              type: string
              description: Local path or GitHub URL to repository
          - name: role
            in: query
            required: false
            schema:
              type: string
              enum: [fullstack, frontend, backend, devops]
              default: fullstack
        responses:
          200:
            description: Full pipeline completed successfully
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [success, failed]
                stage_results:
                  type: object
                  description: Results from each stage
                onboarding_guide:
                  type: string
                modernization_plan:
                  type: string
    
    Args:
        repo_url: Local path or GitHub URL to repository
        role: Developer role for onboarding guide
        
    Returns:
        Dictionary containing:
        - status: 'success' or 'failed'
        - stage_results: Results from each stage
        - onboarding_guide: Final onboarding guide
        - modernization_plan: Final modernization roadmap
        - execution_time: Total execution time
    """
    start_time = datetime.utcnow()
    logger.info(f"Starting full pipeline for {repo_url} (role: {role})")
    
    try:
        # Stage 1: Scan
        logger.info("=== Stage 1/5: Scanning repository ===")
        file_manifest = stage_1_scan(repo_url)
        
        # Stage 2: Analyze
        logger.info("=== Stage 2/5: Analyzing structure ===")
        structural_data = stage_2_analyze(file_manifest)
        
        # Stage 3: Build Graph
        logger.info("=== Stage 3/5: Building knowledge graph ===")
        graph_summary = stage_3_build_graph(structural_data)
        
        # Stage 4: Enrich
        logger.info("=== Stage 4/5: Enriching with AI ===")
        semantic_data = stage_4_enrich(graph_summary)
        
        # Stage 5: Generate Reports
        logger.info("=== Stage 5/5: Generating reports ===")
        reports = stage_5_generate_reports(semantic_data, role)
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        result = {
            'status': 'success',
            'stage_results': {
                'stage_1': {'file_count': file_manifest['file_count']},
                'stage_2': {'health_score': structural_data['health_score']},
                'stage_3': {'nodes_created': graph_summary['nodes_created']},
                'stage_4': {'modules_enriched': semantic_data['modules_enriched']},
                'stage_5': {'role': role}
            },
            'onboarding_guide': reports['onboarding_guide'],
            'modernization_plan': reports['modernization_plan'],
            'execution_time': execution_time,
            'timestamp': end_time.isoformat()
        }
        
        logger.info(f"Pipeline completed successfully in {execution_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <repo_path> [role]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    role = sys.argv[2] if len(sys.argv) > 2 else 'fullstack'
    
    print(f"\n🚀 Running DevScope Pipeline")
    print(f"Repository: {repo_path}")
    print(f"Role: {role}\n")
    
    result = run_full_pipeline(repo_path, role)
    
    if result['status'] == 'success':
        print(f"\n✅ Pipeline completed in {result['execution_time']:.2f}s")
        print(f"\nOnboarding guide: {result['stage_results']['stage_5']['role']}")
        print(f"Health score: {result['stage_results']['stage_2']['health_score']}/100")
    else:
        print(f"\n❌ Pipeline failed: {result['error']}")

# Made with Bob
