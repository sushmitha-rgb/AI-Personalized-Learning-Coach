def validate_plan(plan_data):
    """Main validator - accepts all Gemini formats"""
    if not plan_data:
        raise ValueError("Missing plan - empty")
    
    # Handle {"plan": {...}} wrapper
    if "plan" in plan_data and isinstance(plan_data["plan"], dict):
        plan_data = plan_data["plan"]
    
    # Handle different keys for days
    if "days" not in plan_data:
        if "study_plan" in plan_data:
            plan_data["days"] = plan_data["study_plan"]
        elif "week_plan" in plan_data:
            plan_data["days"] = plan_data["week_plan"]
        elif "plan_data" in plan_data:
            plan_data["days"] = plan_data["plan_data"]
        else:
            raise ValueError(f"Missing plan - keys found: {list(plan_data.keys())}")
    
    if not isinstance(plan_data["days"], list) or len(plan_data["days"]) == 0:
        raise ValueError("Missing plan - days is empty")
    
    if "plan_summary" not in plan_data:
        plan_data["plan_summary"] = "Your personalized learning journey"
    
    return plan_data

# ALIASES for different app.py versions - all point to same function
def validate_and_save_plan(plan_data):
    return validate_plan(plan_data)

def validate_and_parse_plan(plan_data):
    return validate_plan(plan_data)

def get_plan_summary(plan_data):
    return plan_data.get("plan_summary", "Plan")

def format_plan_for_display(plan_data):
    return validate_plan(plan_data)

def get_all_topics(plan_data):
    plan = validate_plan(plan_data)
    return [day["topic"] for day in plan["days"] if day.get("topic")]

def get_next_topic(plan_data, topics_progress):
    completed_topics = {
        item["topic"] for item in topics_progress
        if item.get("status") == "completed"
    }
    return next(
        (topic for topic in get_all_topics(plan_data) if topic not in completed_topics),
        None,
    )