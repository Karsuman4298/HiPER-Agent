import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config.settings import settings

class ExperienceDatabase:
    def __init__(self, db_path: str = settings.EXPERIENCE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Table for tasks and evaluations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_type TEXT,
                    query TEXT,
                    plan TEXT,
                    result TEXT,
                    evaluation_score FLOAT,
                    feedback TEXT,
                    strategy_used TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Table for strategy improvements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_role TEXT,
                    old_strategy TEXT,
                    new_strategy TEXT,
                    reasoning TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_experience(self, task_type: str, query: str, plan: Dict, result: str, score: float, feedback: str, strategy: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO experiences (task_type, query, plan, result, evaluation_score, feedback, strategy_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_type, query, json.dumps(plan), result, score, feedback, strategy))
            conn.commit()

    def get_recent_experiences(self, limit: int = 5) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM experiences ORDER BY timestamp DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def add_improvement(self, agent_role: str, old_strategy: str, new_strategy: str, reasoning: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO improvements (agent_role, old_strategy, new_strategy, reasoning)
                VALUES (?, ?, ?, ?)
            ''', (agent_role, old_strategy, new_strategy, reasoning))
            conn.commit()
