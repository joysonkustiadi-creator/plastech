import sqlite3
import pandas as pd
from datetime import datetime
from config import Config

class DatabaseManager:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    # ============================
    # INIT DATABASE (CREATE TABLE)
    # ============================
    def init_database(self):
        conn = self.get_connection()
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            waste_type TEXT,
            points INTEGER,
            image_data BLOB,
            status TEXT DEFAULT 'pending',
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS disposal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            detection_id INTEGER,
            qr_code TEXT,
            image_data BLOB,
            disposed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (detection_id) REFERENCES detections (id)
        )
        """)

        conn.commit()
        conn.close()

    # ============================
    # USERS
    # ============================
    def create_user(self, username, hashed_password):
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username, hashed_password):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed_password)
        )
        user = c.fetchone()
        conn.close()
        return user

    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM users WHERE id=?", conn, params=(user_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    def get_user_by_id_simple(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, points FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'username': row[1], 'points': row[2]}
        return None

    def refresh_user(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, points FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user

    def update_user_points(self, user_id, points):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE users SET points = points + ? WHERE id = ?",
            (points, user_id)
        )
        conn.commit()
        conn.close()

    # ============================
    # DETECTIONS
    # ============================
    def create_detection(self, user_id, waste_type, points, image_data, expires_at):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO detections (user_id, waste_type, points, image_data, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, waste_type, points, image_data, expires_at))
        conn.commit()
        conn.close()

    def get_pending_detections(self, user_id):
        conn = self.get_connection()
        df = pd.read_sql_query("""
            SELECT id, waste_type, points, detected_at, expires_at
            FROM detections
            WHERE user_id=? AND status='pending'
            ORDER BY detected_at DESC
        """, conn, params=(user_id,))
        conn.close()
        return df

    def get_user_detections(self, user_id, limit=10):
        conn = self.get_connection()
        df = pd.read_sql_query("""
            SELECT waste_type, points, status, detected_at, expires_at
            FROM detections
            WHERE user_id=?
            ORDER BY detected_at DESC
            LIMIT ?
        """, conn, params=(user_id, limit))
        conn.close()
        return df

    def update_detection_status(self, detection_id, status):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE detections SET status=? WHERE id=?", (status, detection_id))
        conn.commit()
        conn.close()

    def expire_old_detections(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            UPDATE detections SET status = 'expired'
            WHERE status = 'pending' AND expires_at < datetime('now')
        """)
        conn.commit()
        conn.close()

    # ============================
    # DISPOSAL
    # ============================
    def create_disposal(self, user_id, detection_id, qr_code, image_data):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO disposal (user_id, detection_id, qr_code, image_data)
            VALUES (?, ?, ?, ?)
        """, (user_id, detection_id, qr_code, image_data))
        conn.commit()
        conn.close()

    # ============================
    # STATISTICS
    # ============================
    def get_user_stats(self, user_id):
        conn = self.get_connection()

        pending = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM detections WHERE user_id=? AND status='pending'",
            conn, params=(user_id,)
        )['count'][0]

        detected = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM detections WHERE user_id=?",
            conn, params=(user_id,)
        )['count'][0]

        disposed = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM disposal WHERE user_id=?",
            conn, params=(user_id,)
        )['count'][0]

        conn.close()

        return {
            'pending': pending,
            'detected': detected,
            'disposed': disposed
        }

    def get_leaderboard(self, limit=10):
        conn = self.get_connection()
        df = pd.read_sql_query("""
            SELECT username, points,
                (SELECT COUNT(*) FROM disposal WHERE user_id = users.id) as total_disposed
            FROM users
            ORDER BY points DESC
            LIMIT ?
        """, conn, params=(limit,))
        conn.close()
        return df