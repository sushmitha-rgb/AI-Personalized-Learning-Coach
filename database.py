import sqlite3
import json
from datetime import datetime

DB_FILE = "learning_coach.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS learners (
            id INTEGER PRIMARY KEY, subject TEXT, goal TEXT, level TEXT,
            duration_days INTEGER, daily_minutes INTEGER, created_at TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY, learner_id INTEGER, plan_json TEXT, created_at TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY, topic TEXT, score INTEGER, total INTEGER
        )""")

def save_learner(subject, goal, level, duration_days, daily_minutes):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            "INSERT INTO learners (subject, goal, level, duration_days, daily_minutes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (subject, goal, level, duration_days, daily_minutes, datetime.now().isoformat()),
        )
        return cursor.lastrowid

def get_latest_learner():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM learners ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else None

def save_plan(learner_id, plan):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO plans (learner_id, plan_json, created_at) VALUES (?, ?, ?)",
            (learner_id, json.dumps(plan), datetime.now().isoformat()),
        )

def get_latest_plan(learner_id):
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute(
            "SELECT plan_json FROM plans WHERE learner_id = ? ORDER BY id DESC LIMIT 1",
            (learner_id,),
        ).fetchone()
    return json.loads(row[0]) if row else None

def save_quiz_result(topic, score, total):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO quiz_results VALUES (NULL,?,?,?)", (topic, score, total))
    conn.commit()
    conn.close()

def save_quiz_attempt(topic, score, total):
    return save_quiz_result(topic, score, total)

def get_progress():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT topic, score, total FROM quiz_results ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [{"Topic": r[0], "Score": f"{r[1]}/{r[2]}", "Percent": round(r[1]/r[2]*100,1) if r[2] else 0} for r in rows]

def get_weak_topics():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT topic, score, total FROM quiz_results WHERE score < total*0.6")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_quiz_history():
    return get_progress()