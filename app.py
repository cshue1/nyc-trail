import streamlit as st
import random
import json
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests

# ==============================================================================
# INITIALIZE APP ENGINE & SURFACE THEME CONFIGURATIONS
# ==============================================================================
st.set_page_config(page_title="NYC TRAIL PLANNER", page_icon="🤠", layout="centered")

st.title("== NYC TRAIL PLANNER v16.0 ==")

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
# INITIALIZE HIGH-SPEED GOOGLE GEMINI CORE LINK
# ==============================================================================
ai_enabled = False
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    ai_enabled = True

# Load JSON Data rations
try:
    with open("adventures.json", "r") as file:
        adventure_pool = json.load(file)
except FileNotFoundError:
    st.error("CRITICAL ERROR: MISSING ADVENTURES.JSON SOURCE DECK.")
    adventure_pool = {}

cyber_prefixes = ["TACTICAL RECONNAISSANCE PROTOCOL", "SILENT OBJECTIVE VECTOR", "CRITICAL METRIC HUNT", "MINIMALIST FRAMING COGNITION", "GEOMETRIC MATRIX TRACKER"]
cyber_atmospheres = {
    "WALK": ["TRACKING ON FOOT ALONG THE REINFORCED PERIMETERS OF", "NAVIGATING THE HIGH-CONTRAST URBAN CORRIDORS OF", "EXECUTING MOVEMENT DRILLS DOWN THE BLOCKS OF"],
    "EAT": ["SOURCING SUSTENANCE NANO-COUNTER TILES INSIDE", "RECONNOITERING KITCHEN EMISSION VENTS IN", "LOCATING A SEAFOOD OR GRAIN REFUEL STATION WITHIN"],
    "CHILL": ["LOCATING A STATIONARY REST PROFILE DECK AMIDST", "ESTABLISHING A STATIC OBSERVATION SECTOR IN", "ANCHORING POSITION TO ASSIMILATE THE AMBIENT GRID OF"]
}

if "started" not in st.session_state: st.session_state.started = False
if "current_hood" not in st.session_state: st.session_state.current_hood = None
if "itinerary" not in st.session_state: st.session_state.itinerary = []
if "order_list" not in st.session_state: st.session_state.order_list = []
if "show_debrief" not in st.session_state: st.session_state.show_debrief = False
if "used_missions" not in st.session_state: st.session_state.used_missions = []

# ==============================================================================
# 🧠 PROTECTED STATE CALLBACK CORES (STRICT DICTIONARY ROUTING POOLS)
# ==============================================================================
def trigger_action_callback(action_type):
    overrides = adventure_pool.get("special_overrides", {})
    has_override = st.session_state.current_hood in overrides and "packages" in overrides[st.session_state.current_hood]
    
    is_legendary = False
    base_vibe = ""
    base_mission = ""
    
    if has_override:
        chosen_package = random.choice(overrides[st.session_state.current_hood]["packages"])
        base_vibe = chosen_package["vibe"]
        # ROUTING SAFETY LOCKED: Looks for specific category arrays inside your local override pools
        valid_missions = chosen_package.get(action_type, [])
        if not valid_missions:
            valid_missions = chosen_package.get("missions", ["Explore local layout structures."])
        
        unused_override = [m for m in valid_missions if m not in st.session_state.used_missions]
        base_mission = random.choice(unused_override if unused_override else valid_missions)
        is_legendary = True
    else:
        # ROUTING SAFETY LOCKED: Pulls directly from standard isolated keys, avoiding keyword matching flaws
        if action_type == "EAT":
            base_vibe = "CULINARY INTERCEPT MATRIX // AVOCADO-FREE PESCATARIAN PROFILE"
            pool = adventure_pool.get("EAT", {}).get("missions", ["Locate a marketplace counter. Secure shared plates. Zero land-meat broths, zero avocados."])
        elif action_type == "CHILL":
            base_vibe = "STATIC STATIONARY ANCHOR // ATMOSPHERIC CALIBRATION"
            pool = adventure_pool.get("CHILL", {}).get("missions", ["Halt transit vector. Identify a step or architectural ledge to sit silently."])
        else:  # WALK
            base_vibe = random.choice(adventure_pool.get("vibes", ["URBAN ARCHITECTURE MATRIX"]))
            pool = adventure_pool.get("WALK", {}).get("missions", ["Document structural geometric features on foot."])
            
        unused = [m for m in pool if m not in st.session_state.used_missions]
        base_mission = random.choice(unused if unused else pool)

    st.session_state.used_missions.append(base_mission)
    
    vibe = base_vibe
    mission = base_mission
    is_ai_generated = False
    
    if ai_enabled:
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Enhance this configuration profile:\nNEIGHBORHOOD: {st.session_state.current_hood}\nACTION CATEGORY: {action_type}\nBASE VIBE BLUEPRINT: {base_vibe}\nBASE MISSION BLUEPRINT: {base_mission}"
                    }]
                }],
                "systemInstruction": {
                    "parts": [{
                        "text": f"""You are an advanced content-enhancement engine for a text-adventure game set in NYC. 
                        Match the tone of a high-tech tactical terminal or cyberpunk operative deck.
                        
                        CRITICAL GEOGRAPHIC REALISM PROTOCOLS:
                        - The target neighborhood sector is: {st.session_state.current_hood} (New York City).
                        - Every mission generated MUST be physically true, possible, and logical for the actual geography, architecture, layout, and atmosphere of {st.session_state.current_hood}.
                        
                        CRITICAL ACTION ENFORCEMENT PROTOCOLS:
                        - Current Strategy Component Action Category is: {action_type}. Your generation MUST strictly focus on this specific type of task.
                        - If the category is EAT, the assignment MUST focus on dining, finding fish/vegetarian snacks, kitchen counters, or food markets.
                        - If the category is WALK, the assignment MUST focus on walking, navigating blocks, footprints, and movement photography.
                        - If the category is CHILL, the assignment MUST focus on sitting, resting, pausing, absorbing atmosphere, and stationary observation.
                        - STRICT DIETARY BOUNDARY: If food is referenced, descriptions MUST be strictly pescatarian and COMPLETELY AVOCADO-FREE.
                        - CRITICAL RESTRICTION: Do NOT name or recommend real commercial storefronts, specific shops, or chain brands. Keep spaces generalized to architectural textures.
                        
                        Output format must be exactly this strict raw text structure with no conversational chatter, asterisks, or markdown bold symbols:
                        VIBE: [Text here]
                        MISSION: [Text here]"""
                    }]
                },
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 250
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=6)
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                extracted_vibe = ""
                extracted_mission = ""
                for line in ai_response.split("\n"):
                    clean_line = line.replace("**", "").strip()
                    if clean_line.upper().startswith("VIBE:"):
                        extracted_vibe = clean_line[5:].strip()
                    elif clean_line.upper().startswith("MISSION:"):
                        extracted_mission = clean_line[8:].strip()
                
                if extracted_vibe and extracted_mission:
                    vibe = extracted_vibe
                    mission = extracted_mission
                    is_ai_generated = True
        except Exception as e:
            st.error(f"⚠️ INTERNAL API DIAGNOSTIC EXCEPTION: {e}")

    if not is_ai_generated:
        prefix = random.choice(cyber_prefixes)
        atmosphere = random.choice(cyber_atmospheres[action_type])
        vibe = f"LOCAL FALLBACK // {base_vibe}"
        
        is_duplicate = any(item["mission"].endswith(base_mission) for item in st.session_state.itinerary)
        if is_duplicate:
            mission = f"[{prefix} RE-ROUTE ACTIVE]: ALTERNATE PHASE VECTOR. {atmosphere} {st.session_state.current_hood}. Pivot your objective strategy to focus on nearby architectural textures, angles, and micro-details while completing: {base_mission}"
        else:
            mission = f"[{prefix} ENGAGED]: {atmosphere} {st.session_state.current_hood}. {base_mission}"

    random_hash = random.randint(1000, 9999)
    unique_id = f"{action_type} [{random_hash}]: {mission[:20]}..."

    st.session_state.itinerary.append({
        "label": unique_id,
        "mood": action_type,
        "vibe": vibe,
        "mission": mission,
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
        sorted_order = st.multiselect(
            "Drag, drop, or remove steps to set your sequence metric configuration:",
            options=[item["label"] for item in st.session_state.itinerary],
            default=st.session_state.order_list
        )
        st.session_state.order_list = sorted_order

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

        # --- DIAGNOSTIC ANALYTICS EXPANDER ("STATS FOR NERDS") ---
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
            st.write(f"- Running AI Cloud Core: **{'CONNECTED (GEMINI 2.5 CORE)' if ai_enabled else 'OFFLINE (FALLBACK EMBEDDED)'}**")
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
    
    for index, label in enumerate(st.session_state.order_list):
        item = itinerary_map.get(label)
        if item:
            st.markdown(f"### STOP {index + 1}: {item['mood']}")
            st.write(f"**Vibe:** {item['vibe']}")
            st.write(f"**Mission:** {item['mission']}")
            
            status = st.radio(f"Stop {index + 1} Status:", ["COMPLETED", "ABANDONED/SKIPPED"], key=f"status_{index}")
            notes = st.text_area(f"Quick Notes (Stop {index + 1}):", placeholder="Notes...", key=f"notes_{index}")
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
        if conn is not None and not demo_mode:
            try:
                existing_df = conn.read(ttl=0)
                existing_df['Stop_Number'] = existing_df['Stop_Number'].astype(str)
                fresh_df = pd.DataFrame(new_rows)
                updated_df = pd.concat([existing_df, fresh_df], ignore_index=True)
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