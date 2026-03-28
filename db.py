import sqlite3
from datetime import datetime
import hashlib

DB_PATH = "learning_history.db"


# -------------------------------------------------
# UTILS
# -------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------------------------------------
# INIT DB
# -------------------------------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # USERS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # PER-CHECKPOINT PERFORMANCE (SINGLE SOURCE OF TRUTH)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS checkpoint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            checkpoint_id INTEGER,
            checkpoint_title TEXT,
            score INTEGER,
            total INTEGER,
            percentage REAL,
            passed INTEGER,
            relevance REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# AUTH
# -------------------------------------------------
def create_user(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
        """, (
            username,
            hash_password(password),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, password_hash
        FROM users
        WHERE username = ?
    """, (username,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    user_id, stored_hash = row
    return user_id if stored_hash == hash_password(password) else None


# -------------------------------------------------
# SAVE CHECKPOINT PERFORMANCE
# -------------------------------------------------
def save_checkpoint_performance(
    user_id,
    checkpoint_id,
    title,
    score,
    total,
    percentage,
    passed,
    relevance
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO checkpoint_history
        (user_id, timestamp, checkpoint_id, checkpoint_title, score, total, percentage, passed, relevance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        checkpoint_id,
        title,
        score,
        total,
        percentage,
        int(passed),
        relevance
    ))

    conn.commit()
    conn.close()


# -------------------------------------------------
# FETCH CHECKPOINT HISTORY
# -------------------------------------------------
def fetch_checkpoint_history(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, checkpoint_title, score, total, percentage, passed
        FROM checkpoint_history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "timestamp": r[0],
            "checkpoint": r[1],
            "score": r[2],
            "total": r[3],
            "percentage": r[4],
            "passed": bool(r[5])
        }
        for r in rows
    ]


# -------------------------------------------------
# FETCH OVERALL STATS (DERIVED)
# -------------------------------------------------
def fetch_overall_stats(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) as attempted,
            SUM(score) as total_score,
            SUM(total) as max_score,
            AVG(percentage) as avg_percentage
        FROM checkpoint_history
        WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()

    if not row or row[0] == 0:
        return None

    return {
        "attempted": row[0],
        "total_score": row[1],
        "max_score": row[2],
        "avg_percentage": row[3]
    }
