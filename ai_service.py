import os, json, re
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)
MODEL_NAME="gemini-1.5-flash"
def get_model():
    if not api_key: raise ValueError("GEMINI_API_KEY not found")
    return genai.GenerativeModel(MODEL_NAME)
def extract_json(text):
    m=re.search(r"```(?:json)?\s*([\s\S]*?)\s*```",text)
    if m: text=m.group(1)
    s=text.find("{"); e=text.rfind("}")
    s2=text.find("["); e2=text.rfind("]")
    if s2!=-1 and e2!=-1 and (s==-1 or s2<s): text=text[s2:e2+1]
    elif s!=-1 and e!=-1: text=text[s:e+1]
    return text.strip()
def generate_study_plan(subject,goal,level,duration_days,daily_minutes):
    model=get_model()
    prompt=f"""You are AI Personalized Learning Coach. Create plan. Learner: Subject {subject}, Goal {goal}, Level {level}, Duration {duration_days} days, Daily {daily_minutes} min. Return ONLY valid JSON: {{"subject":"{subject}","goal":"{goal}","total_days":{duration_days},"daily_minutes":{daily_minutes},"plan":[{{"day":1,"topic":"Topic","objective":"Achieve","estimated_time":{daily_minutes},"activities":["A1","A2"],"practice_task":"Task"}}]}} Create exactly {duration_days} days progressive. No extra text."""
    raw=model.generate_content(prompt).text
    data=json.loads(extract_json(raw))
    return data
def generate_quiz(topic,level,subject,num_questions=5):
    model=get_model()
    prompt=f"""Generate quiz. Subject {subject}, Topic {topic}, Level {level}, Qs {num_questions}. Return ONLY JSON array: [{{"question":"text","options":["A) opt","B) opt","C) opt","D) opt"],"correct_answer":"A","explanation":"brief","difficulty":"easy"}}]. No extra text."""
    raw=model.generate_content(prompt).text
    data=json.loads(extract_json(raw))
    if isinstance(data,dict) and "questions" in data: data=data["questions"]
    return data
def generate_feedback(topic,score,total,level):
    model=get_model()
    prompt=f"Learner scored {score}/{total} on {topic} at {level}. Provide 2-3 lines encouraging feedback. If <60% recommend revision else next topic. Max 80 words."
    return model.generate_content(prompt).text.strip()