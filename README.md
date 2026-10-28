# AI Personalized Learning Coach

Personalized study plan • Topic quizzes • Progress tracking

## Features FR-01 to FR-12
- Learner Setup (Subject, Goal, Level, Duration, Daily Time)
- Gemini generates personalized study plan (JSON)
- Quiz generation per topic
- Score calculated in Python (not LLM)
- Progress Dashboard with weak topics
- SQLite persistence

## Setup
1. pip install -r requirements.txt
2. Create .env with GEMINI_API_KEY=your_key
3. streamlit run app.py

## Tech
Streamlit, Gemini 1.5 Flash, SQLite