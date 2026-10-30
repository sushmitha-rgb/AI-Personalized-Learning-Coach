# AI-Personalized-Learning-Coach

An AI-powered tutor that creates personalized 7-day learning plans, quizzes, and tracks progress.

## Features
- Generate personalized study plan with Gemini AI
- Interactive Practice Quiz with scoring
- Progress Dashboard
- SQLite database for user progress

## How to Run
1. Clone: `git clone https://github.com/sushmitha-rgb/AI-Personalized-Learning-Coach.git`
2. Install: `pip install -r requirements.txt`
3. Add API Key: Create `.env` file with `GOOGLE_API_KEY=your_key`
4. Run: `streamlit run app.py`

## Screenshots
- Plan Generation Working
- Study Plan Page
- Quiz Page
- Progress Dashboard

## Fixed Issues
- Fixed ImportError: validate_plan from learning_plan
- Fixed database import errors
- Universal validator for all Gemini JSON formats

Built with Streamlit + Google Gemini 1.5 Flash
