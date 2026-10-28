import sqlite3, json
from datetime import datetime
DB_PATH="learning_coach.db"
def get_conn():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; return conn
def init_db():
    conn=get_conn(); c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS learners (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, goal TEXT, level TEXT, duration_days INTEGER, daily_minutes INTEGER, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS plans (id INTEGER PRIMARY KEY AUTOINCREMENT, learner_id INTEGER, plan_json TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS quiz_attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, learner_id INTEGER, topic TEXT, score INTEGER, total INTEGER, answers_json TEXT, feedback TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS topic_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, learner_id INTEGER, topic TEXT, status TEXT, best_score INTEGER, attempts INTEGER DEFAULT 0, UNIQUE(learner_id, topic))")
    conn.commit(); conn.close()
def save_learner(subject,goal,level,duration_days,daily_minutes):
    conn=get_conn(); c=conn.cursor()
    c.execute("INSERT INTO learners VALUES (NULL,?,?,?,?,?,?)",(subject,goal,level,duration_days,daily_minutes,datetime.now().isoformat()))
    lid=c.lastrowid; conn.commit(); conn.close(); return lid
def get_latest_learner():
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM learners ORDER BY id DESC LIMIT 1"); row=c.fetchone(); conn.close(); return dict(row) if row else None
def save_plan(learner_id,plan_json):
    conn=get_conn(); c=conn.cursor(); c.execute("INSERT INTO plans VALUES (NULL,?,?,?)",(learner_id,json.dumps(plan_json),datetime.now().isoformat())); conn.commit(); conn.close()
def get_latest_plan(learner_id):
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM plans WHERE learner_id=? ORDER BY id DESC LIMIT 1",(learner_id,)); row=c.fetchone(); conn.close(); return json.loads(row["plan_json"]) if row else None
def save_quiz_attempt(learner_id,topic,score,total,answers,feedback=""):
    conn=get_conn(); c=conn.cursor()
    c.execute("INSERT INTO quiz_attempts VALUES (NULL,?,?,?,?,?,?,?)",(learner_id,topic,score,total,json.dumps(answers),feedback,datetime.now().isoformat()))
    c.execute("SELECT * FROM topic_progress WHERE learner_id=? AND topic=?",(learner_id,topic)); ex=c.fetchone()
    status="completed" if score/total>=0.7 else "needs_revision"
    if ex:
        best=max(ex["best_score"] or 0, score)
        c.execute("UPDATE topic_progress SET status=?, best_score=?, attempts=attempts+1 WHERE learner_id=? AND topic=?",(status,best,learner_id,topic))
    else:
        c.execute("INSERT INTO topic_progress VALUES (NULL,?,?,?,?,?)",(learner_id,topic,status,score,1))
    conn.commit(); conn.close()
def get_progress(learner_id):
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT * FROM topic_progress WHERE learner_id=?",(learner_id,)); topics=[dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM quiz_attempts WHERE learner_id=? ORDER BY created_at DESC LIMIT 10",(learner_id,)); attempts=[dict(r) for r in c.fetchall()]
    conn.close(); return topics,attempts
def get_weak_topics(learner_id):
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM topic_progress WHERE learner_id=? AND status='needs_revision'",(learner_id,)); rows=[dict(r) for r in c.fetchall()]; conn.close(); return rows