"""
AutoPromptix Storage Manager

Handles local storage of knowledge, chat history, and prompt improvement history.
"""

import json
import os
import pickle
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

class StorageManager:
    """Manages local storage for AutoPromptix"""
    
    def __init__(self, storage_dir: str = "autopromptix_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.knowledge_dir = self.storage_dir / "knowledge"
        self.chat_dir = self.storage_dir / "chat_history"
        self.improvement_dir = self.storage_dir / "improvements"
        
        for dir_path in [self.knowledge_dir, self.chat_dir, self.improvement_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize SQLite database for structured data
        self.db_path = self.storage_dir / "autopromptix.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                args TEXT,
                kwargs TEXT,
                result TEXT,
                execution_time REAL,
                success BOOLEAN
            )
        """)
        
        # Prompt improvements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_id TEXT NOT NULL,
                original_prompt TEXT,
                improved_prompt TEXT,
                improvement_reason TEXT,
                performance_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Test results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_id TEXT NOT NULL,
                test_name TEXT,
                prompt_version TEXT,
                expected_output TEXT,
                actual_output TEXT,
                score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                test_config TEXT
            )
        """)
        
        # Knowledge base table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_id TEXT NOT NULL,
                knowledge_type TEXT,
                content TEXT,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_execution(self, function_id: str, args: tuple, kwargs: dict, result: Any, execution_time: float = None, success: bool = True):
        """Log function execution to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO test_executions (function_id, args, kwargs, result, execution_time, success)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            function_id,
            json.dumps(args, default=str),
            json.dumps(kwargs, default=str),
            json.dumps(result, default=str),
            execution_time,
            success
        ))
        
        conn.commit()
        conn.close()
    
    def save_prompt_improvement(self, function_id: str, original_prompt: str, improved_prompt: str, 
                               improvement_reason: str, performance_score: float):
        """Save a prompt improvement to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO prompt_improvements (function_id, original_prompt, improved_prompt, improvement_reason, performance_score)
            VALUES (?, ?, ?, ?, ?)
        """, (function_id, original_prompt, improved_prompt, improvement_reason, performance_score))
        
        conn.commit()
        conn.close()
    
    def save_test_result(self, function_id: str, test_name: str, prompt_version: str, 
                        expected_output: str, actual_output: str, score: float, test_config: Dict[str, Any]):
        """Save test result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO test_results (function_id, test_name, prompt_version, expected_output, actual_output, score, test_config)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (function_id, test_name, prompt_version, expected_output, actual_output, score, json.dumps(test_config)))
        
        conn.commit()
        conn.close()
    
    def save_knowledge(self, function_id: str, knowledge_type: str, content: str, metadata: Dict[str, Any] = None):
        """Save knowledge to the knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO knowledge_base (function_id, knowledge_type, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (function_id, knowledge_type, content, json.dumps(metadata or {})))
        
        conn.commit()
        conn.close()
    
    def get_execution_history(self, function_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history for a function"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM test_executions 
            WHERE function_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (function_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]
    
    def get_prompt_improvements(self, function_id: str) -> List[Dict[str, Any]]:
        """Get prompt improvements for a function"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM prompt_improvements 
            WHERE function_id = ? 
            ORDER BY timestamp DESC
        """, (function_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]
    
    def get_test_results(self, function_id: str) -> List[Dict[str, Any]]:
        """Get test results for a function"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM test_results 
            WHERE function_id = ? 
            ORDER BY timestamp DESC
        """, (function_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]
    
    def get_knowledge(self, function_id: str, knowledge_type: str = None) -> List[Dict[str, Any]]:
        """Get knowledge for a function"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if knowledge_type:
            cursor.execute("""
                SELECT * FROM knowledge_base 
                WHERE function_id = ? AND knowledge_type = ?
                ORDER BY timestamp DESC
            """, (function_id, knowledge_type))
        else:
            cursor.execute("""
                SELECT * FROM knowledge_base 
                WHERE function_id = ?
                ORDER BY timestamp DESC
            """, (function_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]
    
    def save_chat_history(self, session_id: str, messages: List[Dict[str, Any]]):
        """Save chat history to file"""
        chat_file = self.chat_dir / f"{session_id}.json"
        
        chat_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'messages': messages
        }
        
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)
    
    def load_chat_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load chat history from file"""
        chat_file = self.chat_dir / f"{session_id}.json"
        
        if chat_file.exists():
            with open(chat_file, 'r') as f:
                chat_data = json.load(f)
            return chat_data.get('messages', [])
        
        return None
    
    def save_improvement_history(self, function_id: str, improvements: List[Dict[str, Any]]):
        """Save improvement history to file"""
        improvement_file = self.improvement_dir / f"{function_id}.json"
        
        improvement_data = {
            'function_id': function_id,
            'timestamp': datetime.now().isoformat(),
            'improvements': improvements
        }
        
        with open(improvement_file, 'w') as f:
            json.dump(improvement_data, f, indent=2)
    
    def load_improvement_history(self, function_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load improvement history from file"""
        improvement_file = self.improvement_dir / f"{function_id}.json"
        
        if improvement_file.exists():
            with open(improvement_file, 'r') as f:
                improvement_data = json.load(f)
            return improvement_data.get('improvements', [])
        
        return []
    
    def get_all_functions(self) -> List[str]:
        """Get all function IDs in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT function_id FROM test_executions")
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    def get_function_stats(self, function_id: str) -> Dict[str, Any]:
        """Get statistics for a function"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get execution count
        cursor.execute("SELECT COUNT(*) FROM test_executions WHERE function_id = ?", (function_id,))
        execution_count = cursor.fetchone()[0]
        
        # Get improvement count
        cursor.execute("SELECT COUNT(*) FROM prompt_improvements WHERE function_id = ?", (function_id,))
        improvement_count = cursor.fetchone()[0]
        
        # Get test count
        cursor.execute("SELECT COUNT(*) FROM test_results WHERE function_id = ?", (function_id,))
        test_count = cursor.fetchone()[0]
        
        # Get average score
        cursor.execute("SELECT AVG(score) FROM test_results WHERE function_id = ?", (function_id,))
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'execution_count': execution_count,
            'improvement_count': improvement_count,
            'test_count': test_count,
            'avg_score': avg_score
        }
    
    def cleanup_old_data(self, days_old: int = 30):
        """Clean up old data from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().isoformat()
        
        # Delete old executions
        cursor.execute("""
            DELETE FROM test_executions 
            WHERE timestamp < datetime('now', '-{} days')
        """.format(days_old))
        
        # Delete old test results
        cursor.execute("""
            DELETE FROM test_results 
            WHERE timestamp < datetime('now', '-{} days')
        """.format(days_old))
        
        conn.commit()
        conn.close() 