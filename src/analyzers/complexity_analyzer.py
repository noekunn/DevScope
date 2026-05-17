"""
Complexity Analyzer for DevScope.

Analyzes code complexity using the radon library:
- Cyclomatic complexity per function/method
- Lines of code per file
- Complexity hotspot detection
- Overall codebase health score
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from radon.complexity import cc_visit, cc_rank
from radon.raw import analyze

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplexityAnalyzer:
    """
    Analyzes code complexity metrics for a codebase.
    
    Uses radon library to compute:
    - Cyclomatic complexity (McCabe complexity)
    - Lines of code (LOC)
    - Complexity hotspots (functions with high complexity)
    - Overall health score
    """
    
    # Complexity thresholds
    HOTSPOT_THRESHOLD = 10  # Functions with complexity > 10 are hotspots
    EXCELLENT_THRESHOLD = 5
    GOOD_THRESHOLD = 10
    MODERATE_THRESHOLD = 20
    
    def __init__(self, repo_path: str):
        """
        Initialize the complexity analyzer.
        
        Args:
            repo_path: Path to the repository root directory
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        self.file_metrics: List[Dict[str, Any]] = []
        self.total_functions = 0
        self.total_complexity = 0
        self.hotspot_count = 0
        
    def analyze(self) -> List[Dict[str, Any]]:
        """
        Analyze all Python files in the repository.
        
        Returns:
            List of file metrics with complexity data
        """
        logger.info(f"Starting complexity analysis for: {self.repo_path}")
        
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                metrics = self._analyze_file(file_path)
                if metrics:
                    self.file_metrics.append(metrics)
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
                continue
        
        logger.info(f"Analysis complete. Analyzed {len(self.file_metrics)} files, "
                   f"found {self.hotspot_count} complexity hotspots")
        
        return self.file_metrics
    
    def _get_python_files(self) -> List[Path]:
        """Get all Python files in the repository."""
        files = list(self.repo_path.rglob('*.py'))
        
        # Filter out common directories to ignore
        ignore_dirs = {'__pycache__', '.git', 'venv', 'env', 'dist', 'build', '.tox'}
        files = [f for f in files if not any(ignore in f.parts for ignore in ignore_dirs)]
        
        return files
    
    def _analyze_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a single Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with file metrics or None if analysis fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            relative_path = str(file_path.relative_to(self.repo_path))
            
            # Get raw metrics (lines of code)
            raw_metrics = analyze(content)
            
            # Get complexity metrics for functions
            complexity_results = cc_visit(content)
            
            functions = []
            file_total_complexity = 0
            
            for result in complexity_results:
                complexity = result.complexity
                is_hotspot = complexity > self.HOTSPOT_THRESHOLD
                
                function_data = {
                    'name': result.name,
                    'complexity': complexity,
                    'lines': result.endline - result.lineno + 1,
                    'is_hotspot': is_hotspot,
                    'rank': cc_rank(complexity),
                    'lineno': result.lineno,
                    'col_offset': result.col_offset
                }
                
                functions.append(function_data)
                file_total_complexity += complexity
                self.total_complexity += complexity
                self.total_functions += 1
                
                if is_hotspot:
                    self.hotspot_count += 1
            
            # Calculate average complexity for this file
            avg_complexity = (file_total_complexity / len(functions)) if functions else 0
            
            file_metrics = {
                'file': relative_path,
                'functions': functions,
                'total_lines': raw_metrics.loc,  # Lines of code
                'source_lines': raw_metrics.sloc,  # Source lines (excluding comments/blanks)
                'comment_lines': raw_metrics.comments,
                'blank_lines': raw_metrics.blank,
                'avg_complexity': round(avg_complexity, 2),
                'max_complexity': max([f['complexity'] for f in functions]) if functions else 0,
                'function_count': len(functions),
                'hotspot_count': sum(1 for f in functions if f['is_hotspot'])
            }
            
            return file_metrics
            
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None
    
    def get_hotspots(self) -> List[Dict[str, Any]]:
        """
        Get all complexity hotspots across the codebase.
        
        Returns:
            List of hotspot functions with their file locations
        """
        hotspots = []
        
        for file_metrics in self.file_metrics:
            for func in file_metrics['functions']:
                if func['is_hotspot']:
                    hotspots.append({
                        'file': file_metrics['file'],
                        'function': func['name'],
                        'complexity': func['complexity'],
                        'lines': func['lines'],
                        'rank': func['rank'],
                        'lineno': func['lineno']
                    })
        
        # Sort by complexity (highest first)
        hotspots.sort(key=lambda x: x['complexity'], reverse=True)
        
        return hotspots
    
    def get_file_rankings(self) -> List[Dict[str, Any]]:
        """
        Get files ranked by average complexity.
        
        Returns:
            List of files sorted by average complexity (highest first)
        """
        rankings = [
            {
                'file': fm['file'],
                'avg_complexity': fm['avg_complexity'],
                'max_complexity': fm['max_complexity'],
                'function_count': fm['function_count'],
                'hotspot_count': fm['hotspot_count'],
                'total_lines': fm['total_lines']
            }
            for fm in self.file_metrics
        ]
        
        rankings.sort(key=lambda x: x['avg_complexity'], reverse=True)
        
        return rankings
    
    def health_score(self) -> int:
        """
        Calculate overall codebase health score (0-100).
        
        Score is based on:
        - Average complexity across all functions
        - Percentage of hotspot functions
        - Distribution of complexity ranks
        
        Returns:
            Health score from 0 (poor) to 100 (excellent)
        """
        if self.total_functions == 0:
            return 100  # No code = perfect score
        
        # Calculate average complexity
        avg_complexity = self.total_complexity / self.total_functions
        
        # Calculate hotspot percentage
        hotspot_percentage = (self.hotspot_count / self.total_functions) * 100
        
        # Score based on average complexity (0-50 points)
        if avg_complexity <= self.EXCELLENT_THRESHOLD:
            complexity_score = 50
        elif avg_complexity <= self.GOOD_THRESHOLD:
            complexity_score = 40
        elif avg_complexity <= self.MODERATE_THRESHOLD:
            complexity_score = 25
        else:
            complexity_score = max(0, 50 - (avg_complexity - self.MODERATE_THRESHOLD) * 2)
        
        # Score based on hotspot percentage (0-50 points)
        if hotspot_percentage == 0:
            hotspot_score = 50
        elif hotspot_percentage <= 5:
            hotspot_score = 40
        elif hotspot_percentage <= 10:
            hotspot_score = 30
        elif hotspot_percentage <= 20:
            hotspot_score = 20
        else:
            hotspot_score = max(0, 50 - hotspot_percentage * 2)
        
        total_score = int(complexity_score + hotspot_score)
        
        return min(100, max(0, total_score))
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the complexity analysis.
        
        Returns:
            Dictionary with summary statistics
        """
        if self.total_functions == 0:
            avg_complexity = 0
            hotspot_percentage = 0
        else:
            avg_complexity = self.total_complexity / self.total_functions
            hotspot_percentage = (self.hotspot_count / self.total_functions) * 100
        
        total_lines = sum(fm['total_lines'] for fm in self.file_metrics)
        total_source_lines = sum(fm['source_lines'] for fm in self.file_metrics)
        
        return {
            'total_files': len(self.file_metrics),
            'total_functions': self.total_functions,
            'total_lines': total_lines,
            'total_source_lines': total_source_lines,
            'avg_complexity': round(avg_complexity, 2),
            'hotspot_count': self.hotspot_count,
            'hotspot_percentage': round(hotspot_percentage, 2),
            'health_score': self.health_score(),
            'health_rating': self._get_health_rating(self.health_score())
        }
    
    def _get_health_rating(self, score: int) -> str:
        """Convert health score to a rating."""
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 50:
            return 'Fair'
        elif score >= 25:
            return 'Poor'
        else:
            return 'Critical'


# Example usage
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python complexity_analyzer.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    analyzer = ComplexityAnalyzer(repo_path)
    results = analyzer.analyze()
    
    # Print summary
    summary = analyzer.get_summary()
    print("\n=== Complexity Analysis Summary ===")
    print(json.dumps(summary, indent=2))
    
    # Print top hotspots
    hotspots = analyzer.get_hotspots()
    print(f"\n=== Top 10 Complexity Hotspots ===")
    for i, hotspot in enumerate(hotspots[:10], 1):
        print(f"{i}. {hotspot['file']}:{hotspot['function']} "
              f"(complexity: {hotspot['complexity']}, rank: {hotspot['rank']})")
    
    # Print most complex files
    rankings = analyzer.get_file_rankings()
    print(f"\n=== Top 10 Most Complex Files ===")
    for i, file_rank in enumerate(rankings[:10], 1):
        print(f"{i}. {file_rank['file']} "
              f"(avg: {file_rank['avg_complexity']}, max: {file_rank['max_complexity']}, "
              f"hotspots: {file_rank['hotspot_count']})")

# Made with Bob
