def calculate_score(quiz_questions,user_answers):
    score=0; details=[]
    for i,q in enumerate(quiz_questions):
        correct=q.get("correct_answer","").strip().upper()[0]
        user=""
        if isinstance(user_answers,dict): user=str(user_answers.get(i,"")).strip().upper()
        elif isinstance(user_answers,list) and i<len(user_answers): user=str(user_answers[i]).strip().upper()
        if user: user=user[0]
        is_correct=user==correct
        if is_correct: score+=1
        details.append({"question":q["question"],"correct":correct,"user":user,"is_correct":is_correct,"explanation":q.get("explanation","")})
    return score,details