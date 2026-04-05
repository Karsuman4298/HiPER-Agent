import os
import subprocess
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
import pandas as pd
from config.settings import settings

class ToolLayer:
    def __init__(self):
        pass

    def web_search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search the web using DuckDuckGo."""
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({"title": r['title'], "link": r['href'], "snippet": r['body']})
        return results

    def file_read(self, file_path: str) -> str:
        """Read content from a file."""
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def file_write(self, file_path: str, content: str) -> str:
        """Write content to a file."""
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"

    def python_code_execution(self, code: str) -> Dict[str, Any]:
        """Execute Python code safely in a subprocess."""
        # Note: In production, use a more sandboxed environment.
        temp_file = "tmp_execution.py"
        self.file_write(temp_file, code)
        try:
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out"}
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def dataset_loader(self, file_path: str) -> str:
        """Load and summarize a dataset."""
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist."
        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
            summary = {
                "columns": list(df.columns),
                "shape": df.shape,
                "head": df.head(5).to_dict()
            }
            return str(summary)
        except Exception as e:
            return f"Error loading dataset: {str(e)}"

# Singleton tool instance
    def query_memory(self, query: str) -> str:
        """Search the experience database for past tasks."""
        from memory.database import ExperienceDatabase
        db = ExperienceDatabase()
        results = db.get_recent_experiences(limit=5)
        if not results:
            return "No past experiences found in memory."
        
        summary = "Recent Tasks found in memory:\n"
        for r in results:
            summary += f"- {r['query']}: {r['result'][:200]}...\n"
        return summary

tools = ToolLayer()
