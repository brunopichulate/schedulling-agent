from src.services.mentor_service import find_mentor
import json

def search_mentor_tool(query: str) -> str:
    """
    Searches for a mentor in the database based on the name or query.
    Returns the biography if found, or a message indicating not found.
    
    Args:
        query (str): The name of the mentor or the question asking about the mentor.
    """
    mentor = find_mentor(query)
    if mentor:
        return json.dumps(mentor.get("biography", "Biography not available."), ensure_ascii=False)
    else:
        return "Mentor not found in the database."


def recommend_mentor_tool(topic: str, limit: int = 3) -> str:
    """
    Recommends mentors based on a specific topic or skill.
    
    Args:
        topic (str): The skill, expertise, or topic to find mentors for (e.g., 'marketing', 'compliance').
        limit (int): The maximum number of mentors to return. Defaults to 3.
    
    Returns:
        str: A JSON string containing a list of recommended mentors with their biographies and skills.
    """
    from src.services.mentor_service import find_mentors_by_skill
    
    mentors = find_mentors_by_skill(topic, limit=limit)
    
    if not mentors:
        return "No mentors found for the given topic."
        
    return json.dumps(mentors, ensure_ascii=False)
