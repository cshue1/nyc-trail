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

st.title("== NYC TRAIL PLANNER v8.0 ==")

# ==============================================================================
# DASHBOARD SYSTEM CONTROL HEADER
# ==============================================================================
col_info, col_toggle = st.columns([2, 1])
with col_info:
    with st.popover("ℹ️ VIEW SYSTEM WORKFLOW"):
        st.markdown("### == AUTOMATED BACKEND LOOP ==")
        st.write("🤖 **1. STACK:** Drop random location coordinates and load objective matrices.")
        st.write("🧠 **2. ENHANCEMENT:** Hugging Face serverless logic parses your local JSON blueprint, amping its creative profile.")
        st.write("📸 **3. CAPTURE:** Document field entries natively on your camera roll.")
        st.write("📊 **4. TRANSMIT:** Appends mission telemetry rows directly to your shared Google Sheet.")

with col_toggle:
    demo_mode = st.toggle("🛠️ DEMO MODE", value=False, help="Blocks Google Sheet streaming updates to simulate sandboxed logs.")

if demo_mode:
    st.markdown("**⚠️ SANDBOX MATRIX ENGAGED: TRANSMISSIONS DEACTIVATED ⚠️**")

st.write("--------------------------------------------------")

# ==============================================================================
# INITIALIZE FREE HUGGING FACE INFERENCE CLIENT
# ==============================================================================
ai_enabled = False
if "HF_API_KEY" in st.secrets:
    HF_API_KEY = st.secrets["HF_API_KEY"]
    # Serverless API endpoint targeting Meta Llama-3 open-source model architecture
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    ai_enabled = True

# Load JSON Data rations
try:
    with open("adventures.json", "r") as file:
        adventure_pool = json.load(file)
except FileNotFoundError:
    st.error("CRITICAL ERROR: MISSING ADVENTURES.JSON SOURCE DECK.")
    adventure_pool = {}

# Local fallback arrays for zero-risk text amplification injections if API keys are missing
cyber_prefixes = ["TACTICAL RECONNAISSANCE PROTOCOL", "SILENT OBJECTIVE VECTOR", "CRITICAL METRIC HUNT", "MINIMALIST FRAMING COGNITION", "GEOMETRIC MATRIX TRACKER"]
cyber_atmospheres = ["UNDER THE CONCRETE SHADOW GRID OF", "TRACKING THROUGH THE LOW-LIGHT SECTOR CORES OF", "NAVIGATING THE HIGH-CONTRAST TEXTURE FIELDS OF", "EXPLORING THE HISTORIC ARCHITECTURAL CHANNELS OF"]

# Initialize unified session layout variables
if "started" not in st.session_state: st.session_state.started = False
if "current_hood" not in st.session_state: st.session_state.current_hood = None
if "itinerary" not in st.session_state: st.session_state.itinerary = []
if "order_list" not in st.session_state: st.session_state.order_list = []
if "show_debrief" not in st.session_state: st.session_state.show_debrief = False
if "active_trigger" not in st.session_state: st.session_state.active_trigger = None

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

# ==============================================================================
# STEP 1: DEPLOY REGIONAL DROP SECTOR
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
            st.session_state.active_trigger = None
            st.rerun()
else:
    st.markdown(f"### [DROPPED SECTOR]: {st.session_state.current_hood}")
    
    overrides = adventure_pool.get("special_overrides", {})
    has_override = st.session_state.current_hood in overrides and "packages" in overrides[st.session_state.current_hood]

    if not st.session_state.show_debrief:
        st.write("CHOOSE YOUR STRATEGY FOR THE NEXT STOP IN THIS AREA:")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("➕ ADD WALK"): st.session_state.active_trigger = "WALK"
        with col2:
            if st.button("➕ ADD EAT"): st.session_state.active_trigger = "EAT"
        with col3:
            if st.button("➕ ADD CHILL"): st.session_state.active_trigger = "CHILL"

        # ==============================================================================
        # STEP 2: STOCHASTIC & AI AMPLIFICATION ENGINE (HYBRID ROUTE)
        # ==============================================================================
        if st.session_state.active_trigger:
            current_action = st.session_state.active_trigger
            is_legendary = False
            is_ai_generated = False
            
            # Base text compilation extraction out of adventures.json structure
            if has_override:
                chosen_package = random.choice(overrides[st.session_state.current_hood]["packages"])
                base_vibe = chosen_package["vibe"]
                base_mission = random.choice(chosen_package["missions"])
                is_legendary = True
            else:
                base_vibe = random.choice(adventure_pool["vibes"])
                base_mission = random.choice(adventure_pool[current_action]["missions"])

            # UI Control Switch Layer
            st.write("---")
            use_ai = st.checkbox("🧠 ENGAGE LIVE HUGGING FACE COGNITION", value=True,
                                 help="When checked, uses an open-source model to rewrite descriptions. Uncheck for instant, local generation.")

            if use_ai and ai_enabled:
                with st.spinner("🧠 GENERATING AI CORE MISSION AMPLIFICATION..."):
                    try:
                        # Structured Llama-3 text instruction parameters
                        prompt_text = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                        You are the advanced content-enhancement engine for an offline retro text adventure game set in NYC called "NYC TRAIL PLANNER".
                        Match the tone of a high-tech tactical terminal or cyberpunk operative deck.
                        STRICT DIETARY BOUNDARY: If food is referenced, descriptions MUST be strictly pescatarian and COMPLETELY AVOCADO-FREE.
                        CRITICAL RESTRICTION: Do NOT name or recommend real-world commercial storefronts or restaurants. Keep spaces generalized to architectural textures (e.g., "a neon counter", "a concrete ledge").
                        Output your response in exactly this strict raw text structure with no extra conversational chatter:
                        VIBE: [Text here]
                        MISSION: [Text here]<|eot_id|><|start_header_id|>user<|end_header_id|>
                        Enhance this setup for the location '{st.session_state.current_hood}' and action '{current_action}'.
                        BASE VIBE BLUEPRINT: {base_vibe}
                        BASE MISSION BLUEPRINT: {base_mission}
                        INSTRUCTIONS: Use this base blueprint purely as an imaginative launching pad. Amp up the flavor text, add rich cinematic atmospheric descriptors, and inject unique narrative objective twists.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

                        payload = {
                            "inputs": prompt_text,
                            "parameters": {"max_new_tokens": 250, "temperature": 0.7, "return_full_text": False}
                        }
                        
                        response = requests.post(API_URL, headers=headers, json=payload)
                        response_data = response.json()
                        
                        if isinstance(response_data, list):
                            output_text = response_data[0]['generated_text']
                        else:
                            output_text = response_data['generated_text']
                        
                        ai_response = output_text.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
                        
                        vibe = base_vibe
                        mission = ai_response
                        for line in ai_response.split("\n"):
                            if line.strip().startswith("VIBE:"): vibe = line.replace("VIBE:", "").strip()
                            if line.strip().startswith("MISSION:"): mission = line.replace("MISSION:", "").strip()
                        
                        is_ai_generated = True
                    except Exception as e:
                        # Immediate safe structural fallback if server tier rate-limits
                        vibe = f"LOCAL AMPLER // {base_vibe}"
                        mission = base_mission
            else:
                # 100% Safe Local programatic extraction if checkbox is cleared
                prefix = random.choice(cyber_prefixes)
                atmosphere = random.choice(cyber_atmospheres)
                vibe = f"{prefix} // {base_vibe}"
                mission = f"[{prefix} ENGAGED]: {atmosphere} {st.session_state.current_hood}. {base_mission}"

            # Build an explicit random fingerprint to prevent matching index label rendering traps
            random_hash = random.randint(1000, 9999)
            unique_id = f"{current_action} [{random_hash}]: {mission[:20]}..."

            st.session_state.itinerary.append({
                "label": unique_id,
                "mood": current_action,
                "vibe": vibe,
                "mission": mission,
                "legendary": is_legendary,
                "ai_generated": is_ai_generated
            })
            st.session_state.order_list.append(unique_id)
            
            # Clear register button memory
            st.session_state.active_trigger = None
            st.rerun()

    # --- STEP 3: INTERACTIVE TIMELINE REORDERING ---
    if st.session_state.itinerary and not st.session_state.show_debrief:
        st.write("--------------------------------------------------")
        st.write("🔧 REORDER OR REMOVE STOPS FROM THE TIMELINE:")
        sorted_order = st.multiselect(
            "Drag, drop, or remove steps to set your sequence metric configuration:",
            options=st.session_state.order_list,
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
                elif item["ai_generated"]:
                    alert_prefix = " [LEGENDARY AI AMPLIFIED]" if item["legendary"] else " [AI CLOUD ENHANCED]"
                else:
                    alert_prefix = " [LEGENDARY EXCURSION]" if item["legendary"] else " [LOCAL CREATIVE]"
                
                # Render using native safe container blocks with config color themes
                with st.container(border=True):
                    st.markdown(f"**STOP {index + 1}: {item['mood']}{alert_prefix}**")
                    st.write(f"**[ENVIRONMENT VIBE]:** {item['vibe']}")
                    st.markdown("---")
                    st.write(f"**[ASSIGNMENT]:** {item['mission']}")

        # --- DIAGNOSTIC ANALYTICS EXPANDER ("STATS FOR NERDS") ---
        with st.expander("📊 STATS FOR NERDS (DIAGNOSTIC ANALYTICS)"):
            total_stops = len(st.session_state.order_list)
            active_items = [itinerary_map[l] for l in st.session_state.order_list if l in itinerary_map]
            
            walk_count = sum(1 for x in active_items if x["mood"] == "WALK")
            eat_count = sum(1 for x in active_items if x["mood"] == "EAT")
            chill_count = sum(1 for x in active_items if x["mood"] == "CHILL")
            legendary_count = sum(1 for x in active_items if x["legendary"])
            ai_count = sum(1 for x in active_items if x.get("ai_generated", False))
            
            st.markdown(f"**⚡ TOTAL TIMELINE ENTRIES:** {total_stops} stops configured")
            st.text(f"WALK  [{'█' * walk_count}{'░' * (total_stops-walk_count)}] {walk_count} allocations")
            st.text(f"EAT   [{'█' * eat_count}{'░' * (total_stops-eat_count)}] {eat_count} allocations")
            st.text(f"CHILL [{'█' * chill_count}{'░' * (total_stops-chill_count)}] {chill_count} allocations")
            
            st.markdown("---")
            st.write("**🛡️ OPERATIONAL INTEGRITY SCORE:**")
            st.write(f"- Running AI Cloud Core: **{'CONNECTED (HF SERVERLESS)' if ai_enabled else 'OFFLINE (FALLBACK EMBEDDED)'}**")
            st.write(f"- Active AI Generations: **{ai_count} modules loaded**")
            st.write(f"- Cloud Transmission Safety Block: **{'ENGAGED (SANDBOX OVERRIDE)' if demo_mode else 'LIVE TO LEDGER'}**")

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
                notes = st.text_area(f"Quick Notes (Stop {index + 1}):", placeholder="What did you eat? Best photo details? Inside jokes...", key=f"notes_{index}")
                st.markdown("---")
                
                new_rows.append({
                    "Date": current_date,
                    "Neighborhood": st.session_state.current_hood,
                    "Stop_Number": int(index + 1),
                    "Mood": item['mood'],
                    "Vibe": item['vibe'],
                    "Mission": item['mission'],
                    "Status": status,
                    "Notes": notes
                })
        
        st.write("### 💾 TRANSMIT STRATEGY REPORT")
        
        if demo_mode:
            if st.button("⚡ SIMULATE CLOUD TRANSMISSION (DEMO)"):
                st.warning("SIMULATION LOG: Cloud sync bypassed. Previewing current staging payload:")
                st.dataframe(pd.DataFrame(new_rows))
                st.success("DEMO SUCCESS: Log array staging simulation verified with zero errors!")
        else:
            if st.button("⚡ APPEND CAMPAIGN TO SHARED CLOUD SHEET"):
                if conn is not None:
                    try:
                        existing_df = conn.read(ttl=0)
                        fresh_df = pd.DataFrame(new_rows)
                        updated_df = pd.concat([existing_df, fresh_df], ignore_index=True)
                        conn.update(data=updated_df)
                        st.success("SUCCESS: Telemetry array successfully committed to Google Cloud ledger!")
                    except Exception as e:
                        st.error(f"TRANSMISSION INTERRUPTED: {e}")
                else:
                    st.error("ERROR: Sheets Connection Offline. Verify secrets token credentials.")
        
        if st.button("⬅️ RETURN TO TIMELINE EDITING"):
            st.session_state.show_debrief = False
            st.rerun()

    if st.button("ABANDON MISSION & RESET MATRIX"):
        st.session_state.started = False
        st.session_state.current_hood = None
        st.session_state.itinerary = []
        st.session_state.order_list = []
        st.session_state.show_debrief = False
        st.session_state.active_trigger = None
        st.rerun()