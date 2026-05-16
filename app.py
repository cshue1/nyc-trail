import streamlit as st
import random
import json
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from google import genai

st.set_page_config(page_title="NYC TRAIL PLANNER", page_icon="🤠", layout="centered")

# ==============================================================================
# RETRO CYBERPUNK TERMINAL CSS THEME OVERRIDES
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
    
    /* System Command Buttons & Popover Inputs */
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
    
    /* Popover Content Dialogue Window */
    div[data-testid="stPopoverBody"] {
        background-color: #111111 !important;
        border: 3px solid #33ff33 !important;
        padding: 15px !important;
    }
    
    /* Stats Extander Custom Outline Framework */
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
    
    /* Strategic UI Card Matrices */
    .adventure-box { background-color: #000000; border: 4px double #33ff33; padding: 15px; margin-top: 15px; line-height: 1.4; }
    .override-box { background-color: #000000; border: 4px double #ff3333; padding: 15px; margin-top: 15px; line-height: 1.4; color: #ff3333 !important; }
    .demo-box { background-color: #000000; border: 4px double #ffff33; padding: 15px; margin-top: 15px; line-height: 1.4; color: #ffff33 !important; }
    .ai-box { background-color: #000000; border: 4px double #00ffff; padding: 15px; margin-top: 15px; line-height: 1.4; color: #00ffff !important; }
    
    .itinerary-header { font-size: 36px !important; margin-top: 30px; text-decoration: underline; text-transform: uppercase; }
    .divider { border-top: 3px dashed #33ff33; margin: 10px 0; }
    .divider-red { border-top: 3px dashed #ff3333; margin: 10px 0; }
    .divider-yellow { border-top: 3px dashed #ffff33; margin: 10px 0; }
    .divider-cyan { border-top: 3px dashed #00ffff; margin: 10px 0; }
    
    div[data-baseweb="select"] { background-color: #000000 !important; border: 2px dashed #33ff33 !important; }
    div[role="button"] { background-color: #111111 !important; color: #33ff33 !important; border: 1px solid #33ff33 !important; }
    
    /* Force check labels into monochrome green */
    div[data-testid="stCheckbox"] label p { color: #33ff33 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>== NYC TRAIL PLANNER v6.0 ==</h1>", unsafe_allow_html=True)

# ==============================================================================
# DASHBOARD SYSTEM CONTROL HEADER
# ==============================================================================
col_info, col_toggle = st.columns([2, 1])
with col_info:
    with st.popover("ℹ️ VIEW SYSTEM WORKFLOW"):
        st.markdown("<h3 style='color: #33ff33 !important;'>== AUTOMATED BACKEND LOOP ==</h3>", unsafe_allow_html=True)
        st.write("🤖 **1. STACK:** Drop your random sector and map custom itinerary components.")
        st.write("🧠 **2. COGNITION:** Gemini inputs your JSON file strings as baseline rules, then customizes them.")
        st.write("📸 **3. CAPTURE:** Take photos natively on your device camera roll while executing operations.")
        st.write("📊 **4. TRANSMIT:** Appends a text telemetry log row straight to your shared Google Sheet.")
        st.write("🖼️ **5. PUSH MEDIA:** Manually dump the afternoon's best frames into your fixed shared master album folder.")

with col_toggle:
    demo_mode = st.toggle("🛠️ DEMO MODE", value=False, help="Blocks all Google Sheets writes and simulates staging logs.")

if demo_mode:
    st.markdown("<p style='color: #ffff33 !important; text-align: center; font-weight: bold;'>⚠️ SANDBOX MATRIX ENGAGED: TRANSMISSIONS DEACTIVATED ⚠️</p>", unsafe_allow_html=True)

st.write("--------------------------------------------------")

# ==============================================================================
# INITIALIZE DATABASE & API CONFIGURATIONS
# ==============================================================================
ai_enabled = False
if "GEMINI_API_KEY" in st.secrets:
    try:
        ai_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        ai_enabled = True
    except Exception:
        ai_enabled = False

try:
    with open("adventures.json", "r") as file:
        adventure_pool = json.load(file)
except FileNotFoundError:
    st.error("CRITICAL ERROR: MISSING ADVENTURES.JSON SOURCE LEDGER.")
    adventure_pool = {}

# --- INITIALIZE PERSISTENT SESSION STATES ---
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
# STEP 1: DROP REGIONAL LOCATION SECTOR
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

    # Display configuration buttons only if we are actively planning the trip layout
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
        # STEP 2: DUAL-BRANCH GEMINI CREATIVE SYNTHESIS GATEWAY
        # ==============================================================================
        if chosen_mood:
            is_legendary = False
            is_ai = False
            
            # Extract baseline data strings straight from adventures.json template configuration
            if has_override:
                chosen_package = random.choice(overrides[st.session_state.current_hood]["packages"])
                base_vibe = chosen_package["vibe"]
                base_mission = random.choice(chosen_package["missions"])
                is_legendary = True
            else:
                base_vibe = random.choice(adventure_pool["vibes"])
                base_mission = random.choice(adventure_pool[chosen_mood]["missions"])

            # Render live geo-mapping checkbox parameter directly inside action sequence
            st.write("---")
            activate_live_map = st.checkbox("🛰️ MAP TO REAL-WORLD STREET COORDINATES", value=False, 
                                            help="Flipping this anchors the AI amplification step to a specific, real commercial venue name or physical address landmark.")

            if ai_enabled:
                is_ai = True
                with st.spinner("🧠 ENGAGING DUAL-ENGINE GEMINI CONTEXT CORES..."):
                    try:
                        if activate_live_map:
                            # BRANCH A: DYNAMIC PHYSICAL GEO-MAPPING
                            prompt = f"""
                            You are the advanced content-enhancement engine for an offline retro text adventure game set in NYC called "NYC TRAIL PLANNER".
                            Current Drop Sector Location: {st.session_state.current_hood}
                            Strategy Component Action Category: {chosen_mood}

                            DATA SEED FROM BLUEPRINT:
                            BASE VIBE: {base_vibe}
                            BASE MISSION: {base_mission}

                            INSTRUCTIONS:
                            Take the concepts, photography framing rules, and constraints from the BASE MISSION and amplify the creative text.
                            Then, map it directly onto real, specific, highly-rated physical storefronts, venues, or street landmarks within {st.session_state.current_hood}.
                            
                            STRICT DIETARY BOUNDARY: If food is referenced, the target spot and food item MUST be strictly pescatarian (fish/seafood/dairy/eggs allowed; NO land meats/broths) and COMPLETELY AVOCADO-FREE. Do not include avocados under any circumstances.
                            Match the tone of a high-tech tactical terminal or cyberpunk operative deck.

                            Output your response in exactly this strict raw text structure, with no extra chatter or markdown bolding around titles:
                            VIBE: [Enhanced environment vibe in ALL CAPS, weaving in real local landmarks]
                            MISSION: [Enhanced action assignment, anchoring the base mission rules to a real physical venue coordinate]
                            """
                        else:
                            # BRANCH B: CONCEPTUAL CREATIVE AMPLIFICATION (PURE IMAGINATION)
                            prompt = f"""
                            You are the creative amplification engine for an offline retro text adventure game set in NYC called "NYC TRAIL PLANNER".
                            Current Drop Sector Location: {st.session_state.current_hood}
                            Strategy Component Action Category: {chosen_mood}

                            DATA SEED FROM BLUEPRINT:
                            BASE VIBE: {base_vibe}
                            BASE MISSION: {base_mission}

                            INSTRUCTIONS:
                            Use this base blueprint purely as an imaginative launching pad. Amp up the flavor text, add rich cinematic atmospheric descriptors, and inject a creative or dramatic narrative objective.
                            CRITICAL RESTRICTION: Do NOT name or recommend real-world commercial business storefronts, restaurants, or specific shops. Keep it generalized to architectural types (e.g., "a dim-lit neon window", "an old brick stoop").
                            
                            STRICT DIETARY BOUNDARY: If food is referenced, keep descriptions strictly pescatarian and completely avocado-free.
                            Match the tone of a high-tech tactical terminal or cyberpunk operative deck.

                            Output your response in exactly this strict raw text structure, with no extra chatter or markdown bolding around titles:
                            VIBE: [Amplified descriptive environment vibe in ALL CAPS using pure atmospheric and architectural textures]
                            MISSION: [Amplified action assignment, elevating the base photography framing rules with creative storytelling twists]
                            """
                        
                        response = ai_client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=prompt,
                        )
                        ai_text = response.text
                        
                        vibe = base_vibe
                        mission = ai_text
                        for line in ai_text.split("\n"):
                            if line.strip().startswith("VIBE:"): vibe = line.replace("VIBE:", "").strip()
                            if line.strip().startswith("MISSION:"): mission = line.replace("MISSION:", "").strip()
                            
                    except Exception as e:
                        vibe = base_vibe + " (AI Pipeline Error)"
                        mission = base_mission
            else:
                vibe = base_vibe
                mission = base_mission

            # Deduplicate labels to keep timeline multiselect sorting indexes clean
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
                "ai_generated": is_ai,
                "live_mapped": activate_live_map
            })
            st.session_state.order_list.append(unique_id)
            st.rerun()

    # --- STEP 3: INTERACTIVE DRAG-AND-DROP REORDERING ---
    if st.session_state.itinerary and not st.session_state.show_debrief:
        st.write("--------------------------------------------------")
        st.write("🔧 REORDER OR REMOVE STOPS FROM THE TIMELINE:")
        sorted_order = st.multiselect(
            "Drag, drop, or remove steps to set your sequence metric configuration:",
            options=st.session_state.order_list,
            default=st.session_state.order_list
        )
        st.session_state.order_list = sorted_order

    # --- STEP 4: DISPLAY ADAPTIVE ITINERARY BLOCK MATRIX ---
    if st.session_state.itinerary and not st.session_state.show_debrief:
        st.markdown("<p class='itinerary-header'>== TARGET DAY ITINERARY ==</p>", unsafe_allow_html=True)
        itinerary_map = {item["label"]: item for item in st.session_state.itinerary}
        
        for index, label in enumerate(st.session_state.order_list):
            item = itinerary_map.get(label)
            if item:
                if demo_mode:
                    box_class, div_class, alert_prefix, txt_color = "demo-box", "divider-yellow", " [DEMO SIMULATION]", "color: #ffff33 !important;"
                elif item["ai_generated"]:
                    if item["legendary"]:
                        prefix_label = " [LEGENDARY ENHANCED]"
                        box_class, div_class = "override-box", "divider-red"
                        txt_color = "color: #ff3333 !important;"
                    else:
                        prefix_label = " [LIVE GEO-MAPPED]" if item["live_mapped"] else " [AMPLIFIED BLUEPRINT]"
                        box_class, div_class = "ai-box", "divider-cyan"
                        txt_color = "color: #00ffff !important;"
                    alert_prefix = prefix_label
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

        # ==============================================================================
        # 📈 DIAGNOSTIC ANALYTICS EXPANDER ("STATS FOR NERDS")
        # ==============================================================================
        with st.expander("📊 STATS FOR NERDS (DIAGNOSTIC ANALYTICS)"):
            total_stops = len(st.session_state.order_list)
            active_items = [itinerary_map[l] for l in st.session_state.order_list if l in itinerary_map]
            
            walk_count = sum(1 for x in active_items if x["mood"] == "WALK")
            eat_count = sum(1 for x in active_items if x["mood"] == "EAT")
            chill_count = sum(1 for x in active_items if x["mood"] == "CHILL")
            legendary_count = sum(1 for x in active_items if x["legendary"])
            ai_count = sum(1 for x in active_items if x.get("ai_generated", False))
            live_map_count = sum(1 for x in active_items if x.get("live_mapped", False))
            
            st.markdown(f"**⚡ TOTAL TIMELINE ENTRIES:** {total_stops} stops configured")
            st.text(f"WALK  [{'█' * walk_count}{'░' * (total_stops-walk_count)}] {walk_count} allocations")
            st.text(f"EAT   [{'█' * eat_count}{'░' * (total_stops-eat_count)}] {eat_count} allocations")
            st.text(f"CHILL [{'█' * chill_count}{'░' * (total_stops-chill_count)}] {chill_count} allocations")
            
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.write("**💎 CORE COMPOSITION BALANCING MATRIX:**")
            st.write(f"- Curated Handmade Overrides: **{legendary_count} sectors**")
            st.write(f"- Amplified Core Pipelines: **{ai_count - live_map_count} instances**")
            st.write(f"- Live Storefront Geo-Mappings: **{live_map_count} endpoints**")

        st.write("--------------------------------------------------")
        if st.button("🏁 END DAY & OPEN MISSION DEBRIEF"):
            st.session_state.show_debrief = True
            st.rerun()

    # ==============================================================================
    # STEP 5: MISSION DEBRIEF & CONDITIONAL SHEET STREAMING
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