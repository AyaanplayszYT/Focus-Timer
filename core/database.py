"""
SQLite database module for task and session storage.
Handles all data persistence for the Dynamic Island Timer.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Task:
    id: Optional[int] = None
    name: str = ""
    completed: bool = False
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_focus_seconds: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FocusSession:
    id: Optional[int] = None
    task_id: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: int = 0
    session_type: str = "work"  # "work" or "break"
    completed: bool = False


@dataclass
class DailyStats:
    date: str
    total_focus_seconds: int = 0
    sessions_completed: int = 0
    tasks_completed: int = 0


@dataclass 
class DailyGoal:
    """Daily focus goal tracking."""
    date: str
    target_minutes: int = 120  # Default 2 hours
    achieved_minutes: int = 0
    
    @property
    def progress(self) -> float:
        """Get goal progress as 0.0 to 1.0"""
        if self.target_minutes <= 0:
            return 0.0
        return min(self.achieved_minutes / self.target_minutes, 1.0)
    
    @property
    def is_achieved(self) -> bool:
        return self.achieved_minutes >= self.target_minutes


class Database:
    """SQLite database handler for task timer data."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to user's app data directory
            app_data = os.getenv('APPDATA', os.path.expanduser('~'))
            db_dir = Path(app_data) / 'DynamicIslandTimer'
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / 'timer_data.db')
        
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                total_focus_seconds INTEGER DEFAULT 0
            )
        ''')
        
        # Focus sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                start_time TEXT DEFAULT CURRENT_TIMESTAMP,
                end_time TEXT,
                duration_seconds INTEGER DEFAULT 0,
                session_type TEXT DEFAULT 'work',
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')
        
        # Daily stats table for quick aggregation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_focus_seconds INTEGER DEFAULT 0,
                sessions_completed INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Daily goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_goals (
                date TEXT PRIMARY KEY,
                target_minutes INTEGER DEFAULT 120,
                achieved_minutes INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ============== Task Operations ==============
    
    def add_task(self, name: str) -> Task:
        """Add a new task and return it with ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO tasks (name, created_at) VALUES (?, ?)',
            (name, datetime.now().isoformat())
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return Task(
            id=task_id,
            name=name,
            completed=False,
            created_at=datetime.now().isoformat()
        )
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Task(
                id=row['id'],
                name=row['name'],
                completed=bool(row['completed']),
                created_at=row['created_at'],
                completed_at=row['completed_at'],
                total_focus_seconds=row['total_focus_seconds']
            )
        return None
    
    def get_all_tasks(self, include_completed: bool = True) -> List[Task]:
        """Get all tasks, optionally filtering out completed ones."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if include_completed:
            cursor.execute('SELECT * FROM tasks ORDER BY completed ASC, created_at DESC')
        else:
            cursor.execute('SELECT * FROM tasks WHERE completed = 0 ORDER BY created_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Task(
                id=row['id'],
                name=row['name'],
                completed=bool(row['completed']),
                created_at=row['created_at'],
                completed_at=row['completed_at'],
                total_focus_seconds=row['total_focus_seconds']
            )
            for row in rows
        ]
    
    def update_task(self, task: Task):
        """Update an existing task."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET name = ?, completed = ?, completed_at = ?, total_focus_seconds = ?
            WHERE id = ?
        ''', (task.name, int(task.completed), task.completed_at, 
              task.total_focus_seconds, task.id))
        
        conn.commit()
        conn.close()
    
    def complete_task(self, task_id: int):
        """Mark a task as completed."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute(
            'UPDATE tasks SET completed = 1, completed_at = ? WHERE id = ?',
            (now, task_id)
        )
        
        # Update daily stats
        today = date.today().isoformat()
        cursor.execute('''
            INSERT INTO daily_stats (date, tasks_completed)
            VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET tasks_completed = tasks_completed + 1
        ''', (today,))
        
        conn.commit()
        conn.close()
    
    def uncomplete_task(self, task_id: int):
        """Mark a task as not completed."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE tasks SET completed = 0, completed_at = NULL WHERE id = ?',
            (task_id,)
        )
        
        conn.commit()
        conn.close()
    
    def delete_task(self, task_id: int):
        """Delete a task and its associated sessions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM focus_sessions WHERE task_id = ?', (task_id,))
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        
        conn.commit()
        conn.close()
    
    def add_focus_time(self, task_id: int, seconds: int):
        """Add focus time to a task."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE tasks SET total_focus_seconds = total_focus_seconds + ? WHERE id = ?',
            (seconds, task_id)
        )
        
        conn.commit()
        conn.close()
    
    # ============== Session Operations ==============
    
    def start_session(self, task_id: Optional[int] = None, session_type: str = "work") -> int:
        """Start a new focus session and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO focus_sessions (task_id, start_time, session_type)
            VALUES (?, ?, ?)
        ''', (task_id, datetime.now().isoformat(), session_type))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def end_session(self, session_id: int, duration_seconds: int, completed: bool = True):
        """End a focus session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE focus_sessions 
            SET end_time = ?, duration_seconds = ?, completed = ?
            WHERE id = ?
        ''', (now, duration_seconds, int(completed), session_id))
        
        # Get session details
        cursor.execute('SELECT task_id, session_type FROM focus_sessions WHERE id = ?', (session_id,))
        row = cursor.fetchone()
        
        if row and row['session_type'] == 'work':
            # Update task focus time
            if row['task_id']:
                cursor.execute('''
                    UPDATE tasks 
                    SET total_focus_seconds = total_focus_seconds + ?
                    WHERE id = ?
                ''', (duration_seconds, row['task_id']))
            
            # Update daily stats
            today = date.today().isoformat()
            cursor.execute('''
                INSERT INTO daily_stats (date, total_focus_seconds, sessions_completed)
                VALUES (?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET 
                    total_focus_seconds = total_focus_seconds + ?,
                    sessions_completed = sessions_completed + ?
            ''', (today, duration_seconds, 1 if completed else 0,
                  duration_seconds, 1 if completed else 0))
        
        conn.commit()
        conn.close()
    
    def get_sessions_for_task(self, task_id: int) -> List[FocusSession]:
        """Get all sessions for a task."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM focus_sessions 
            WHERE task_id = ? 
            ORDER BY start_time DESC
        ''', (task_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            FocusSession(
                id=row['id'],
                task_id=row['task_id'],
                start_time=row['start_time'],
                end_time=row['end_time'],
                duration_seconds=row['duration_seconds'],
                session_type=row['session_type'],
                completed=bool(row['completed'])
            )
            for row in rows
        ]
    
    # ============== Stats Operations ==============
    
    def get_daily_stats(self, days: int = 7) -> List[DailyStats]:
        """Get daily stats for the last N days."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Generate date range
        today = date.today()
        dates = [(today - timedelta(days=i)).isoformat() for i in range(days)]
        
        stats = []
        for d in reversed(dates):
            cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (d,))
            row = cursor.fetchone()
            
            if row:
                stats.append(DailyStats(
                    date=row['date'],
                    total_focus_seconds=row['total_focus_seconds'],
                    sessions_completed=row['sessions_completed'],
                    tasks_completed=row['tasks_completed']
                ))
            else:
                stats.append(DailyStats(date=d))
        
        conn.close()
        return stats
    
    def get_today_stats(self) -> DailyStats:
        """Get stats for today."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (today,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return DailyStats(
                date=row['date'],
                total_focus_seconds=row['total_focus_seconds'],
                sessions_completed=row['sessions_completed'],
                tasks_completed=row['tasks_completed']
            )
        return DailyStats(date=today)
    
    def get_total_stats(self) -> Dict[str, int]:
        """Get total cumulative stats."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COALESCE(SUM(total_focus_seconds), 0) as total_focus,
                COALESCE(SUM(sessions_completed), 0) as total_sessions,
                COALESCE(SUM(tasks_completed), 0) as total_tasks
            FROM daily_stats
        ''')
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_focus_seconds': row['total_focus'] if row else 0,
            'total_sessions': row['total_sessions'] if row else 0,
            'total_tasks': row['total_tasks'] if row else 0
        }
    
    # ============== Settings Operations ==============
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting value."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row['value'] if row else default
    
    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = ?
        ''', (key, value, value))
        
        conn.commit()
        conn.close()
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        conn.close()
        
        return {row['key']: row['value'] for row in rows}
    
    # ============== Daily Goals Operations ==============
    
    def get_daily_goal(self, goal_date: Optional[str] = None) -> DailyGoal:
        """Get daily goal for a date (defaults to today)."""
        if goal_date is None:
            goal_date = date.today().isoformat()
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM daily_goals WHERE date = ?', (goal_date,))
        row = cursor.fetchone()
        
        if row:
            goal = DailyGoal(
                date=row['date'],
                target_minutes=row['target_minutes'],
                achieved_minutes=row['achieved_minutes']
            )
        else:
            # Get default goal from settings or use 120 minutes
            default_target = int(self.get_setting('daily_goal_minutes', '120'))
            goal = DailyGoal(date=goal_date, target_minutes=default_target)
        
        conn.close()
        return goal
    
    def set_daily_goal_target(self, target_minutes: int, goal_date: Optional[str] = None):
        """Set the daily goal target."""
        if goal_date is None:
            goal_date = date.today().isoformat()
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO daily_goals (date, target_minutes)
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET target_minutes = ?
        ''', (goal_date, target_minutes, target_minutes))
        
        # Also save as default for future days
        self.set_setting('daily_goal_minutes', str(target_minutes))
        
        conn.commit()
        conn.close()
    
    def add_to_daily_goal(self, minutes: int, goal_date: Optional[str] = None):
        """Add achieved minutes to daily goal."""
        if goal_date is None:
            goal_date = date.today().isoformat()
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # First ensure the goal exists
        goal = self.get_daily_goal(goal_date)
        
        cursor.execute('''
            INSERT INTO daily_goals (date, target_minutes, achieved_minutes)
            VALUES (?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET achieved_minutes = achieved_minutes + ?
        ''', (goal_date, goal.target_minutes, minutes, minutes))
        
        conn.commit()
        conn.close()
    
    def get_streak(self) -> int:
        """Get current streak of days where goal was achieved."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        streak = 0
        current_date = date.today()
        
        while True:
            date_str = current_date.isoformat()
            cursor.execute('''
                SELECT achieved_minutes, target_minutes FROM daily_goals 
                WHERE date = ?
            ''', (date_str,))
            row = cursor.fetchone()
            
            if row and row['achieved_minutes'] >= row['target_minutes']:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                # If it's today and we haven't achieved yet, check yesterday
                if current_date == date.today() and streak == 0:
                    current_date -= timedelta(days=1)
                    continue
                break
        
        conn.close()
        return streak
