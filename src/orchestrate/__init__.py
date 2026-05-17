"""
Orchestrate module for DevScope.

This module provides pipeline orchestration for watsonx Orchestrate integration.
"""

from .pipeline import (
    stage_1_scan,
    stage_2_analyze,
    stage_3_build_graph,
    stage_4_enrich,
    stage_5_generate_reports,
    run_full_pipeline
)

__all__ = [
    'stage_1_scan',
    'stage_2_analyze',
    'stage_3_build_graph',
    'stage_4_enrich',
    'stage_5_generate_reports',
    'run_full_pipeline'
]

# Made with Bob
