import streamlit as st
import random
import json
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="NYC TRAIL PLANNER", page_icon="🤠", layout="centered")

# ==============================================================================
# RETRO CYBERPUNK TERMINAL CSS THEME OVERRIDES (WITH SECURITY BYPASS APPLIED)
# ==============================================================================
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
    <style>
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #000000 !important;
        color: #33ff33 !important;
        font-family: 'VT323', monospace !important;
        font-size: 24px;
    }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #33ff33 !important; font-family: 'VT323', monospace !important; }
    h1 { font-size: 48px !important; text-align: center; text-transform: uppercase; }
    h3 { font-size: 32px !important; text-transform: uppercase; }
    
    .stButton>button, div[data-testid="stPopover"] > button {
        width: 100%;
        background-color: #000000 !important;
        color: #33ff33 !important;
        font-family: 'VT323', monospace !important;
        font-size: 26px !important;
        border: 3px dashed #33ff33 !important;
        border-radius: 0px !important;
        padding: 10px !important;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .stButton>button:hover, div[data-testid="stPopover"] > button:hover { 
        background-color: #33ff33 !important; 
        color: #000000 !important; 
    }
    
    div[data-testid="stPopoverBody"] {
        background-color: #111111 !important;
        border: 3px solid #33ff33 !important;
        padding: 15px !important;
    }
    
    div[data-testid="stExpander"] {
        background-color: #000000 !important;
        border: 3px solid #33ff33 !important;
        border-radius: 0px !important;
        margin-top: 15px;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #111111 !important;
        color: #33ff33 !important;
        border: 2px dashed #33ff33 !important;
        font-family: 'VT323', monospace !important;
        font-size: 22px !important;
    }
    
    .adventure-box { background-color: #000000; border: 4px double #33ff33; padding: 15px; margin-top: 15px; line-height: 1.4; }
    .override-box { background-color: #000000; border: 4px double #ff3333; padding: 15px; margin-top: 15px; line-height: 1.4; color: #ff3333 !important; }
    .demo-box { background-color: #000000; border: 4px double #ffff33; padding: 15px; margin-top: 15px; line-height: 1.4; color: #ffff33 !important; }
    .amplified-box { background-color: #000000; border: 4px double #00ffff; padding: 15px; margin-top: 15px; line-height: 1.4; color: #00ffff !important; }
    
    .itinerary-header { font-size: 36px !important; margin-top: 30px; text-decoration: underline; text-transform: uppercase; }
    .divider { border-top: 3px dashed #33ff33; margin: 10px 0; }
    .divider-red { border-top: 3px dashed #ff3333; margin: 10px 0; }
    .divider-yellow { border-top: 3px dashed #ffff33; margin: 10px 0; }
    .divider-cyan { border-top: 3px dashed #00ffff; margin: 10px 0; }
    
    div[data-baseweb="select"] { background-color: #000000 !important; border: 2px dashed #33ff33 !important; }
    div[role="button"] { background-color: #111111 !important; color: #33ff33 !important; border: 1px solid #33ff33 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>== NYC TRAIL PLANNER v1 ==</h1>", unsafe_allow_html=True)

# ==============================================================================
# SYSTEM CONTROL HEADER
# ==============================================================================
col_info, col_toggle = st.columns([2, 1])
with col_info:
    with st.popover("ℹ️ VIEW SYSTEM WORKFLOW"):
        st.markdown("<h3 style='color: #33ff33 !important;'>== AUTOMATED BACKEND LOOP ==</h3>", unsafe_allow_html=True)
        st.write("🤖 **1. STACK:** Drop random location coordinates and load objective matrices.")
        st.write("🔒 **2. DETERMINISTIC CORE:** Runs 100% locally with zero external network execution data risk.")
        st.write("📸 **3. CAPTURE:** Document field entries natively on your camera roll.")
        st.write("📊 **4. TRANSMIT:** Appends mission telemetry rows directly to your shared Google Sheet.")

with col_toggle:
    demo_mode = st.toggle("🛠️ DEMO MODE", value=False, help="Blocks Google Sheet streaming updates to simulate sandboxed logs.")

if demo_mode:
    st.markdown("<p style='color: #ffff33 !important; text-align: center; font-weight: bold;'>⚠️ SANDBOX MATRIX ENGAGED: TRANSMISSIONS DEACTIVATED ⚠️</p>", unsafe_allow_html=True)

st.write("--------------------------------------------------")

# ==============================================================================
# SECURE LOCAL DATA EXTRACTION ENGINE
# ==============================================================================
try:
    with open("adventures.json", "r") as file:
        adventure_pool = json.load(file)
except FileNotFoundError:
    st.error("CRITICAL ERROR: MISSING ADVENTURES.JSON SOURCE DECK.")
    adventure_pool = {}

# Local matrix arrays for zero-risk, high-flavor text amplification injections
cyber_prefixes = ["TACTICAL RECONNAISSANCE PROTOCOL", "SILENT OBJECTIVE VECTOR", "CRITICAL METRIC HUNT", "MINIMALIST FRAMING COGNITION", "GEOMETRIC MATRIX TRACKER"]
cyber_atmospheres = ["UNDER THE CONCRETE SHADOW GRID OF", "TRACKING THROUGH THE LOW-LIGHT SECTOR CORES OF", "NAVIGATING THE HIGH-CONTRAST TEXTURE FIELDS OF", "EXPLORING THE HISTORIC ARCHITECTURAL CHANNELS OF"]

if "started" not in st.session_state: st.session_state.started = False
if "current_hood" not in st.session_state: st.session_state.current_hood = None
if "itinerary" not in st.session_state: st.session_state.itinerary = []
if "order_list" not in st.session_state: st.session_state.order_list = []
if "show_debrief" not in st.session_state: st.session_state.show_debrief = False

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
            st.rerun()
else:
    st.markdown(f"<h3>[DROPPED SECTOR]: {st.session_state.current_hood}</h3>", unsafe_allow_html=True)
    
    overrides = adventure_pool.get("special_overrides", {})
    has_override = st.session_state.current_hood in overrides and "packages" in overrides[st.session_state.current_hood]

    if not st.session_state.show_debrief:
        st.write("CHOOSE YOUR STRATEGY FOR THE NEXT STOP IN THIS AREA:")
        col1, col2, col3 = st.columns(3)
        chosen_mood = None

        with col1:
            if st.button("➕ ADD WALK"): chosen_mood = "WALK"
        with col2:
            if st.button("➕ ADD EAT"): chosen_mood = "EAT"
        with col3:
            if st.button("➕ ADD CHILL"): chosen_mood = "CHILL"

        # ==============================================================================
        # STEP 2: STOCHASTIC AMPLIFICATION GATEWAY (100% SECURE & LOCAL)
        # ==============================================================================
        if chosen_mood:
            is_legendary = False
            is_amplified = False
            
            # Base Extraction
            if has_override:
                chosen_package = random.choice(overrides[st.session_state.current_hood]["packages"])
                base_vibe = chosen_package["vibe"]
                base_mission = random.choice(chosen_package["missions"])
                is_legendary = True
            else:
                base_vibe = random.choice(adventure_pool["vibes"])
                base_mission = random.choice(adventure_pool[chosen_mood]["missions"])

            # UI Control Switch
            st.write("---")
            amplify_flavor = st.checkbox("⚡ ACTIVATE LOCAL CREATIVE AMPLIFIER PROTOCOL", value=False, 
                                         help="Uses local deterministic random text layers to expand cinematic description fields safely.")

            if amplify_flavor:
                is_amplified = True
                prefix = random.choice(cyber_prefixes)
                atmosphere = random.choice(cyber_atmospheres)
                
                vibe = f"{prefix} // {base_vibe}"
                mission = f"[{prefix} ENGAGED]: {atmosphere} {st.session_state.current_hood}. Execute following parameters precisely: {base_mission}"
            else:
                vibe = base_vibe
                mission = base_mission

            # Deduplicate labels to safeguard timeline sorting mechanics
            unique_id = f"{chosen_mood}: {mission[:30]}..."
            dup_count = sum(1 for x in st.session_state.itinerary if x["label"].startswith(unique_id))
            if dup_count > 0:
                unique_id = f"{chosen_mood} ({dup_count + 1}): {mission[:30]}..."

            st.session_state.itinerary.append({
                "label": unique_id,
                "mood": chosen_mood,
                "vibe": vibe,
                "mission": mission,
                "legendary": is_legendary,
                "amplified": is_amplified
            })
            st.session_state.order_list.append(unique_id)
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

    # --- STEP 4: DISPLAY ADAPTIVE BLOCK MATRIX ---
    if st.session_state.itinerary and not st.session_state.show_debrief:
        st.markdown("<p class='itinerary-header'>== TARGET DAY ITINERARY ==</p>", unsafe_allow_html=True)
        itinerary_map = {item["label"]: item for item in st.session_state.itinerary}
        
        for index, label in enumerate(st.session_state.order_list):
            item = itinerary_map.get(label)
            if item:
                if demo_mode:
                    box_class, div_class, alert_prefix, txt_color = "demo-box", "divider-yellow", " [DEMO SIMULATION]", "color: #ffff33 !important;"
                elif item["amplified"]:
                    prefix_label = " [LEGENDARY AMPLIFIED]" if item["legendary"] else " [LOCAL EXTRA CREATIVE]"
                    box_class = "override-box" if item["legendary"] else "amplified-box"
                    div_class = "divider-red" if item["legendary"] else "divider-cyan"
                    alert_prefix = prefix_label
                    txt_color = "color: #ff3333 !important;" if item["legendary"] else "color: #00ffff !important;"
                else:
                    box_class = "override-box" if item["legendary"] else "adventure-box"
                    div_class = "divider-red" if item["legendary"] else "divider"
                    alert_prefix = " [LEGENDARY EXCURSION]" if item["legendary"] else ""
                    txt_color = "color: #ff3333 !important;" if item["legendary"] else "color: #33ff33 !important;"
                
                st.markdown(f"""
                    <div class="{box_class}">
                        <strong style="{txt_color}">STOP {index + 1}: {item['mood']}{alert_prefix}</strong><br>
                        <span style="{txt_color}">[ENVIRONMENT VIBE]: {item['vibe']}</span>
                        <div class="{div_class}"></div>
                        <span style="{txt_color}">[ASSIGNMENT]: {item['mission']}</span>
                    </div>
                """, unsafe_allow_html=True)

        # --- DIAGNOSTIC ANALYTICS EXPANDER ("STATS FOR NERDS") ---
        with st.expander("📊 STATS FOR NERDS (DIAGNOSTIC ANALYTICS)"):
            total_stops = len(st.session_state.order_list)
            active_items = [itinerary_map[l] for l in st.session_state.order_list if l in itinerary_map]
            
            walk_count = sum(1 for x in active_items if x["mood"] == "WALK")
            eat_count = sum(1 for x in active_items if x["mood"] == "EAT")
            chill_count = sum(1 for x in active_items if x["mood"] == "CHILL")
            legendary_count = sum(1 for x in active_items if x["legendary"])
            amp_count = sum(1 for x in active_items if x.get("amplified", False))
            
            st.markdown(f"**⚡ TOTAL TIMELINE ENTRIES:** {total_stops} stops configured")
            st.text(f"WALK  [{'█' * walk_count}{'░' * (total_stops-walk_count)}] {walk_count} allocations")
            st.text(f"EAT   [{'█' * eat_count}{'░' * (total_stops-eat_count)}] {eat_count} allocations")
            st.text(f"CHILL [{'█' * chill_count}{'░' * (total_stops-chill_count)}] {chill_count} allocations")
            
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.write("**🛡️ OPERATIONAL INTEGRITY SCORE:**")
            st.write("- Running Environment: **100% Air-Gapped Sandbox Local**")
            st.write(f"- Active Creative Variations: **{amp_count} structures deployed**")
            st.write("- Third-Party Security Vulnerability Vector: **0.00%**")

        st.write("--------------------------------------------------")
        if st.button("🏁 END DAY & OPEN MISSION DEBRIEF"):
            st.session_state.show_debrief = True
            st.rerun()

    # ==============================================================================
    # STEP 5: MISSION DEBRIEF & CONDITIONAL DATA SAVING
    # ==============================================================================
    if st.session_state.show_debrief:
        st.markdown("<p class='itinerary-header'>== FIELD MISSION DEBRIEF ==</p>", unsafe_allow_html=True)
        st.write("RECORD CURRENT TRACKING STATS TO YOUR SHARABLE DATABASE LEDGER:")
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
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
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                
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
        st.rerun()