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
