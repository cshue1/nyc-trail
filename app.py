import streamlit as st
import random
import json
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Load environment variables from .env if available
load_dotenv()

# ==============================================================================
# INITIALIZE APP ENGINE & SURFACE THEME CONFIGURATIONS
# ==============================================================================
st.set_page_config(page_title="NYC TRAIL PLANNER", page_icon="🤠", layout="centered")

st.title("== NYC TRAIL PLANNER v16.0 ==")

# Initialize Session State Keys
if "started" not in st.session_state: st.session_state.started = False
if "current_hood" not in st.session_state: st.session_state.current_hood = None
if "itinerary" not in st.session_state: st.session_state.itinerary = []
if "order_list" not in st.session_state: st.session_state.order_list = []
if "show_debrief" not in st.session_state: st.session_state.show_debrief = False
if "used_missions" not in st.session_state: st.session_state.used_missions = []
if "ai_active_model" not in st.session_state: st.session_state.ai_active_model = None

# ==============================================================================
# DASHBOARD SYSTEM CONTROL HEADER
# ==============================================================================
col_info, col_toggle = st.columns([2, 1])
with col_info:
    with st.popover("ℹ️ VIEW SYSTEM WORKFLOW"):
        st.markdown("### == AUTOMATED BACKEND LOOP ==")
        st.write("🤖 **1. STACK:** Drop random location coordinates.")
        st.write("🧠 **2. ENHANCEMENT:** Dedicated Gemini Engine optimizes text strings instantly.")
        st.write("📸 **3. CAPTURE:** Document field entries on camera.")
        st.write("📊 **4. TRANSMIT:** Appends telemetry rows directly to Google Sheets.")

with col_toggle:
    demo_mode = st.toggle("🛠️ DEMO MODE", value=False)

if demo_mode:
    st.markdown("**⚠️ SANDBOX MATRIX ENGAGED: TRANSMISSIONS DEACTIVATED ⚠️**")

st.write("--------------------------------------------------")

# ==============================================================================
# INITIALIZE GOOGLE GENAI CLIENT CORE LINK (ONCE PER SESSION)
# ==============================================================================
if st.session_state.ai_active_model is None:
    gemini_api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    print("\n--- [DEBUG SYSTEM INITIALIZATION] ---")
    print(f"Checking for API Key presence: {'FOUND' if gemini_api_key else 'MISSING'}")
    
    if gemini_api_key:
        try:
            test_client = genai.Client(api_key=gemini_api_key)
            # Tier targets checking loop
            for model_name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro"]:
                try:
                    print(f"Testing connectivity validation ping on: {model_name}")
                    test_client.models.generate_content(
                        model=model_name,
                        contents="Ping",
                        config=types.GenerateContentConfig(max_output_tokens=5)
                    )
                    st.session_state.ai_active_model = model_name
                    print(f"Successfully locked active engine: {model_name}")
                    break
                except Exception as ping_err:
                    print(f"Ping failed for {model_name}: {ping_err}")
                    continue
            if not st.session_state.ai_active_model:
                st.session_state.ai_active_model = "OFFLINE"
        except Exception as e:
            st.sidebar.warning(f"⚠️ SDK Core configuration failed: {str(e)}")
            print(f"SDK Critical Core configuration exception raised: {e}")
            st.session_state.ai_active_model = "OFFLINE"
    else:
        st.session_state.ai_active_model = "OFFLINE"
    print("---------------------------------------\n")

# Display Engine Link Status in Sidebar
if st.session_state.ai_active_model and st.session_state.ai_active_model != "OFFLINE":
    st.sidebar.success(f"✅ {st.session_state.ai_active_model} - Mission enhancement active")
else:
    st.sidebar.info("ℹ️ Gemini API not configured - using local mission generation")

# Load JSON Data rations
@st.cache_data
def load_adventure_deck():
    try:
        with open("adventures.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("CRITICAL ERROR: MISSING ADVENTURES.JSON SOURCE DECK.")
        return {}

adventure_pool = load_adventure_deck()

cyber_prefixes = ["TACTICAL RECONNAISSANCE PROTOCOL", "SILENT OBJECTIVE VECTOR", "CRITICAL METRIC HUNT", "MINIMALIST FRAMING COGNITION", "GEOMETRIC MATRIX TRACKER"]
cyber_atmospheres = {
    "WALK": ["TRACKING ON FOOT ALONG THE REINFORCED PERIMETERS OF", "NAVIGATING THE HIGH-CONTRAST URBAN CORRIDORS OF", "EXECUTING MOVEMENT DRILLS DOWN THE BLOCKS OF"],
    "EAT": ["SOURCING SUSTENANCE NANO-COUNTER TILES INSIDE", "RECONNOITERING KITCHEN EMISSION VENTS IN", "LOCATING A SEAFOOD OR GRAIN REFUEL STATION WITHIN"],
    "CHILL": ["LOCATING A STATIONARY REST PROFILE DECK AMIDST", "ESTABLISHING A STATIC OBSERVATION SECTOR IN", "ANCHORING POSITION TO ASSIMILATE THE AMBIENT GRID OF"]
}

# ==============================================================================
# 🤖 PYDANTIC SCHEMA DEFINITION FOR GEMINI OUTPUTS
# ==============================================================================
class EnhancedMission(BaseModel):
    vibe: str = Field(description="The exact text for the VIBE tag. Keep it strictly atmospheric.")
    mission: str = Field(description="The exact text for the MISSION tag. Keep it strictly actionable.")

# ==============================================================================
# 🤖 GEMINI MISSION ENHANCEMENT ENGINE (NEW CLIENT IMPLEMENTATION)
# ==============================================================================
# Removed @st.cache_data - We want this to run fresh every time and bypass Streamlit's cache bloat
def enhance_mission_with_gemini(neighborhood, action_type, base_vibe, base_mission, active_model_name, previously_used_missions):
    """
    Enhance mission description using modern Google GenAI SDK Client structure and Pydantic schemas.
    """
    print("\n--- [CONSOLE LOG: GEMINI ENGINE CALL] ---")
    print(f"Target Neighborhood: {neighborhood} | Action: {action_type}")
    
    # Format the exclusion list so Gemini knows exactly what to avoid
    exclusion_text = ""
    if previously_used_missions:
        exclusion_text = "\nCRITICAL EXCLUSION PROTOCOL: DO NOT generate anything similar to these previously completed missions:\n"
        exclusion_text += "\n".join(f"- {m}" for m in previously_used_missions)

    system_prompt = f"""You are an advanced content-enhancement engine for a text-adventure game set in NYC. 
Match the tone of a high-tech tactical terminal or cyberpunk operative deck.

CRITICAL GEOGRAPHIC REALISM PROTOCOLS:
- The target neighborhood sector is: {neighborhood} (New York City).
- Every mission generated MUST be physically true, possible, and logical for the actual geography, architecture, layout, and atmosphere of {neighborhood}.

CRITICAL ACTION ENFORCEMENT PROTOCOLS:
- Current Strategy Component Action Category is: {action_type}. Your generation MUST strictly focus on this specific type of task.
- If the category is EAT, the assignment MUST focus on dining, finding fish/vegetarian snacks, kitchen counters, or food markets.
- If the category is WALK, the assignment MUST focus on walking, navigating blocks, footprints, and movement photography.
- If the category is CHILL, the assignment MUST focus on sitting, resting, pausing, absorbing atmosphere, and stationary observation.
- STRICT DIETARY BOUNDARY: If food is referenced, descriptions MUST be strictly pescatarian and COMPLETELY AVOCADO-FREE.
- CRITICAL RESTRICTION: Do NOT name or recommend real commercial storefronts, specific shops, or chain brands. Keep spaces generalized to architectural textures.{exclusion_text}"""
    
    user_prompt = f"""Enhance this configuration profile:
NEIGHBORHOOD: {neighborhood}
ACTION CATEGORY: {action_type}
BASE VIBE BLUEPRINT: {base_vibe}
BASE MISSION BLUEPRINT: {base_mission}"""
    
    try:
        gemini_api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=gemini_api_key)
        
        print(f"Sending request payload to Google Cloud Core using {active_model_name}...")
        response = client.models.generate_content(
            model=active_model_name,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json", # Forces JSON output
                response_schema=EnhancedMission,       # Maps to our Pydantic class
            )
        )
        
        # Parse the guaranteed JSON response
        data = json.loads(response.text)
        extracted_vibe = data.get("vibe", "").strip()
        extracted_mission = data.get("mission", "").strip()
        
        if extracted_vibe and extracted_mission:
            print("Successfully compiled and parsed AI content tokens.")
            return extracted_vibe, extracted_mission, True
        else:
            print("Parsing error: Keys missing from JSON response.")
            
    except Exception as api_err:
        st.sidebar.error(f"📡 API Engine Intercept: {str(api_err)}")
        print(f"Critical Exception caught during API generation loop: {api_err}")
        
    print("Executing automatic handoff back to local asset array generation loops.")
    print("-------------------------------------------\n")
    return base_vibe, base_mission, False

# ==============================================================================
# 🧠 PROTECTED STATE CALLBACK CORES
# ==============================================================================
def trigger_action_callback(action_type):
    overrides = adventure_pool.get("special_overrides", {})
    
    current_hood = st.session_state.get("current_hood")
    has_override = current_hood in overrides and "packages" in overrides[current_hood] if current_hood else False
    
    is_legendary = False
    base_vibe = ""
    base_mission = ""
    
    if has_override:
        chosen_package = random.choice(overrides[current_hood]["packages"])
        base_vibe = chosen_package["vibe"]
        valid_missions = chosen_package.get(action_type, [])
        if not valid_missions:
            valid_missions = chosen_package.get("missions", ["Explore local layout structures."])
        pool = valid_missions
        is_legendary = True
    else:
        if action_type == "EAT":
            base_vibe = "CULINARY INTERCEPT MATRIX // AVOCADO-FREE PESTAX PROFILE"
            pool = adventure_pool.get("EAT", {}).get("missions", ["Locate a marketplace counter. Secure shared plates. Zero land-meat broths, zero avocados."])
        elif action_type == "CHILL":
            base_vibe = "STATIC STATIONARY ANCHOR // ATMOSPHERIC CALIBRATION"
            pool = adventure_pool.get("CHILL", {}).get("missions", ["Halt transit vector. Identify a step or architectural ledge to sit silently."])
        else:  # WALK
            base_vibe = random.choice(adventure_pool.get("vibes", ["URBAN ARCHITECTURE MATRIX"]))
            pool = adventure_pool.get("WALK", {}).get("missions", ["Document structural geometric features on foot."])

    # Enforce Strict Deduplication Filter Check against the local pool
    unused_local = [m for m in pool if m not in st.session_state.used_missions]
    
    is_forced_duplicate = False
    if unused_local:
        base_mission = random.choice(unused_local)
    else:
        base_mission = random.choice(pool)
        is_forced_duplicate = True
    
    ai_live = st.session_state.ai_active_model and st.session_state.ai_active_model != "OFFLINE"
    is_ai_generated = False
    final_vibe = base_vibe
    final_mission = base_mission
    
    # Try to enhance mission with Gemini SDK
    if ai_live and current_hood:
        modified_base = base_mission
        if is_forced_duplicate:
            modified_base += " (Instruction: Pivot alternative execution style to focus on structural macro-angles, lighting variations, or micro-textures)."
            
        final_vibe, final_mission, is_ai_generated = enhance_mission_with_gemini(
            current_hood, 
            action_type, 
            base_vibe, 
            modified_base,
            st.session_state.ai_active_model,
            st.session_state.used_missions # Pass the actual list of previous AI outputs
        )

    # If AI failed or is offline, build the local string
    if not is_ai_generated:
        prefix = random.choice(cyber_prefixes)
        atmosphere = random.choice(cyber_atmospheres[action_type])
        final_vibe = f"LOCAL FALLBACK // {base_vibe}"
        
        hood_display = current_hood if current_hood else "CURRENT SECTOR"
        if is_forced_duplicate:
            final_mission = f"[{prefix} RE-ROUTE ACTIVE]: ALTERNATE PHASE VECTOR. {atmosphere} {hood_display}. Pivot your objective strategy to focus on nearby structural textures, angles, and micro-details while completing: {base_mission}"
        else:
            final_mission = f"[{prefix} ENGAGED]: {atmosphere} {hood_display}. {base_mission}"

    # Track the FINAL mission string in memory so it can be passed to the AI exclusion list next time
    st.session_state.used_missions.append(final_mission)

    random_hash = random.randint(1000, 9999)
    unique_id = f"{action_type} [{random_hash}]: {final_mission[:20]}..."

    st.session_state.itinerary.append({
        "label": unique_id,
        "mood": action_type,
        "vibe": final_vibe,
        "mission": final_mission,
        "legendary": is_legendary,
        "ai_generated": is_ai_generated
    })
    st.session_state.order_list.append(unique_id)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

# ==============================================================================
# MAIN PAGE ROUTING RENDER LOOPS
# ==============================================================================
if not st.session_state.started:
    st.write("READY TO ASSIGN YOUR REGIONAL DROP SECTOR?")
    if st.button("LAUNCH TRAIL MATRIX"):
        if adventure_pool and "neighborhoods" in adventure_pool:
            st.session_state.current_hood = random.choice(adventure_pool["neighborhoods"])
            st.session_state.started = True
            st.session_state.itinerary = []
            st.session_state.order_list = []
            st.session_state.show_debrief = False
            st.session_state.used_missions = []
            st.rerun()
else:
    st.markdown(f"### [DROPPED SECTOR]: {st.session_state.current_hood}")
    
    if not st.session_state.show_debrief:
        st.write("CHOOSE YOUR STRATEGY FOR THE NEXT STOP IN THIS AREA:")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.button("➕ ADD WALK", on_click=trigger_action_callback, args=["WALK"])
        with col2:
            st.button("➕ ADD EAT", on_click=trigger_action_callback, args=["EAT"])
        with col3:
            st.button("➕ ADD CHILL", on_click=trigger_action_callback, args=["CHILL"])

    # --- STEP 3: INTERACTIVE TIMELINE REORDERING ---
    if st.session_state.itinerary and not st.session_state.show_debrief:
        st.write("--------------------------------------------------")
        st.write("🔧 REORDER OR REMOVE STOPS FROM THE TIMELINE:")
        
        valid_itinerary_labels = [item["label"] for item in st.session_state.itinerary]
        current_selection = [lbl for lbl in st.session_state.order_list if lbl in valid_itinerary_labels]
        
        sorted_order = st.multiselect(
            "Drag, drop, or remove steps to set your sequence metric configuration:",
            options=valid_itinerary_labels,
            default=current_selection
        )
        st.session_state.order_list = list(dict.fromkeys(sorted_order))

    # --- STEP 4: DISPLAY NATIVE ADAPTIVE BLOCK MATRIX ---
    if st.session_state.itinerary and not st.session_state.show_debrief:
        st.markdown("### == TARGET DAY ITINERARY == ")
        itinerary_map = {item["label"]: item for item in st.session_state.itinerary}
        
        for index, label in enumerate(st.session_state.order_list):
            item = itinerary_map.get(label)
            if item:
                if demo_mode:
                    alert_prefix = " [DEMO SIMULATION]"
                elif item.get("ai_generated", False):
                    alert_prefix = " 🤖 [AI CLOUD ENHANCED]"
                else:
                    alert_prefix = " [LOCAL CREATIVE]"
                
                with st.container(border=True):
                    st.markdown(f"**STOP {index + 1}: {item['mood']}{alert_prefix}**")
                    st.write(f"**[ENVIRONMENT VIBE]:** {item['vibe']}")
                    st.markdown("---")
                    st.write(f"**[MISSION]:** {item['mission']}")

        # --- DIAGNOSTIC ANALYTICS EXPANDER ---
        with st.expander("📊 STATS FOR NERDS (DIAGNOSTIC ANALYTICS)"):
            total_stops = len(st.session_state.order_list)
            active_items = [itinerary_map[l] for l in st.session_state.order_list if l in itinerary_map]
            
            walk_count = sum(1 for x in active_items if x["mood"] == "WALK")
            eat_count = sum(1 for x in active_items if x["mood"] == "EAT")
            chill_count = sum(1 for x in active_items if x["mood"] == "CHILL")
            ai_count = sum(1 for x in active_items if x.get("ai_generated", False))
            
            st.markdown(f"**⚡ TOTAL TIMELINE ENTRIES:** {total_stops} stops configured")
            st.text(f"WALK  [{'█' * walk_count}{'░' * (total_stops-walk_count)}] {walk_count} allocations")
            st.text(f"EAT   [{'█' * eat_count}{'░' * (total_stops-eat_count)}] {eat_count} allocations")
            st.text(f"CHILL [{'█' * chill_count}{'░' * (total_stops-chill_count)}] {chill_count} allocations")
            
            st.markdown("---")
            st.write("**🛡️ OPERATIONAL INTEGRITY SCORE:**")
            ai_active_flag = st.session_state.ai_active_model and st.session_state.ai_active_model != "OFFLINE"
            st.write(f"- Running AI Cloud Core: **{f'CONNECTED ({st.session_state.ai_active_model})' if ai_active_flag else 'OFFLINE (FALLBACK EMBEDDED)'}**")
            st.write(f"- Active AI Generations: **{ai_count} modules loaded**")
            st.write(f"- Unique Memory Tracking Pool Size: **{len(st.session_state.used_missions)} keys registered**")
            st.write(f"- Cloud Transmission Safety Block: **{'LIVE TO LEDGER' if not demo_mode else 'ENGAGED'}**")

        st.write("--------------------------------------------------")
        if st.button("🏁 END DAY & OPEN MISSION DEBRIEF"):
            st.session_state.show_debrief = True
            st.rerun()

# ==============================================================================
# STEP 5: MISSION DEBRIEF & CONDITIONAL DATA SAVING
# ==============================================================================
if st.session_state.show_debrief:
    st.markdown("### == FIELD MISSION DEBRIEF ==")
    st.write("RECORD CURRENT TRACKING STATS TO YOUR SHARABLE DATABASE LEDGER:")
    st.markdown("---")
    
    itinerary_map = {item["label"]: item for item in st.session_state.itinerary}
    current_date = datetime.now().strftime("%Y-%m-%d")
    new_rows = []
    
    filtered_order_list = list(dict.fromkeys(st.session_state.order_list))
    
    for index, label in enumerate(filtered_order_list):
        item = itinerary_map.get(label)
        if item:
            st.markdown(f"### STOP {index + 1}: {item['mood']}")
            st.write(f"**Vibe:** {item['vibe']}")
            st.write(f"**Mission:** {item['mission']}")
            
            status = st.radio(f"Stop {index + 1} Status:", ["COMPLETED", "ABANDONED/SKIPPED"], key=f"status_widget_{label}")
            notes = st.text_area(f"Quick Notes (Stop {index + 1}):", placeholder="Notes...", key=f"notes_widget_{label}")
            st.markdown("---")
            
            new_rows.append({
                "Date": current_date,
                "Neighborhood": st.session_state.current_hood,
                "Stop_Number": str(index + 1),
                "Mood": item['mood'],
                "Vibe": item['vibe'],
                "Mission": item['mission'],
                "Status": status,
                "Notes": notes
            })
    
    if st.button("⚡ APPEND CAMPAIGN TO SHARED CLOUD SHEET"):
        if conn is not None and not demo_mode and new_rows:
            try:
                existing_df = conn.read()
                if existing_df is not None and not existing_df.empty:
                    existing_df['Stop_Number'] = existing_df['Stop_Number'].astype(str)
                    fresh_df = pd.DataFrame(new_rows)
                    updated_df = pd.concat([existing_df, fresh_df], ignore_index=True)
                else:
                    updated_df = pd.DataFrame(new_rows)
                    
                conn.update(data=updated_df)
                st.success("SUCCESS: Telemetry committed to Google Cloud ledger!")
            except Exception as e:
                st.error(f"TRANSMISSION INTERRUPTED: {e}")
        else:
            st.warning("Sheets connection unavailable or Demo Mode active.")
            
    if st.button("⬅️ RETURN TO TIMELINE EDITING"):
        st.session_state.show_debrief = False
        st.rerun()

if st.session_state.started:
    if st.button("ABANDON MISSION & RESET MATRIX"):
        st.session_state.started = False
        st.session_state.current_hood = None
        st.session_state.itinerary = []
        st.session_state.order_list = []
        st.session_state.show_debrief = False
        st.session_state.used_missions = []
        st.rerun()