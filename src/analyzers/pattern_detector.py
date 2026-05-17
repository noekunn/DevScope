"""
Pattern Detector — Design Pattern Recognition Module.

Detects common software design patterns in Python/JavaScript codebases:
- Singleton Pattern
- Factory Pattern
- Observer/Pub-Sub Pattern
- Repository/DAO Pattern
- Strategy Pattern
- Decorator Pattern
- MVC/MVP Architecture
"""

import ast
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class PatternDetector:
    """Detects design patterns in source code using AST analysis and heuristics."""
    
    # Pattern signatures for detection
    PATTERN_SIGNATURES = {
        'Singleton': {
            'indicators': ['_instance', '__new__', 'get_instance', 'getInstance'],
            'description': 'Ensures a class has only one instance with global access point'
        },
        'Factory': {
            'indicators': ['create_', 'factory', 'build_', 'make_', 'Factory'],
            'description': 'Creates objects without exposing instantiation logic'
        },
        'Observer': {
            'indicators': ['subscribe', 'unsubscribe', 'notify', 'on_', 'emit', 'listener', 'callback'],
            'description': 'Defines one-to-many dependency between objects'
        },
        'Repository': {
            'indicators': ['repository', 'repo', 'dao', 'data_access', 'get_all', 'find_by', 'save', 'delete'],
            'description': 'Mediates between domain and data mapping layers'
        },
        'Strategy': {
            'indicators': ['strategy', 'algorithm', 'policy', 'set_strategy', 'execute'],
            'description': 'Defines a family of interchangeable algorithms'
        },
        'Decorator': {
            'indicators': ['wrapper', 'decorator', 'wrap', '@wraps', 'functools.wraps'],
            'description': 'Attaches additional responsibilities to objects dynamically'
        },
        'Builder': {
            'indicators': ['builder', 'build', 'with_', 'set_', 'Builder'],
            'description': 'Separates construction of complex objects from representation'
        },
        'MVC': {
            'indicators': ['controller', 'view', 'model', 'template', 'route', 'handler'],
            'description': 'Separates application into Model, View, and Controller'
        }
    }
    
    def __init__(self, repo_path: str):
        """Initialize with repository path."""
        self.repo_path = repo_path
        self.detected_patterns: List[Dict[str, Any]] = []
    
    def detect_patterns(self) -> List[Dict[str, Any]]:
        """
        Scan the repository and detect design patterns.
        
        Returns:
            List of detected patterns with file locations and confidence scores.
        """
        self.detected_patterns = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden dirs and common non-source dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                      ('node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build')]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    self._analyze_python_file(filepath)
                elif file.endswith(('.js', '.ts')):
                    filepath = os.path.join(root, file)
                    self._analyze_js_file(filepath)
        
        return self.detected_patterns
    
    def _analyze_python_file(self, filepath: str):
        """Analyze a Python file for design patterns."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            
            tree = ast.parse(source)
            rel_path = os.path.relpath(filepath, self.repo_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._check_class_patterns(node, rel_path, source)
                elif isinstance(node, ast.FunctionDef):
                    self._check_function_patterns(node, rel_path, source)
            
            # Check file-level patterns
            self._check_file_patterns(rel_path, source)
            
        except (SyntaxError, UnicodeDecodeError, OSError):
            pass
    
    def _analyze_js_file(self, filepath: str):
        """Analyze a JavaScript/TypeScript file for patterns using regex."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            
            rel_path = os.path.relpath(filepath, self.repo_path)
            source_lower = source.lower()
            
            for pattern_name, signature in self.PATTERN_SIGNATURES.items():
                matches = sum(1 for ind in signature['indicators'] if ind.lower() in source_lower)
                if matches >= 2:
                    confidence = min(matches / len(signature['indicators']), 1.0)
                    self.detected_patterns.append({
                        'pattern': pattern_name,
                        'file': rel_path,
                        'confidence': round(confidence, 2),
                        'description': signature['description'],
                        'evidence': [ind for ind in signature['indicators'] if ind.lower() in source_lower]
                    })
        except (UnicodeDecodeError, OSError):
            pass
    
    def _check_class_patterns(self, node: ast.ClassDef, filepath: str, source: str):
        """Check a class definition for design patterns."""
        class_source = ast.get_source_segment(source, node) or ''
        class_lower = class_source.lower()
        class_name = node.name.lower()
        
        # Singleton detection
        method_names = [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if '__new__' in method_names or 'get_instance' in method_names or '_instance' in class_source:
            self.detected_patterns.append({
                'pattern': 'Singleton',
                'file': filepath,
                'class': node.name,
                'confidence': 0.9,
                'description': self.PATTERN_SIGNATURES['Singleton']['description'],
                'evidence': ['__new__' if '__new__' in method_names else '_instance']
            })
        
        # Factory detection
        if 'factory' in class_name or any('create' in m.lower() for m in method_names):
            self.detected_patterns.append({
                'pattern': 'Factory',
                'file': filepath,
                'class': node.name,
                'confidence': 0.7,
                'description': self.PATTERN_SIGNATURES['Factory']['description'],
                'evidence': [m for m in method_names if 'create' in m.lower()]
            })
        
        # Observer detection
        observer_methods = [m for m in method_names if any(ind in m.lower() for ind in ['subscribe', 'notify', 'emit', 'on_'])]
        if len(observer_methods) >= 2:
            self.detected_patterns.append({
                'pattern': 'Observer',
                'file': filepath,
                'class': node.name,
                'confidence': 0.8,
                'description': self.PATTERN_SIGNATURES['Observer']['description'],
                'evidence': observer_methods
            })
        
        # Builder detection
        builder_methods = [m for m in method_names if m.startswith('with_') or m.startswith('set_')]
        if len(builder_methods) >= 2 and 'build' in method_names:
            self.detected_patterns.append({
                'pattern': 'Builder',
                'file': filepath,
                'class': node.name,
                'confidence': 0.85,
                'description': self.PATTERN_SIGNATURES['Builder']['description'],
                'evidence': builder_methods + ['build']
            })
    
    def _check_function_patterns(self, node: ast.FunctionDef, filepath: str, source: str):
        """Check a function for decorator pattern usage."""
        if node.decorator_list:
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id in ('wraps', 'decorator'):
                    self.detected_patterns.append({
                        'pattern': 'Decorator',
                        'file': filepath,
                        'function': node.name,
                        'confidence': 0.9,
                        'description': self.PATTERN_SIGNATURES['Decorator']['description'],
                        'evidence': [f'@{decorator.id}']
                    })
    
    def _check_file_patterns(self, filepath: str, source: str):
        """Check file-level patterns based on naming and imports."""
        filename = os.path.basename(filepath).lower()
        source_lower = source.lower()
        
        # MVC pattern detection
        if any(term in filename for term in ['controller', 'view', 'model', 'route', 'handler']):
            self.detected_patterns.append({
                'pattern': 'MVC',
                'file': filepath,
                'confidence': 0.6,
                'description': self.PATTERN_SIGNATURES['MVC']['description'],
                'evidence': [filename]
            })
        
        # Repository pattern
        if 'repository' in filename or 'dao' in filename:
            self.detected_patterns.append({
                'pattern': 'Repository',
                'file': filepath,
                'confidence': 0.8,
                'description': self.PATTERN_SIGNATURES['Repository']['description'],
                'evidence': [filename]
            })
        
        # Strategy pattern
        if 'strategy' in filename or 'policy' in filename:
            self.detected_patterns.append({
                'pattern': 'Strategy',
                'file': filepath,
                'confidence': 0.7,
                'description': self.PATTERN_SIGNATURES['Strategy']['description'],
                'evidence': [filename]
            })
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of detected patterns.
        
        Returns:
            Dictionary with pattern counts, files affected, and details.
        """
        if not self.detected_patterns:
            self.detect_patterns()
        
        pattern_counts = {}
        for p in self.detected_patterns:
            name = p['pattern']
            pattern_counts[name] = pattern_counts.get(name, 0) + 1
        
        return {
            'total_patterns': len(self.detected_patterns),
            'unique_patterns': len(pattern_counts),
            'pattern_counts': pattern_counts,
            'patterns': self.detected_patterns,
            'files_with_patterns': len(set(p['file'] for p in self.detected_patterns))
        }


# Made with Bob
