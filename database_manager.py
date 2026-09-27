import mysql.connector
import pandas as pd
from datetime import datetime
from config import Config

class DatabaseManager:
    def __init__(self):
        self.init_database()

    def get_connection(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # default XAMPP
            database=Config.DB_NAME
        )

    # ============================
    # INIT DATABASE (CREATE TABLE)
    # ============================
    def init_database(self):
        conn = self.get_connection()
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            points INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            waste_type VARCHAR(255),
            points INT,
            image_data LONGBLOB,
            status VARCHAR(50) DEFAULT 'pending',
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS disposal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            detection_id INT,
            qr_code VARCHAR(255),
            image_data LONGBLOB,
            disposed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (detection_id) REFERENCES detections(id)
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
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()
            return True
        except mysql.connector.IntegrityError:
            return False

    def get_user(self, username, hashed_password):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                  (username, hashed_password))
        user = c.fetchone()
        conn.close()
        return user

    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        df = pd.read_sql("SELECT * FROM users WHERE id=%s", conn, params=(user_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    def update_user_points(self, user_id, points):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE users SET points = points + %s WHERE id = %s",
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
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, waste_type, points, image_data, expires_at))
        conn.commit()
        conn.close()

    def get_pending_detections(self, user_id):
        conn = self.get_connection()
        df = pd.read_sql("""
            SELECT id, waste_type, points, detected_at, expires_at
            FROM detections
            WHERE user_id=%s AND status='pending'
            ORDER BY detected_at DESC
        """, conn, params=(user_id,))
        conn.close()
        return df

    def get_user_detections(self, user_id, limit=10):
        conn = self.get_connection()
        df = pd.read_sql("""
            SELECT waste_type, points, status, detected_at, expires_at
            FROM detections
            WHERE user_id=%s
            ORDER BY detected_at DESC
            LIMIT %s
        """, conn, params=(user_id, limit))
        conn.close()
        return df

    def update_detection_status(self, detection_id, status):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE detections SET status=%s WHERE id=%s",
                  (status, detection_id))
        conn.commit()
        conn.close()

    def expire_old_detections(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            UPDATE detections SET status='expired'
            WHERE status='pending' AND expires_at < NOW()
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
            VALUES (%s, %s, %s, %s)
        """, (user_id, detection_id, qr_code, image_data))
        conn.commit()
        conn.close()

    # ============================
    # STATISTICS
    # ============================
    def get_user_stats(self, user_id):
        conn = self.get_connection()

        pending = pd.read_sql(
            "SELECT COUNT(*) AS c FROM detections WHERE user_id=%s AND status='pending'",
            conn, params=(user_id,)
        )['c'][0]

        detected = pd.read_sql(
            "SELECT COUNT(*) AS c FROM detections WHERE user_id=%s",
            conn, params=(user_id,)
        )['c'][0]

        disposed = pd.read_sql(
            "SELECT COUNT(*) AS c FROM disposal WHERE user_id=%s",
            conn, params=(user_id,)
        )['c'][0]

        conn.close()

        return {
            'pending': pending,
            'detected': detected,
            'disposed': disposed
        }

    def get_leaderboard(self, limit=10):
        conn = self.get_connection()
        df = pd.read_sql("""
            SELECT username, points,
                (SELECT COUNT(*) FROM disposal WHERE user_id = users.id) AS total_disposed
            FROM users
            ORDER BY points DESC
            LIMIT %s
        """, conn, params=(limit,))
        conn.close()
        return df

    def refresh_user(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, points FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    
    def get_user_by_id_simple(self, user_id):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT id, username, points FROM users WHERE id=%s", (user_id,))
        row = c.fetchone()
        conn.close()
        return row