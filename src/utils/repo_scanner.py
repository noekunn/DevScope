"""
Repository Scanner — Git cloning and file traversal utilities.
"""
import os
import shutil
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path


class RepoScanner:
    """Scans repositories (local or remote) for source files."""
    
    SUPPORTED_EXTENSIONS = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'JavaScript', '.tsx': 'TypeScript', '.java': 'Java',
        '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
        '.cs': 'C#', '.cpp': 'C++', '.c': 'C', '.swift': 'Swift',
    }
    
    SKIP_DIRS = {
        'node_modules', '__pycache__', '.git', '.venv', 'venv',
        'dist', 'build', '.next', '.nuxt', 'vendor', '.tox',
        'env', '.env', 'eggs', '.eggs', 'target',
    }
    
    def __init__(self, path: str):
        self.path = path
        self.is_remote = path.startswith('http') or path.startswith('git@')
        self.local_path = None
        self._temp_dir = None
    
    def prepare(self) -> str:
        """Clone remote repo or validate local path. Returns local path."""
        if self.is_remote:
            return self._clone_repo()
        
        if os.path.isdir(self.path):
            self.local_path = self.path
            return self.path
        
        raise FileNotFoundError(f"Repository not found: {self.path}")
    
    def _clone_repo(self) -> str:
        """Clone a remote git repository to a temp directory."""
        try:
            import git
        except ImportError:
            raise ImportError("GitPython is required: pip install gitpython")
        
        self._temp_dir = tempfile.mkdtemp(prefix='devscope_')
        git.Repo.clone_from(self.path, self._temp_dir, depth=1)
        self.local_path = self._temp_dir
        return self._temp_dir
    
    def scan_files(self) -> List[Dict[str, Any]]:
        """Scan the repository and return metadata for all source files."""
        if not self.local_path:
            self.prepare()
        
        files = []
        for root, dirs, filenames in os.walk(self.local_path):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS and not d.startswith('.')]
            
            for filename in filenames:
                ext = Path(filename).suffix.lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, self.local_path)
                    
                    try:
                        size = os.path.getsize(filepath)
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = sum(1 for _ in f)
                    except OSError:
                        size = 0
                        lines = 0
                    
                    files.append({
                        'path': rel_path,
                        'absolute_path': filepath,
                        'language': self.SUPPORTED_EXTENSIONS[ext],
                        'extension': ext,
                        'size_bytes': size,
                        'lines': lines,
                    })
        
        return files
    
    def cleanup(self):
        """Remove temporary cloned repository."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
    
    def __del__(self):
        self.cleanup()

# Made with Bob
