import streamlit as st
import json
import os
from database import init_db, save_learner, get_latest_learner, save_plan, get_latest_plan, save_quiz_attempt, get_progress, get_weak_topics
from ai_service import generate_study_plan, generate_quiz, generate_feedback
from learning_plan import validate_plan, get_all_topics, get_next_topic
from quiz_manager import calculate_score
from dotenv import load_dotenv

load_dotenv()
init_db()

st.set_page_config(page_title="AI Personalized Learning Coach", page_icon="🎓", layout="wide")
st.title("🎓 AI Personalized Learning Coach")
st.caption("Personalized study plan • Topic quizzes • Progress tracking")
menu = st.sidebar.radio("Navigation", ["Home", "Setup Learner", "Study Plan", "Practice Quiz", "Progress Dashboard"])

if "learner" not in st.session_state:
    st.session_state.learner = get_latest_learner()
if "plan" not in st.session_state:
    st.session_state.plan = get_latest_plan(st.session_state.learner["id"]) if st.session_state.learner else None
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None

if menu == "Home":
    st.header("Welcome!")
    st.markdown("""
    **Flow:** Setup Learner -> Generate Plan with Gemini -> Practice Quiz -> Progress Dashboard
    - FR-01 to FR-12 all covered
    - SQLite persists after restart
    """)
    if st.session_state.learner:
        st.success(f"Active: {st.session_state.learner['subject']} - {st.session_state.learner['goal']}")
    else:
        st.warning("No learner yet. Go to Setup Learner.")

elif menu == "Setup Learner":
    st.header("👤 Learner Setup")
    with st.form("learner_form"):
        subject = st.text_input("Subject *", placeholder="e.g., Python, DSA")
        goal = st.text_area("Learning Goal *", placeholder="e.g., Learn Python fundamentals in 7 days")
        level = st.selectbox("Current Level *", ["Beginner", "Intermediate", "Advanced"])
        c1, c2 = st.columns(2)
        with c1:
            duration = st.number_input("Target Duration (days) *", 1, 60, 7)
        with c2:
            daily = st.number_input("Daily Study Time (min) *", 15, 240, 45, step=15)
        submitted = st.form_submit_button("Save & Generate Plan")
    if submitted:
        if not subject or not goal:
            st.error("Fill Subject and Goal")
        else:
            try:
                with st.spinner("Saving..."):
                    learner_id = save_learner(subject, goal, level, duration, daily)
                    st.session_state.learner = get_latest_learner()
                with st.spinner("Generating plan with Gemini..."):
                    plan_data = generate_study_plan(subject, goal, level, duration, daily)
                    valid, msg = validate_plan(plan_data)
                    if not valid:
                        st.error(f"Invalid plan: {msg}")
                    else:
                        save_plan(learner_id, plan_data)
                        st.session_state.plan = plan_data
                        st.success("Plan generated! Go to Study Plan page.")
                        st.json(plan_data)
            except Exception as e:
                st.error(f"Error: {e} - Check GEMINI_API_KEY in .env")

elif menu == "Study Plan":
    st.header("📚 Study Plan")
    if not st.session_state.learner or not st.session_state.plan:
        st.warning("Setup learner first")
    else:
        plan = st.session_state.plan
        st.subheader(f"{plan.get('subject')} - {plan.get('goal')}")
        for day in plan.get("plan", []):
            with st.expander(f"Day {day.get('day')}: {day.get('topic')}"):
                st.write(f"**Objective:** {day.get('objective')}")
                st.write(f"**Time:** {day.get('estimated_time')} min")
                st.write("**Activities:"); [st.write(f"- {a}") for a in day.get("activities", [])]
                st.write(f"**Practice:** {day.get('practice_task')}")
        if st.button("🔄 Regenerate Plan"):
            try:
                l = st.session_state.learner
                with st.spinner("Regenerating..."):
                    new_plan = generate_study_plan(l["subject"], l["goal"], l["level"], l["duration_days"], l["daily_minutes"])
                    save_plan(l["id"], new_plan)
                    st.session_state.plan = new_plan
                st.success("Regenerated!")
                st.rerun()
            except Exception as e:
                st.error(str(e))

elif menu == "Practice Quiz":
    st.header("📝 Practice Quiz")
    if not st.session_state.learner or not st.session_state.plan:
        st.warning("Setup learner and generate plan first")
    else:
        topics = get_all_topics(st.session_state.plan)
        selected_topic = st.selectbox("Select Topic (FR-04)", topics)
        num_q = st.slider("Questions", 3, 10, 5)
        if st.button("Generate Quiz"):
            try:
                with st.spinner(f"Generating quiz for {selected_topic}..."):
                    quiz = generate_quiz(selected_topic, st.session_state.learner["level"], st.session_state.learner["subject"], num_q)
                    st.session_state.current_quiz = quiz
                    st.session_state.current_topic = selected_topic
                st.success("Quiz ready!")
            except Exception as e:
                st.error(str(e))
        if st.session_state.current_quiz:
            st.divider()
            st.subheader(f"Quiz: {st.session_state.current_topic}")
            with st.form("quiz_form"):
                answers = {}
                for i, q in enumerate(st.session_state.current_quiz):
                    st.write(f"**Q{i+1}. {q['question']}**")
                    choice = st.radio(f"Answer Q{i+1}", q.get("options", []), key=f"q_{i}", index=None)
                    if choice:
                        answers[i] = choice[0]
                    st.caption(f"Difficulty: {q.get('difficulty', 'medium')}")
                    st.divider()
                submit = st.form_submit_button("Submit Answers")
            if submit:
                if len(answers) < len(st.session_state.current_quiz):
                    st.warning("Answer all questions")
                else:
                    score, details = calculate_score(st.session_state.current_quiz, answers)
                    st.success(f"Score: {score}/{len(st.session_state.current_quiz)}")
                    for d in details:
                        if d["is_correct"]:
                            st.success(f"✅ {d['question']}")
                        else:
                            st.error(f"❌ {d['question']} | Yours:{d['user']} Correct:{d['correct']}")
                        st.info(f"Explanation: {d['explanation']}")
                    try:
                        feedback = generate_feedback(st.session_state.current_topic, score, len(st.session_state.current_quiz), st.session_state.learner["level"])
                    except:
                        feedback = "Keep practicing!" if score / len(st.session_state.current_quiz) < 0.7 else "Great! Move ahead"
                    st.subheader("Feedback")
                    st.write(feedback)
                    save_quiz_attempt(st.session_state.learner["id"], st.session_state.current_topic, score, len(st.session_state.current_quiz), {"answers": answers, "details": details}, feedback)
                    st.success("Saved to SQLite")

elif menu == "Progress Dashboard":
    st.header("📊 Progress Dashboard")
    if not st.session_state.learner:
        st.warning("No learner")
    else:
        learner = st.session_state.learner
        topics_progress, attempts = get_progress(learner["id"])
        st.subheader("Topic Status")
        if topics_progress:
            for p in topics_progress:
                if p["status"] == "completed":
                    st.success(f"✅ {p['topic']} - Best:{p['best_score']} Attempts:{p['attempts']}")
                else:
                    st.error(f"🔄 {p['topic']} - Needs Revision | Best:{p['best_score']}")
        else:
            st.info("No quizzes yet")
        st.subheader("Weak Topics")
        weak = get_weak_topics(learner["id"])
        if weak:
            for w in weak:
                st.warning(f"⚠️ {w['topic']} - Score {w['best_score']} - Recommend revision")
        else:
            st.success("No weak topics")
        st.subheader("Recent History")
        for a in attempts:
            st.write(f"{a['created_at'][:19]} | {a['topic']} | {a['score']}/{a['total']}")
        if st.session_state.plan:
            next_t = get_next_topic(st.session_state.plan, topics_progress)
            if next_t:
                st.info(f"Next Recommended: {next_t}")
            else:
                st.success("All done!")
            completed = len([p for p in topics_progress if p["status"] == "completed"])
            total = len(st.session_state.plan.get("plan", []))
            st.progress(completed / total if total else 0)
            st.caption(f"Progress: {completed}/{total}")