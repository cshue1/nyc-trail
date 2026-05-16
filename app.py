import streamlit as st
import random
import json
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import google.genai as genai

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
# INITIALIZE HIGH-SPEED GOOGLE GEMINI CORE LINK (ONCE PER SESSION)
# ==============================================================================
if st.session_state.ai_active_model is None:
    gemini_api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            # Standard deployment configurations check (Free tier targets)
            for model_name in ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-pro"]:
                try:
                    test_model = genai.GenerativeModel(model_name)
                    # Low-latency ping call to verify connection layer integrity
                    test_model.generate_content("Ping", generation_config={"max_output_tokens": 5})
                    st.session_state.ai_active_model = model_name
                    break
                except Exception:
                    continue
        except Exception as e:
            st.sidebar.warning(f"⚠️ SDK Core configuration failed: {str(e)}")
            st.session_state.ai_active_model = "OFFLINE"
    else:
        st.session_state.ai_active_model = "OFFLINE"

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
    except