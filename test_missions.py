"""
Unit Tests for NYC Trail Planner
Tests core mission logic, validation, and data processing.
"""

import pytest
from missions import (
    select_base_mission,
    parse_gemini_response,
    create_mission_id,
    validate_action_type,
    validate_mission_structure,
    count_missions_by_type,
    count_ai_generated,
    validate_pescatarian_dietary_constraints,
    get_mission_summary_stats,
    CYBER_PREFIXES,
    CYBER_ATMOSPHERES,
    DEFAULT_BASE_VIBES,
    DEFAULT_MISSIONS,
)


class TestActionTypeValidation:
    """Test action type validation logic."""
    
    def test_valid_action_types(self):
        """Test that valid action types are recognized."""
        assert validate_action_type("WALK") is True
        assert validate_action_type("EAT") is True
        assert validate_action_type("CHILL") is True
    
    def test_invalid_action_types(self):
        """Test that invalid action types are rejected."""
        assert validate_action_type("INVALID") is False
        assert validate_action_type("run") is False
        assert validate_action_type("") is False
        assert validate_action_type("walk") is False  # case sensitive


class TestBaseMissionSelection:
    """Test mission selection from adventure pool."""
    
    def test_select_base_mission_eat(self):
        """Test EAT mission selection."""
        adventure_pool = {
            "EAT": {
                "missions": ["Mission 1", "Mission 2", "Mission 3"]
            }
        }
        vibe, mission = select_base_mission("EAT", adventure_pool, [])
        
        assert vibe == DEFAULT_BASE_VIBES["EAT"]
        assert mission in ["Mission 1", "Mission 2", "Mission 3"]
    
    def test_select_base_mission_walk(self):
        """Test WALK mission selection."""
        adventure_pool = {
            "vibes": ["Vibe 1", "Vibe 2"],
            "WALK": {
                "missions": ["Walk Mission 1", "Walk Mission 2"]
            }
        }
        vibe, mission = select_base_mission("WALK", adventure_pool, [])
        
        assert vibe in ["Vibe 1", "Vibe 2"]
        assert mission in ["Walk Mission 1", "Walk Mission 2"]
    
    def test_select_base_mission_chill(self):
        """Test CHILL mission selection."""
        adventure_pool = {
            "CHILL": {
                "missions": ["Chill 1", "Chill 2"]
            }
        }
        vibe, mission = select_base_mission("CHILL", adventure_pool, [])
        
        assert vibe == DEFAULT_BASE_VIBES["CHILL"]
        assert mission in ["Chill 1", "Chill 2"]
    
    def test_select_base_mission_unused_preferred(self):
        """Test that unused missions are preferred over used ones."""
        adventure_pool = {
            "WALK": {
                "missions": ["Mission 1", "Mission 2"]
            },
            "vibes": ["Vibe"]
        }
        # Mark one mission as used
        used_missions = ["Mission 1"]
        
        # Run multiple times to increase chance of getting unused mission
        results = []
        for _ in range(10):
            _, mission = select_base_mission("WALK", adventure_pool, used_missions)
            results.append(mission)
        
        # Should predominantly get Mission 2 (the unused one)
        assert results.count("Mission 2") > 5
    
    def test_select_base_mission_fallback_to_defaults(self):
        """Test fallback to default missions when pool is empty."""
        adventure_pool = {}
        vibe, mission = select_base_mission("WALK", adventure_pool, [])
        
        assert vibe == DEFAULT_BASE_VIBES["WALK"]
        assert mission == DEFAULT_MISSIONS["WALK"][0]


class TestGeminiResponseParsing:
    """Test parsing of Gemini AI responses."""
    
    def test_parse_valid_gemini_response(self):
        """Test parsing a properly formatted Gemini response."""
        response = """VIBE: The underground speakeasy pulse
MISSION: Navigate the neon-lit corridors at dusk"""
        
        vibe, mission = parse_gemini_response(response)
        
        assert vibe == "The underground speakeasy pulse"
        assert mission == "Navigate the neon-lit corridors at dusk"
    
    def test_parse_gemini_response_with_markdown(self):
        """Test parsing response with markdown formatting."""
        response = """**VIBE:** The bustling market energy
**MISSION:** Capture the geometric angles of the street"""
        
        vibe, mission = parse_gemini_response(response)
        
        assert vibe == "The bustling market energy"
        assert mission == "Capture the geometric angles of the street"
    
    def test_parse_gemini_response_with_extra_whitespace(self):
        """Test parsing response with extra whitespace."""
        response = """   VIBE:   The cool rooftop breeze   
   MISSION:   Find a quiet corner to observe   """
        
        vibe, mission = parse_gemini_response(response)
        
        assert vibe == "The cool rooftop breeze"
        assert mission == "Find a quiet corner to observe"
    
    def test_parse_incomplete_gemini_response(self):
        """Test parsing incomplete response returns empty strings."""
        response = """VIBE: Some vibe
Something else"""
        
        vibe, mission = parse_gemini_response(response)
        
        assert vibe == "Some vibe"
        assert mission == ""
    
    def test_parse_empty_gemini_response(self):
        """Test parsing empty response."""
        response = ""
        
        vibe, mission = parse_gemini_response(response)
        
        assert vibe == ""
        assert mission == ""
    
    def test_parse_case_insensitive(self):
        """Test that parsing is case-insensitive for VIBE and MISSION."""
        response = """vibe: lowercase vibe
mission: lowercase mission"""
        
        vibe, mission = parse_gemini_response(response)
        
        assert vibe == "lowercase vibe"
        assert mission == "lowercase mission"


class TestMissionIDGeneration:
    """Test mission ID creation."""
    
    def test_mission_id_format(self):
        """Test that mission IDs have correct format."""
        mission_id = create_mission_id("WALK", "Document structural geometric features on foot")
        
        assert mission_id.startswith("WALK [")
        assert mission_id.endswith("...")
        assert "Document" in mission_id
        assert mission_id.count("[") == 1
        assert mission_id.count("]") == 1
    
    def test_mission_id_uniqueness(self):
        """Test that multiple calls generate different IDs (due to random hash)."""
        ids = [create_mission_id("EAT", "Test mission") for _ in range(10)]
        
        # Should have at least 8 unique IDs out of 10 (high probability)
        assert len(set(ids)) >= 8
    
    def test_mission_id_action_type_preserved(self):
        """Test that action type is preserved in ID."""
        for action in ["WALK", "EAT", "CHILL"]:
            mission_id = create_mission_id(action, "Test mission")
            assert mission_id.startswith(f"{action} [")


class TestMissionStructureValidation:
    """Test validation of mission dictionary structure."""
    
    def test_valid_mission_structure(self):
        """Test that valid mission passes validation."""
        mission = {
            "label": "WALK [1234]: Document...",
            "mood": "WALK",
            "vibe": "URBAN ARCHITECTURE MATRIX",
            "mission": "Document the geometry of the street",
            "legendary": False,
            "ai_generated": False
        }
        
        assert validate_mission_structure(mission) is True
    
    def test_missing_required_field(self):
        """Test that missing fields cause validation to fail."""
        mission = {
            "label": "WALK [1234]: Document...",
            "mood": "WALK",
            # missing "vibe"
            "mission": "Document the geometry",
            "legendary": False,
            "ai_generated": False
        }
        
        assert validate_mission_structure(mission) is False
    
    def test_extra_fields_allowed(self):
        """Test that extra fields don't invalidate structure."""
        mission = {
            "label": "EAT [5678]: Eat...",
            "mood": "EAT",
            "vibe": "CULINARY MATRIX",
            "mission": "Find a fish market",
            "legendary": True,
            "ai_generated": True,
            "extra_field": "allowed"
        }
        
        assert validate_mission_structure(mission) is True


class TestMissionCounting:
    """Test counting missions by type."""
    
    def test_count_missions_by_type(self):
        """Test counting missions by action type."""
        itinerary = [
            {"mood": "WALK", "ai_generated": False},
            {"mood": "WALK", "ai_generated": True},
            {"mood": "EAT", "ai_generated": False},
            {"mood": "CHILL", "ai_generated": True},
            {"mood": "CHILL", "ai_generated": False},
        ]
        
        counts = count_missions_by_type(itinerary)
        
        assert counts["WALK"] == 2
        assert counts["EAT"] == 1
        assert counts["CHILL"] == 2
    
    def test_count_missions_empty_itinerary(self):
        """Test counting on empty itinerary."""
        counts = count_missions_by_type([])
        
        assert counts["WALK"] == 0
        assert counts["EAT"] == 0
        assert counts["CHILL"] == 0
    
    def test_count_ai_generated(self):
        """Test counting AI-generated missions."""
        itinerary = [
            {"ai_generated": True},
            {"ai_generated": False},
            {"ai_generated": True},
            {"ai_generated": True},
        ]
        
        count = count_ai_generated(itinerary)
        
        assert count == 3
    
    def test_count_ai_generated_empty(self):
        """Test counting on empty itinerary."""
        count = count_ai_generated([])
        
        assert count == 0


class TestDietaryConstraints:
    """Test dietary constraint validation."""
    
    def test_compliant_mission(self):
        """Test that pescatarian-compliant mission passes."""
        mission = "Find a fresh fish market and sample the local catch"
        
        assert validate_pescatarian_dietary_constraints(mission) is True
    
    def test_mission_with_avocado(self):
        """Test that mission with avocado fails."""
        mission = "Find a cafe that serves fresh avocado toast"
        
        assert validate_pescatarian_dietary_constraints(mission) is False
    
    def test_mission_with_beef(self):
        """Test that mission with beef fails."""
        mission = "Locate a restaurant serving prime beef steaks"
        
        assert validate_pescatarian_dietary_constraints(mission) is False
    
    def test_mission_with_chicken(self):
        """Test that mission with chicken fails."""
        mission = "Try the roasted chicken at the market"
        
        assert validate_pescatarian_dietary_constraints(mission) is False
    
    def test_mission_case_insensitive(self):
        """Test that constraint checking is case-insensitive."""
        mission = "Avoid AVOCADO and BEEF products"
        
        assert validate_pescatarian_dietary_constraints(mission) is False
    
    def test_pescatarian_compliant_seafood(self):
        """Test that pescatarian seafood is allowed."""
        mission = "Sample the local shrimp and oyster selection"
        
        assert validate_pescatarian_dietary_constraints(mission) is True


class TestMissionSummaryStats:
    """Test summary statistics generation."""
    
    def test_summary_stats_full_itinerary(self):
        """Test stats on a complete itinerary."""
        itinerary = [
            {"mood": "WALK", "ai_generated": True},
            {"mood": "WALK", "ai_generated": False},
            {"mood": "EAT", "ai_generated": False},
            {"mood": "CHILL", "ai_generated": True},
        ]
        
        stats = get_mission_summary_stats(itinerary)
        
        assert stats["total_stops"] == 4
        assert stats["walk_count"] == 2
        assert stats["eat_count"] == 1
        assert stats["chill_count"] == 1
        assert stats["ai_generated_count"] == 2
        assert stats["local_generated_count"] == 2
    
    def test_summary_stats_empty_itinerary(self):
        """Test stats on empty itinerary."""
        stats = get_mission_summary_stats([])
        
        assert stats["total_stops"] == 0
        assert stats["walk_count"] == 0
        assert stats["eat_count"] == 0
        assert stats["chill_count"] == 0
        assert stats["ai_generated_count"] == 0
        assert stats["local_generated_count"] == 0
    
    def test_summary_stats_all_ai_generated(self):
        """Test stats when all missions are AI-generated."""
        itinerary = [
            {"mood": "WALK", "ai_generated": True},
            {"mood": "EAT", "ai_generated": True},
        ]
        
        stats = get_mission_summary_stats(itinerary)
        
        assert stats["ai_generated_count"] == 2
        assert stats["local_generated_count"] == 0


class TestConstantsConfiguration:
    """Test that configuration constants are properly defined."""
    
    def test_cyber_prefixes_not_empty(self):
        """Test that cyber prefixes are defined."""
        assert len(CYBER_PREFIXES) > 0
        assert all(isinstance(p, str) for p in CYBER_PREFIXES)
    
    def test_cyber_atmospheres_complete(self):
        """Test that cyber atmospheres cover all action types."""
        assert "WALK" in CYBER_ATMOSPHERES
        assert "EAT" in CYBER_ATMOSPHERES
        assert "CHILL" in CYBER_ATMOSPHERES
        
        for action_type in CYBER_ATMOSPHERES:
            assert len(CYBER_ATMOSPHERES[action_type]) > 0
            assert all(isinstance(a, str) for a in CYBER_ATMOSPHERES[action_type])
    
    def test_default_vibes_complete(self):
        """Test that default vibes exist for all action types."""
        assert "WALK" in DEFAULT_BASE_VIBES
        assert "EAT" in DEFAULT_BASE_VIBES
        assert "CHILL" in DEFAULT_BASE_VIBES
    
    def test_default_missions_complete(self):
        """Test that default missions exist for all action types."""
        assert "WALK" in DEFAULT_MISSIONS
        assert "EAT" in DEFAULT_MISSIONS
        assert "CHILL" in DEFAULT_MISSIONS
        
        for action_type in DEFAULT_MISSIONS:
            assert len(DEFAULT_MISSIONS[action_type]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
