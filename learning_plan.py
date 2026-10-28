def validate_plan(plan_data):
    if not isinstance(plan_data,dict): return False,"Plan must be dict"
    if "plan" not in plan_data: return False,"Missing plan"
    for item in plan_data["plan"]:
        if "day" not in item or "topic" not in item: return False,f"Missing fields {item}"
    return True,"Valid"
def get_all_topics(plan_data): return [d["topic"] for d in plan_data.get("plan",[])]
def get_next_topic(plan_data,progress):
    completed={p["topic"] for p in progress if p["status"]=="completed"}
    for t in get_all_topics(plan_data):
        if t not in completed: return t
    return None