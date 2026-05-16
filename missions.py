"""
Core mission generation and enhancement logic - extracted for testability.
This module contains the business logic decoupled from Streamlit UI.
"""

import random
import requests
from typing import Tuple, Dict, Any, List

# Default fallback data
CYBER_PREFIXES = [
    "TACTICAL RECONNAISSANCE PROTOCOL",
    "SILENT OBJECTIVE VECTOR",
    "CRITICAL METRIC HUNT",
    "MINIMALIST FRAMING COGNITION",
    "GEOMETRIC MATRIX TRACKER"
]

CYBER_ATMOSPHERES = {
    "WALK": [
        "TRACKING ON FOOT ALONG THE REINFORCED PERIMETERS OF",
        "NAVIGATING THE HIGH-CONTRAST URBAN CORRIDORS OF",
        "EXECUTING MOVEMENT DRILLS DOWN THE BLOCKS OF"
    ],
    "EAT": [
        "SOURCING SUSTENANCE NANO-COUNTER TILES INSIDE",
        "RECONNOITERING KITCHEN EMISSION VENTS IN",
        "LOCATING A SEAFOOD OR GRAIN REFUEL STATION WITHIN"
    ],
    "CHILL": [
        "LOCATING A STATIONARY REST PROFILE DECK AMIDST",
        "ESTABLISHING A STATIC OBSERVATION SECTOR IN",
        "ANCHORING POSITION TO ASSIMILATE THE AMBIENT GRID OF"
    ]
}

DEFAULT_BASE_VIBES = {
    "EAT": "CULINARY INTERCEPT MATRIX // AVOCADO-FREE PESCATARIAN PROFILE",
    "CHILL": "STATIC STATIONARY ANCHOR // ATMOSPHERIC CALIBRATION",
    "WALK": "URBAN ARCHITECTURE MATRIX"
}

DEFAULT_MISSIONS = {
    "EAT": ["Locate a marketplace counter. Secure shared plates. Zero land-meat broths, zero avocados."],
    "CHILL": ["Halt transit vector. Identify a step or architectural ledge to sit silently."],
    "WALK": ["Document structural geometric features on foot."]
}


def select_base_mission(action_type: str, adventure_pool: Dict[str, Any], used_missions: List[str]) -> Tuple[str, str]:
    """
    Select a base vibe and mission for the given action type.
    
    Args:
        action_type: One of "WALK", "EAT", or "CHILL"
        adventure_pool: Dictionary containing adventure data
        used_missions: List of previously used mission strings
        
    Returns:
        Tuple of (base_vibe, base_mission)
    """
    if action_type == "EAT":
        base_vibe = DEFAULT_BASE_VIBES["EAT"]
        pool = adventure_pool.get("EAT", {}).get("missions", DEFAULT_MISSIONS["EAT"])
    elif action_type == "CHILL":
        base_vibe = DEFAULT_BASE_VIBES["CHILL"]
        pool = adventure_pool.get("CHILL", {}).get("missions", DEFAULT_MISSIONS["CHILL"])
    else:  # WALK
        vibes = adventure_pool.get("vibes", ["URBAN ARCHITECTURE MATRIX"])
        base_vibe = random.choice(vibes) if vibes else DEFAULT_BASE_VIBES["WALK"]
        pool = adventure_pool.get("WALK", {}).get("missions", DEFAULT_MISSIONS["WALK"])
    
    # Prefer unused missions, but fall back to any mission if all are used
    unused = [m for m in pool if m not in used_missions]
    base_mission = random.choice(unused if unused else pool)
    
    return base_vibe, base_mission


def parse_gemini_response(ai_response: str) -> Tuple[str, str]:
    """
    Parse Gemini AI response to extract VIBE and MISSION.
    Handles multiple response formats and edge cases.
    
    Args:
        ai_response: Raw text response from Gemini
        
    Returns:
        Tuple of (extracted_vibe, extracted_mission)
    """
    extracted_vibe = ""
    extracted_mission = ""
    
    if not ai_response or not ai_response.strip():
        return extracted_vibe, extracted_mission
    
    for line in ai_response.split("\n"):
        clean_line = line.replace("**", "").replace("*", "").strip()
        if not clean_line:
            continue
        
        line_upper = clean_line.upper()
        if line_upper.startswith("VIBE:"):
            extracted_vibe = clean_line[5:].strip()
        elif line_upper.startswith("MISSION:"):
            extracted_mission = clean_line[8:].strip()
    
    return extracted_vibe, extracted_mission


def create_mission_id(action_type: str, mission: str) -> str:
    """
    Create a unique mission ID label.
    
    Args:
        action_type: Action category (WALK, EAT, CHILL)
        mission: The mission text
        
    Returns:
        Unique label string
    """
    random_hash = random.randint(1000, 9999)
    return f"{action_type} [{random_hash}]: {mission[:20]}..."


def validate_action_type(action_type: str) -> bool:
    """
    Validate that action_type is one of the allowed values.
    
    Args:
        action_type: The action type to validate
        
    Returns:
        True if valid, False otherwise
    """
    return action_type in ["WALK", "EAT", "CHILL"]


def validate_mission_structure(mission_dict: Dict[str, Any]) -> bool:
    """
    Validate that a mission dictionary has all required fields.
    
    Args:
        mission_dict: Dictionary to validate
        
    Returns:
        True if valid structure, False otherwise
    """
    required_fields = ["label", "mood", "vibe", "mission", "legendary", "ai_generated"]
    return all(field in mission_dict for field in required_fields)


def count_missions_by_type(itinerary: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count missions by type (WALK, EAT, CHILL).
    
    Args:
        itinerary: List of mission dictionaries
        
    Returns:
        Dictionary with counts for each type
    """
    counts = {"WALK": 0, "EAT": 0, "CHILL": 0}
    for item in itinerary:
        mood = item.get("mood", "")
        if mood in counts:
            counts[mood] += 1
    return counts


def count_ai_generated(itinerary: List[Dict[str, Any]]) -> int:
    """
    Count how many missions were AI-generated.
    
    Args:
        itinerary: List of mission dictionaries
        
    Returns:
        Count of AI-generated missions
    """
    return sum(1 for item in itinerary if item.get("ai_generated", False))


def validate_pescatarian_dietary_constraints(mission_text: str) -> bool:
    """
    Check if mission text violates pescatarian/avocado constraints.
    Returns True if mission is OK, False if it contains violations.
    
    Args:
        mission_text: The mission text to validate
        
    Returns:
        True if compliant, False if contains violations
    """
    violations = ["avocado", "beef", "chicken", "pork", "lamb", "turkey"]
    text_lower = mission_text.lower()
    
    for violation in violations:
        if violation in text_lower:
            return False
    return True


def get_mission_summary_stats(itinerary: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics for an itinerary.
    
    Args:
        itinerary: List of mission dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
    type_counts = count_missions_by_type(itinerary)
    ai_count = count_ai_generated(itinerary)
    
    return {
        "total_stops": len(itinerary),
        "walk_count": type_counts["WALK"],
        "eat_count": type_counts["EAT"],
        "chill_count": type_counts["CHILL"],
        "ai_generated_count": ai_count,
        "local_generated_count": len(itinerary) - ai_count
    }
