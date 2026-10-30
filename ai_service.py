import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

def generate_text(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        # fallback try other models
        for fallback in ["gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-3-flash-preview"]:
            try:
                response = client.models.generate_content(
                    model=fallback,
                    contents=prompt
                )
                return response.text
            except:
                continue
        raise Exception(f"{str(e)} - Check GEMINI_API_KEY in .env")

def generate_study_plan(subject, goal, level, duration, daily_time):
    prompt = f"""
    You are AI Learning Coach. Create a personalized study plan.
    Subject: {subject}
    Goal: {goal}
    Level: {level}
    Duration: {duration} days
    Daily Time: {daily_time} mins

    Output MUST be ONLY valid JSON. No explanation, no markdown.
    Structure:
    {{
      "plan_summary": "short summary",
      "days": [
        {{"day": 1, "topic": "Variables in Python", "objectives": ["Understand variables", "Practice examples"], "resources": ["Python docs"], "estimated_minutes": {daily_time}}},
        {{"day": 2, "topic": "Data Types", "objectives": ["Learn types"], "resources": ["W3Schools"], "estimated_minutes": {daily_time}}}
      ]
    }}
    Generate exactly {duration} days for beginner learning {subject}.
    """
    text = generate_text(prompt)
    print("RAW GEMINI:", text[:500]) # debug in terminal
    
    # robust JSON extract
    import re
    text = text.replace("```json","").replace("```","").strip()
    # find first { to last }
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        text = match.group(0)
    
    data = json.loads(text)
    
    # Ensure required keys exist
    if "days" not in data:
        raise ValueError("Missing days in plan")
    if "plan_summary" not in data:
        data["plan_summary"] = f"Personalized {duration} day plan for {subject}"
    
    return data
    prompt = f"""
    You are AI Learning Coach. Create a personalized study plan.

    Learner: Subject={subject}, Goal={goal}, Level={level}, Duration={duration} days, Daily={daily_time} mins

    Return ONLY valid JSON, no markdown:
    {{
      "plan_summary": "2 line summary",
      "days": [
        {{"day": 1, "topic": "Topic Name", "objectives": ["obj1","obj2"], "resources": ["resource"], "estimated_minutes": {daily_time}}},
        {{"day": 2, "topic": "..."}}
      ]
    }}
    Generate exactly {duration} days.
    """
    text = generate_text(prompt)
    # clean json
    text = text.replace("```json","").replace("```","").strip()
    return json.loads(text)

def generate_quiz(topic, level="Beginner", subject="", num_questions=5):
    prompt = f"""
    Create {num_questions} MCQs for topic: {topic}, Subject: {subject}, Level: {level}
    Return ONLY valid JSON:
    {{
      "topic": "{topic}",
      "questions": [
        {{"q": "question?", "options": ["A","B","C","D"], "answer": 0, "explanation": "why"}}
      ]
    }}
    answer is 0-3 index.
    """
    text = generate_text(prompt)
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)
    questions = data.get("questions", []) if isinstance(data, dict) else data
    if not isinstance(questions, list):
        raise ValueError("Quiz response must contain a list of questions")

    normalized_questions = []
    for item in questions:
        if not isinstance(item, dict):
            continue

        question = item.get("question") or item.get("q")
        options = item.get("options", [])
        if not question or not isinstance(options, list) or not options:
            continue

        labeled_options = []
        for index, option in enumerate(options):
            option_text = str(option)
            label = chr(ord("A") + index)
            if not re.match(r"^[A-D](?:[.) :]\s*|\s+)", option_text, re.IGNORECASE):
                option_text = f"{label}. {option_text}"
            labeled_options.append(option_text)

        answer = item.get("correct_answer", item.get("answer"))
        if isinstance(answer, int) or (isinstance(answer, str) and answer.isdigit()):
            answer_index = int(answer)
            correct_answer = chr(ord("A") + answer_index) if 0 <= answer_index < len(options) else ""
        elif isinstance(answer, str):
            answer_match = re.match(r"^\s*([A-D])(?:[.) :]\s*|\s+|$)", answer, re.IGNORECASE)
            if answer_match:
                correct_answer = answer_match.group(1).upper()
            else:
                matching_option = next(
                    (index for index, option in enumerate(options) if str(option) == answer),
                    -1,
                )
                correct_answer = chr(ord("A") + matching_option) if matching_option >= 0 else ""
        else:
            correct_answer = ""

        normalized_questions.append({
            "question": question,
            "options": labeled_options,
            "correct_answer": correct_answer,
            "explanation": item.get("explanation", ""),
            "difficulty": item.get("difficulty", "medium"),
        })

    if not normalized_questions:
        raise ValueError("Quiz response did not contain any valid questions")
    return normalized_questions
def generate_feedback(topic, score, total, weak_topics=None):
    prompt = f"""
    You are a friendly learning coach.
    Student scored {score}/{total} on topic {topic}.
    Weak topics: {weak_topics}
    
    Give 2-3 lines of motivational feedback + 1 tip to improve. Be encouraging.
    """
    try:
        return generate_text(prompt)
    except:
        if score == total:
            return f"Excellent! You mastered {topic}! 🎉"
        elif score >= total*0.6:
            return f"Good job on {topic}! Review weak areas and try again."
        else:
            return f"Don't worry! {topic} needs more practice. Check your study plan day for {topic}."