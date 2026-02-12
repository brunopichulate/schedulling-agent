import re
from typing import Optional, Dict, Any
from src.core.database import get_database


def extract_name(query: str) -> str:
    """
    Extracts the mentor name from common question patterns.
    Examples:
    - "Who is AJ Nahmad?"
    - "Tell me about AJ Nahmad"
    - "AJ Nahmad"
    """
    match = re.search(
        r"(who is|tell me about|information about)\s+(.+?)(\?|$)",
        query,
        re.IGNORECASE,
    )

    if match:
        return match.group(2).strip()

    return query.strip().rstrip("?")


def find_mentor(query: str) -> Optional[Dict[str, Any]]:
    """
    Searches for a mentor in the 'person' collection
    inside the 'matching' database.

    Expected document structure:
    {
        "_id": "...",
        "name": "AJ Nahmad",
        "biography": "..."
    }
    """
    db = get_database()  # must already return the 'matching' database
    collection = db["person"]

    search_term = extract_name(query)

    mentor = collection.find_one(
        {
            "name": {
                "$regex": f"^{re.escape(search_term)}$",
                "$options": "i",
            }
        },
        {
            "_id": 0,
            "name": 1,
            "biography": 1,
        },
    )

    return mentor


def find_mentors_by_skill(skill_query: str, limit: int = 3) -> list[Dict[str, Any]]:
    """
    Searches for mentors based on a skill or topic.
    Checks 'functional_skills.macro', 'functional_skills.micro',
    and 'functional_skills_description'.
    Sorts by 'avg_mentor_rating' in descending order, handling mixed types (str, float, null).
    """
    db = get_database()
    collection = db["person"]

    # Case-insensitive regex for the skill query
    regex_query = {"$regex": re.escape(skill_query), "$options": "i"}

    pipeline = [
        {
            "$match": {
                "$or": [
                    {"functional_skills.macro": regex_query},
                    {"functional_skills.micro": regex_query},
                    {"functional_skills_description": regex_query},
                ]
            }
        },
        {
            "$addFields": {
                "normalized_rating": {
                    "$convert": {
                        "input": "$avg_mentor_rating",
                        "to": "double",
                        "onError": -1.0,
                        "onNull": -1.0
                    }
                },
                "normalized_time_donated": {
                    "$convert": {
                        "input": "$status.total_time_donated_year",
                        "to": "double",
                        "onError": -1.0,
                        "onNull": -1.0
                    }
                }
            }
        },
        {
            "$sort": {
                "normalized_rating": -1,
                "normalized_time_donated": -1
            }
        },
        {
            "$limit": limit
        },
        {
            "$project": {
                "_id": 0,
                "name": 1,
                "biography": 1,
                "functional_skills": 1,
                "functional_skills_description": 1,
                "avg_mentor_rating": 1,
                "status": 1
            }
        }
    ]

    cursor = collection.aggregate(pipeline)

    return list(cursor)
