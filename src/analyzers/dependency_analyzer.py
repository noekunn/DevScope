"""
Dependency Analyzer for DevScope.

Analyzes code dependencies across Python and JavaScript/TypeScript files:
- Import statements (import X, from X import Y, require, ES6 imports)
- Function calls between files
- Returns structured edge data for graph construction
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """
    Analyzes dependencies in a codebase by detecting imports and function calls.
    
    Supports:
    - Python files (.py): AST-based import and call detection
    - JavaScript/TypeScript files (.js, .ts, .jsx, .tsx): Regex-based detection
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the dependency analyzer.
        
        Args:
            repo_path: Path to the repository root directory
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        self.import_edges: List[Dict] = []
        self.call_edges: List[Dict] = []
        self.file_functions: Dict[str, Set[str]] = {}  # file -> set of function names
        
    def analyze(self) -> Dict[str, List[Dict]]:
        """
        Analyze all supported files in the repository.
        
        Returns:
            Dictionary with 'imports' and 'calls' keys containing edge lists
        """
        logger.info(f"Starting dependency analysis for: {self.repo_path}")
        
        # Scan all files
        for file_path in self._get_source_files():
            try:
                if file_path.suffix == '.py':
                    self._analyze_python_file(file_path)
                elif file_path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                    self._analyze_js_file(file_path)
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
                continue
        
        logger.info(f"Analysis complete. Found {len(self.import_edges)} imports, "
                   f"{len(self.call_edges)} function calls")
        
        return {
            'imports': self.import_edges,
            'calls': self.call_edges
        }
    
    def _get_source_files(self) -> List[Path]:
        """Get all Python and JS/TS files in the repository."""
        extensions = {'.py', '.js', '.ts', '.jsx', '.tsx'}
        files = []
        
        for ext in extensions:
            files.extend(self.repo_path.rglob(f'*{ext}'))
        
        # Filter out common directories to ignore
        ignore_dirs = {'node_modules', '__pycache__', '.git', 'venv', 'env', 'dist', 'build'}
        files = [f for f in files if not any(ignore in f.parts for ignore in ignore_dirs)]
        
        return files
    
    def _analyze_python_file(self, file_path: Path):
        """
        Analyze a Python file using AST parsing.
        
        Detects:
        - Import statements (import X, from X import Y)
        - Function definitions
        - Function calls
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            relative_path = str(file_path.relative_to(self.repo_path))
            
            # Track functions defined in this file
            self.file_functions[relative_path] = set()
            
            for node in ast.walk(tree):
                # Detect imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._add_import_edge(
                            source=relative_path,
                            target=alias.name,
                            import_type='import'
                        )
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._add_import_edge(
                            source=relative_path,
                            target=node.module,
                            import_type='from_import',
                            imported_names=[alias.name for alias in node.names]
                        )
                
                # Track function definitions
                elif isinstance(node, ast.FunctionDef):
                    self.file_functions[relative_path].add(node.name)
                
                # Detect function calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # Simple function call: func()
                        self._add_call_edge(
                            source_file=relative_path,
                            target_function=node.func.id
                        )
                    elif isinstance(node.func, ast.Attribute):
                        # Method call: obj.method()
                        if isinstance(node.func.value, ast.Name):
                            self._add_call_edge(
                                source_file=relative_path,
                                target_function=f"{node.func.value.id}.{node.func.attr}"
                            )
        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error parsing Python file {file_path}: {e}")
    
    def _analyze_js_file(self, file_path: Path):
        """
        Analyze a JavaScript/TypeScript file using regex patterns.
        
        Detects:
        - ES6 imports (import X from 'Y')
        - CommonJS requires (const X = require('Y'))
        - Function definitions
        - Function calls
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = str(file_path.relative_to(self.repo_path))
            self.file_functions[relative_path] = set()
            
            # Detect ES6 imports: import X from 'module'
            es6_imports = re.finditer(
                r"import\s+(?:{[^}]+}|\*\s+as\s+\w+|\w+)\s+from\s+['\"]([^'\"]+)['\"]",
                content
            )
            for match in es6_imports:
                module = match.group(1)
                self._add_import_edge(
                    source=relative_path,
                    target=module,
                    import_type='es6_import'
                )
            
            # Detect CommonJS requires: require('module')
            require_imports = re.finditer(
                r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
                content
            )
            for match in require_imports:
                module = match.group(1)
                self._add_import_edge(
                    source=relative_path,
                    target=module,
                    import_type='require'
                )
            
            # Detect function definitions
            # function name() or const name = () =>
            func_defs = re.finditer(
                r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)",
                content
            )
            for match in func_defs:
                func_name = match.group(1) or match.group(2)
                if func_name:
                    self.file_functions[relative_path].add(func_name)
            
            # Detect function calls: functionName(
            func_calls = re.finditer(r"(\w+)\s*\(", content)
            for match in func_calls:
                func_name = match.group(1)
                # Filter out keywords and common built-ins
                if func_name not in {'if', 'for', 'while', 'switch', 'catch', 'function'}:
                    self._add_call_edge(
                        source_file=relative_path,
                        target_function=func_name
                    )
        
        except Exception as e:
            logger.error(f"Error parsing JS/TS file {file_path}: {e}")
    
    def _add_import_edge(self, source: str, target: str, import_type: str,
                        imported_names: Optional[List[str]] = None):
        """Add an import edge to the list."""
        edge: Dict[str, Any] = {
            'source': source,
            'target': target,
            'type': 'IMPORTS',
            'import_type': import_type
        }
        if imported_names:
            edge['imported_names'] = imported_names
        
        self.import_edges.append(edge)
    
    def _add_call_edge(self, source_file: str, target_function: str):
        """Add a function call edge to the list."""
        # Try to resolve which file contains the target function
        target_file = self._resolve_function_file(target_function)
        
        edge = {
            'source_file': source_file,
            'target_function': target_function,
            'type': 'CALLS'
        }
        
        if target_file:
            edge['target_file'] = target_file
        
        self.call_edges.append(edge)
    
    def _resolve_function_file(self, function_name: str) -> Optional[str]:
        """
        Try to resolve which file contains a function.
        
        This is a simple heuristic - in a real implementation, you'd need
        more sophisticated import resolution.
        """
        # Remove method calls (obj.method -> method)
        if '.' in function_name:
            function_name = function_name.split('.')[-1]
        
        for file_path, functions in self.file_functions.items():
            if function_name in functions:
                return file_path
        
        return None
    
    def get_import_edges(self) -> List[Dict]:
        """Get all import edges."""
        return self.import_edges
    
    def get_call_edges(self) -> List[Dict]:
        """Get all function call edges."""
        return self.call_edges
    
    def get_all_edges(self) -> List[Dict]:
        """Get all edges (imports + calls)."""
        return self.import_edges + self.call_edges


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dependency_analyzer.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    analyzer = DependencyAnalyzer(repo_path)
    results = analyzer.analyze()
    
    print(f"\n=== Import Edges ({len(results['imports'])}) ===")
    for edge in results['imports'][:10]:  # Show first 10
        print(f"  {edge['source']} -> {edge['target']} ({edge['import_type']})")
    
    print(f"\n=== Call Edges ({len(results['calls'])}) ===")
    for edge in results['calls'][:10]:  # Show first 10
        target_file = edge.get('target_file', 'unknown')
        print(f"  {edge['source_file']} -> {edge['target_function']} (in {target_file})")

# Made with Bob
