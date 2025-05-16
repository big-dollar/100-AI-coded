import sqlite3
import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.create_tables()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_tables(self):
        """创建数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_at TEXT
            )
            ''')
            conn.commit()
    
    def _convert_row_to_dict(self, row):
        """将数据库行转换为字典"""
        if not row:
            return None
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "due_date": row[3],
            "created_at": row[4],
            "completed": bool(row[5]),
            "completed_at": row[6] if len(row) > 6 else None
        }
    
    def add_todo(self, title, description, due_date):
        """添加新的待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO todos (title, description, due_date, created_at) VALUES (?, ?, ?, ?)",
                (title, description, due_date, created_at)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_all_todos(self, completed=None, order_by="due_date"):
        """获取所有待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM todos"
            params = []
            if completed is not None:
                sql += " WHERE completed=?"
                params.append(1 if completed else 0)
            if order_by not in ("due_date", "title", "created_at"):
                order_by = "due_date"
            sql += f" ORDER BY {order_by} ASC"
            cursor.execute(sql, params)
            return [self._convert_row_to_dict(row) for row in cursor.fetchall()]
    
    def search_todos(self, keyword, order_by="due_date"):
        """搜索待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if order_by not in ("due_date", "title", "created_at"):
                order_by = "due_date"
            sql = f"SELECT * FROM todos WHERE (title LIKE ? OR description LIKE ?) ORDER BY {order_by} ASC"
            params = [f"%{keyword}%", f"%{keyword}%"]
            cursor.execute(sql, params)
            return [self._convert_row_to_dict(row) for row in cursor.fetchall()]
    
    def find_todo(self, title, description, due_date):
        """查找特定待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM todos WHERE title=? AND description=? AND due_date=?",
                (title, description, due_date)
            )
            return self._convert_row_to_dict(cursor.fetchone())
    
    def get_todo_by_id(self, todo_id):
        """根据ID获取待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
            return self._convert_row_to_dict(cursor.fetchone())
    
    def update_todo(self, todo_id, title, description, due_date):
        """更新待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE todos SET title = ?, description = ?, due_date = ? WHERE id = ?",
                (title, description, due_date, todo_id)
            )
            conn.commit()
    
    def mark_completed(self, todo_id, completed=True):
        """标记待办事项为已完成"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            completed_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if completed else None
            cursor.execute(
                "UPDATE todos SET completed = ?, completed_at = ? WHERE id = ?",
                (1 if completed else 0, completed_at, todo_id)
            )
            conn.commit()
    
    def delete_todo(self, todo_id):
        """删除待办事项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
            conn.commit()