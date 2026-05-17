"""
Generators module for DevScope.

This module provides output generation capabilities:
- Onboarding guide generation
- Modernization plan generation
"""

from .onboarding_generator import OnboardingGenerator
from .modernization_planner import ModernizationPlanner
from .doc_generator import DocGenerator

__all__ = ['OnboardingGenerator', 'ModernizationPlanner', 'DocGenerator']

# Made with Bob
