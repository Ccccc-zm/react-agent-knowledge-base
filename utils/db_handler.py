import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path(__file__).parent.parent / "chat_history.db"

def init_db():
    """初始化数据库表"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT UNIQUE NOT NULL,
                title TEXT DEFAULT '新对话',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(thread_id) REFERENCES conversations(thread_id)
            )
        """)

def create_conversation(thread_id: str, title: str = "新对话") -> None:
    """创建新会话"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO conversations (thread_id, title) VALUES (?, ?)",
            (thread_id, title)
        )

def save_message(thread_id: str, role: str, content: str) -> None:
    """保存单条消息"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
            (thread_id, role, content)
        )
        conn.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?",
            (thread_id,)
        )

def get_all_conversations() -> List[Dict]:
    """获取所有会话列表（按更新时间倒序）"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT thread_id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC"
        )
        return [dict(row) for row in cur.fetchall()]

def get_messages_by_thread(thread_id: str) -> List[Dict]:
    """获取指定会话的所有消息"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT role, content FROM messages WHERE thread_id = ? ORDER BY timestamp ASC",
            (thread_id,)
        )
        return [dict(row) for row in cur.fetchall()]

def delete_conversation(thread_id: str) -> None:
    """删除会话及其所有消息"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
        conn.execute("DELETE FROM conversations WHERE thread_id = ?", (thread_id,))

def update_conversation_title(thread_id: str, title: str) -> None:
    """更新会话标题"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE conversations SET title = ? WHERE thread_id = ?",
            (title, thread_id)
        )