import streamlit as st
import pandas as pd
import numpy as np
import requests
import pydeck as pdk
import plotly.express as px
from datetime import datetime, timedelta
from krigging import perform_kriging_correct, get_aqi_at_location
import geopandas as gpd
from shapely.geometry import Point
import os

# Import the updated agent logic
from agent_logic import (
    get_personalized_recommendation,
    format_recommendation_for_sms,
    get_aqi_category
)

# ==========================
# PAGE CONFIGURATION
# ==========================
st.set_page_config(
    layout="wide",
    page_title="Delhi Air Quality Dashboard",
    page_icon="💨"
)

# ==========================
# STATIC CONFIG
# ==========================
API_TOKEN = "97a0e712f47007556b57ab4b14843e72b416c0f9"
DELHI_BOUNDS = "28.404,76.840,28.883,77.349"
DELHI_LAT = 28.6139
DELHI_LON = 77.2090

DELHI_GEOJSON_URL = "https://raw.githubusercontent.com/shuklaneerajdev/IndiaStateTopojsonFiles/master/Delhi.geojson"

# ==========================
# TELEGRAM CONFIGURATION
# ==========================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8582253332:AAECTJHc6o9Q2OVWhi-FIGIDyagosLtDdJo")

def send_telegram_notification(bot_token, chat_id, message):
    """Send message via Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("ok"):
            return True, "Telegram notification sent successfully."
        else:
            error_desc = data.get("description", "Unknown error")
            return False, f"Telegram API error: {error_desc}"
            
    except requests.RequestException as e:
        return False, f"Failed to send Telegram message: {str(e)}"
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"

# ==========================
# CUSTOM CSS FOR STYLING
# ==========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background - Sky Blue Theme */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Hide Streamlit's default header and footer */
    header, footer, #MainMenu {
        visibility: hidden;
    }
    
    /* Main title styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #ffffff;
        padding: 1.5rem 0 0.5rem 0;
        text-align: center;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
        letter-spacing: -1px;
    }

    /* Subtitle styling */
    .subtitle {
        font-size: 1.2rem;
        color: #f0f0f0;
        text-align: center;
        padding-bottom: 1.5rem;
        font-weight: 500;
    }

    /* Metric cards styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        text-align: center;
        height: 100%;
    }
    .metric-card-label {
        font-size: 1rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    .metric-card-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #764ba2;
        margin: 0.5rem 0;
    }
    .metric-card-delta {
        font-size: 0.9rem;
        color: #667eea;
        font-weight: 500;
    }

    /* Weather widget styling */
    .weather-widget {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        height: 100%;
    }
    .weather-temp {
        font-size: 2.5rem;
        font-weight: 800;
        color: #764ba2;
    }

    /* Styling for Streamlit tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent;
        padding: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1rem 2rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: #667eea;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 1);
        border-color: #764ba2;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white !important;
        border-color: #ffd89b;
    }

    /* General card for content */
    .content-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        margin-top: 1.5rem;
    }

    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #764ba2;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #ffd89b;
    }
    
    /* Recommendation Card Styling */
    .recommendation-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 15px 35px rgba(240, 147, 251, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .recommendation-card h3 {
        color: white;
        margin-top: 0;
        font-size: 1.8rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .recommendation-section {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .recommendation-section h4 {
        color: #ffd89b;
        margin-top: 0;
        font-size: 1.3rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .recommendation-list {
        list-style: none;
        padding-left: 0;
        margin: 0;
    }
    
    .recommendation-list li {
        padding: 0.5rem 0;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    .recommendation-list li:before {
        content: "✓ ";
        color: #4ade80;
        font-weight: bold;
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }

    /* Form styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: white !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
        color: #333 !important;
        font-weight: 500 !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 0 2px rgba(118, 75, 162, 0.2) !important;
    }
    
    .stMultiSelect > div > div {
        background-color: white !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 1rem 2.5rem;
        box-shadow: 0 6px 20px rgba(25, 84, 123, 0.4);
        transition: all 0.3s ease;
        font-size: 1.1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(25, 84, 123, 0.5);
    }
    
    /* Info box styling */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .info-box h3 {
        color: white;
        margin-top: 0;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        padding: 0.5rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: white;
        padding: 1rem;
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading Delhi boundary...")
def load_delhi_boundary_from_url():
    try:
        gdf = gpd.read_file(DELHI_GEOJSON_URL)
        if gdf.crs is None or gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        polygon = gdf.unary_union
        return gdf, polygon
    except Exception as e:
        st.error(f"Failed to load Delhi polygon: {e}")
        return None, None

# Load once into session_state
if "delhi_gdf" not in st.session_state or "delhi_polygon" not in st.session_state:
    gdf, polygon = load_delhi_boundary_from_url()
    st.session_state["delhi_gdf"] = gdf
    st.session_state["delhi_polygon"] = polygon


@st.cache_data(ttl=600, show_spinner="Fetching Air Quality Data...")
def fetch_live_data():
    """Fetches and processes live AQI data from the WAQI API."""
    url = f"https://api.waqi.info/map/bounds/?latlng={DELHI_BOUNDS}&token={API_TOKEN}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "ok":
            df = pd.DataFrame(data["data"])
            df = df[df['aqi'] != "-"]
            df['aqi'] = pd.to_numeric(df['aqi'], errors='coerce')
            df = df.dropna(subset=['aqi'])

            def safe_get_name(x):
                if isinstance(x, dict):
                    return x.get('name', 'N/A')
                elif isinstance(x, str):
                    return x
                else:
                    return 'N/A'

            def safe_get_time(x):
                if isinstance(x, dict):
                    time_data = x.get('time', {})
                    if isinstance(time_data, dict):
                        return time_data.get('s', 'N/A')
                    elif isinstance(time_data, str):
                        return time_data
                    else:
                        return 'N/A'
                else:
                    return 'N/A'

            df['station_name'] = df['station'].apply(safe_get_name)
            df['last_updated'] = df['station'].apply(safe_get_time)
            df[['category', 'color', 'emoji', 'advice']] = df['aqi'].apply(
                lambda x: pd.Series(get_aqi_category_legacy(x)))
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            df = df.dropna(subset=['lat', 'lon'])
            return df
        return pd.DataFrame()
    except requests.RequestException:
        return pd.DataFrame()


def get_aqi_category_legacy(aqi):
    """Legacy function for backward compatibility"""
    if aqi <= 50:
        return "Good", [0, 158, 96], "✅", "Enjoy outdoor activities."
    elif aqi <= 100:
        return "Moderate", [255, 214, 0], "🟡", "Unusually sensitive people should consider reducing prolonged or heavy exertion."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", [249, 115, 22], "🟠", "Sensitive groups should reduce prolonged or heavy exertion."
    elif aqi <= 200:
        return "Unhealthy", [220, 38, 38], "🔴", "Everyone may begin to experience health effects."
    elif aqi <= 300:
        return "Very Unhealthy", [147, 51, 234], "🟣", "Health alert: everyone may experience more serious health effects."
    else:
        return "Hazardous", [126, 34, 206], "☠️", "Health warnings of emergency conditions."


@st.cache_data(ttl=1800, show_spinner="Fetching Weather Data...")
def fetch_weather_data():
    """Fetches current weather data from Open-Meteo API."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={DELHI_LAT}&longitude={DELHI_LON}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=Asia/Kolkata"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def get_weather_info(code):
    """Converts WMO weather code to a description and icon."""
    codes = {
        0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"), 45: ("Fog", "🌫️"), 48: ("Depositing rime fog", "🌫️"),
        51: ("Light drizzle", "💧"), 53: ("Moderate drizzle", "💧"), 55: ("Dense drizzle", "💧"),
        61: ("Slight rain", "🌧️"), 63: ("Moderate rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
        80: ("Slight rain showers", "🌦️"), 81: ("Moderate rain showers", "🌦️"),
        82: ("Violent rain showers", "⛈️"), 95: ("Thunderstorm", "⚡"),
        96: ("Thunderstorm, slight hail", "⛈️"), 99: ("Thunderstorm, heavy hail", "⛈️")
    }
    return codes.get(code, ("Unknown", "❓"))


def render_header(df):
    """Renders the main header with summary metrics and weather."""
    st.markdown('<div class="main-title">🌍 Delhi Air Quality Dashboard</div>',
                unsafe_allow_html=True)
    last_update_time = df['last_updated'].max(
    ) if not df.empty and 'last_updated' in df.columns else "N/A"
    st.markdown(
        f'<p class="subtitle">Real-time monitoring • Last updated: {last_update_time}</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    if not df.empty:
        with c1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-card-label">Average AQI</div><div class="metric-card-value">{df["aqi"].mean():.1f}</div><div class="metric-card-delta">{get_aqi_category(df["aqi"].mean())}</div></div>', unsafe_allow_html=True)
        with c2:
            min_station = df.loc[df["aqi"].idxmin()]["station_name"]
            st.markdown(
                f'<div class="metric-card"><div class="metric-card-label">Minimum AQI</div><div class="metric-card-value">{df["aqi"].min():.0f}</div><div class="metric-card-delta">{min_station}</div></div>', unsafe_allow_html=True)
        with c3:
            max_station = df.loc[df["aqi"].idxmax()]["station_name"]
            st.markdown(
                f'<div class="metric-card"><div class="metric-card-label">Maximum AQI</div><div class="metric-card-value">{df["aqi"].max():.0f}</div><div class="metric-card-delta">{max_station}</div></div>', unsafe_allow_html=True)

    with c4:
        weather_data = fetch_weather_data()
        if weather_data and 'current' in weather_data:
            current = weather_data['current']
            desc, icon = get_weather_info(current.get('weather_code', 0))
            st.markdown(f"""
            <div class="weather-widget">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div class="metric-card-label">Current Weather</div>
                        <div class="weather-temp">{current['temperature_2m']:.1f}°C</div>
                    </div>
                    <div style="font-size: 3rem;">{icon}</div>
                </div>
                <div style="text-align: left; font-size: 0.9rem; color: #667eea; margin-top: 1rem; font-weight: 500;">
                    {desc}<br/>Humidity: {current['relative_humidity_2m']}%<br/>Wind: {current['wind_speed_10m']} km/h
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_personalized_health_advisor_tab(df):
    """Render the AI-powered personalized health advisor with Telegram integration"""
    st.markdown('<div class="section-header">🏥 AI Health Advisor - Get Personalized Recommendations</div>',
                unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3 style="color: white; margin-top: 0;">🤖 AI-Powered Personalized Health Advisory</h3>
        <p style="margin-bottom: 0; font-size: 1.05rem;">
        Get comprehensive, AI-generated health recommendations based on current AQI levels, your health profile, 
        and family members' conditions. Powered by Google Gemini AI with rule-based fallback for reliability.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current AQI
    avg_aqi = df['aqi'].mean() if not df.empty else 100
    
    # Display current AQI prominently
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.9); padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 2rem; border: 2px solid #ffd89b;">
        <h3 style="color: #764ba2; margin: 0;">Current Delhi AQI: <span style="color: #f5576c; font-size: 2rem;">{avg_aqi:.0f}</span></h3>
        <p style="color: #667eea; margin: 0.5rem 0 0 0; font-weight: 600;">{get_aqi_category(avg_aqi)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 👤 Individual Information")
        
        recipient_name = st.text_input(
            "Your Name",
            placeholder="e.g., Rajesh Kumar",
            help="Enter your name for personalized greeting"
        )
        
        # Health conditions with common Delhi NCR conditions
        health_condition_options = [
            "None - I'm Healthy",
            "Asthma",
            "COPD (Chronic Obstructive Pulmonary Disease)",
            "Heart Disease / Cardiovascular Issues",
            "Diabetes",
            "High Blood Pressure",
            "Allergies (Dust, Pollen)",
            "Bronchitis",
            "Pregnancy",
            "Elderly (Age 60+)",
            "Child (Under 12 years)",
            "Teenager (13-18 years)",
            "Lung Disease",
            "Other Respiratory Issues"
        ]
        
        selected_conditions = st.multiselect(
            "Your Health Conditions",
            health_condition_options,
            help="Select all conditions that apply to you"
        )
        
        # Filter out "None"
        user_conditions = [c for c in selected_conditions if "None" not in c]
    
    with col2:
        st.markdown("### 👨‍👩‍👧‍👦 Family Advisory (Optional)")
        
        include_family = st.checkbox(
            "Generate recommendations for family members",
            help="Get personalized advice for each family member"
        )
        
        family_members = []
        if include_family:
            num_members = st.number_input(
                "Number of family members",
                min_value=1,
                max_value=6,
                value=2,
                help="Include yourself and family members"
            )
            
            for i in range(int(num_members)):
                with st.expander(f"👤 Family Member {i+1}", expanded=(i==0)):
                    member_name = st.text_input(
                        "Name",
                        key=f"fam_name_{i}",
                        placeholder="e.g., Priya"
                    )
                    
                    member_age = st.number_input(
                        "Age",
                        min_value=0,
                        max_value=120,
                        value=25,
                        key=f"fam_age_{i}"
                    )
                    
                    member_conditions = st.multiselect(
                        "Health Conditions",
                        health_condition_options,
                        key=f"fam_cond_{i}",
                        help="Select all applicable conditions"
                    )
                    
                    if member_name:
                        family_members.append({
                            "name": member_name,
                            "age": member_age,
                            "health_conditions": [c for c in member_conditions if "None" not in c]
                        })
    
    st.markdown("---")
    
    # Telegram configuration
    st.markdown("### 📬 Telegram Delivery")
    
    col_tg1, col_tg2 = st.columns([2, 1])
    
    with col_tg1:
        telegram_chat_id = st.text_input(
            "Your Telegram Chat ID",
            placeholder="123456789",
            help="Get your Chat ID from @userinfobot on Telegram"
        )
    
    with col_tg2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ℹ️ How to get Chat ID"):
            st.info("""
            **Steps to get your Telegram Chat ID:**
            1. Open Telegram app
            2. Search for @userinfobot
            3. Start the bot
            4. Copy the ID it sends you
            5. Paste it above
            """)
    
    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Generate AI Health Advisory & Send to Telegram", type="primary", use_container_width=True):
        
        # Validation
        if not telegram_chat_id:
            st.error("⚠️ Please enter your Telegram Chat ID to receive recommendations!")
            return
        
        if not recipient_name:
            st.warning("💡 Tip: Add your name for a personalized greeting!")
        
        # Generate AI recommendation
        with st.spinner("🤖 AI is analyzing air quality data and generating personalized health recommendations..."):
            
            # Generate recommendation using AI or rule-based system
            recommendation = get_personalized_recommendation(
                aqi_value=avg_aqi,
                user_health_conditions=user_conditions if user_conditions else None,
                family_members=family_members if family_members else None
            )
            
            # Format message for Telegram
            message = format_recommendation_for_sms(recommendation, recipient_name)
            
            # Store in session state
            st.session_state['last_recommendation'] = recommendation
            st.session_state['last_message'] = message
            
            # Display the recommendation in beautiful card format
            st.markdown(f"""
            <div class="recommendation-card">
                <h3>🎯 Your Personalized Health Advisory</h3>
                <p style="font-size: 1.1rem; margin: 1rem 0; line-height: 1.6;">
                    <strong>AQI Level:</strong> {recommendation['aqi_value']:.0f} ({recommendation['aqi_category']})<br>
                    <strong>Risk Profile:</strong> {recommendation['risk_profile'].title()}<br>
                    <strong>Generated:</strong> {datetime.now().strftime('%d %B %Y, %I:%M %p')}<br>
                    <strong>Powered by:</strong> {'🤖 Google Gemini AI' if recommendation.get('ai_powered') else '📊 Rule-Based System'}
                </p>
                
                <div class="recommendation-section">
                    <h4>📋 Executive Summary</h4>
                    <p style="font-size: 1.05rem; line-height: 1.7;">{recommendation['summary']}</p>
                </div>
                
                <div class="recommendation-section">
                    <h4>⚠️ Critical Precautions</h4>
                    <ul class="recommendation-list">
                        {"".join([f"<li>{p}</li>" for p in recommendation['precautions']])}
                    </ul>
                </div>
                
                <div class="recommendation-section">
                    <h4>✅ Safe Activities</h4>
                    <ul class="recommendation-list">
                        {"".join([f"<li>{a}</li>" for a in recommendation['recommended_activities']])}
                    </ul>
                </div>
                
                <div class="recommendation-section">
                    <h4>🏥 Health Impact Analysis</h4>
                    <p style="font-size: 1.05rem; line-height: 1.7;">{recommendation['health_implications']}</p>
                </div>
                
                <div class="recommendation-section">
                    <h4>📍 Delhi NCR Context</h4>
                    <p style="font-size: 1.05rem; line-height: 1.7;">{recommendation['delhi_specific']}</p>
                </div>
                
                {'<div class="recommendation-section"><h4>👨‍👩‍👧‍👦 Family-Specific Guidance</h4><p style="font-size: 1.05rem; line-height: 1.7;">' + recommendation.get('family_specific', '') + '</p></div>' if 'family_specific' in recommendation else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Send via Telegram
            st.markdown("### 📤 Sending to Telegram...")
            
            if TELEGRAM_BOT_TOKEN:
                # Clean message for Telegram (remove excessive emojis for better readability)
                telegram_message = message
                
                with st.spinner("Sending to Telegram..."):
                    success, status_msg = send_telegram_notification(
                        TELEGRAM_BOT_TOKEN,
                        telegram_chat_id,
                        telegram_message
                    )
                    
                    if success:
                        st.success(f"""
                        ✅ **{status_msg}**
                        
                        Your personalized health advisory has been successfully delivered to your Telegram!
                        Check your Telegram app for the complete recommendation.
                        """)
                    else:
                        st.error(f"""
                        ❌ **Failed to send message**
                        
                        {status_msg}
                        
                        Please check:
                        - Your Chat ID is correct
                        - You have started a conversation with the bot
                        - The bot token is valid
                        """)
                        
                        # Show the message anyway
                        st.info("💡 You can still view and download the recommendation below")
            else:
                st.error("❌ Telegram bot is not configured. Please set TELEGRAM_BOT_TOKEN.")
            
            # Download option
            st.markdown("### 📥 Download Option")
            col_d1, col_d2 = st.columns([2, 1])
            
            with col_d1:
                st.download_button(
                    label="📥 Download Full Recommendation (Text)",
                    data=message,
                    file_name=f"aqi_advisory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col_d2:
                # Create JSON version
                import json
                json_data = json.dumps(recommendation, indent=2)
                st.download_button(
                    label="📊 Download as JSON",
                    data=json_data,
                    file_name=f"aqi_advisory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )


def render_map_tab(df):
    """Renders the interactive map of AQI stations."""
    st.markdown('<div class="section-header">📍 Interactive Air Quality Map</div>',
                unsafe_allow_html=True)

    if df.empty:
        st.warning("No monitoring stations found inside the Delhi boundary.")
        return

    # Add Legend
    st.markdown("""
    <div style="background-color: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 10px; border: 2px solid #e0e0e0; margin-bottom: 1rem;">
        <div style="font-weight: 700; color: #764ba2; margin-bottom: 0.75rem; font-size: 1.1rem;">AQI Color Legend</div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(0, 158, 96);"></div>
                <span style="color: #333; font-weight: 500;">Good (0-50)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(255, 214, 0);"></div>
                <span style="color: #333; font-weight: 500;">Moderate (51-100)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(249, 115, 22);"></div>
                <span style="color: #333; font-weight: 500;">Unhealthy for Sensitive (101-150)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(220, 38, 38);"></div>
                <span style="color: #333; font-weight: 500;">Unhealthy (151-200)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(147, 51, 234);"></div>
                <span style="color: #333; font-weight: 500;">Very Unhealthy (201-300)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(126, 34, 206);"></div>
                <span style="color: #333; font-weight: 500;">Hazardous (300+)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.pydeck_chart(pdk.Deck(
        map_style="light",
        initial_view_state=pdk.ViewState(
            latitude=DELHI_LAT, longitude=DELHI_LON, zoom=9.5, pitch=50),
        layers=[pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[lon, lat]',
            get_fill_color='color',
            get_radius=250,
            pickable=True,
            opacity=0.8,
            stroked=True,
            get_line_color=[0, 0, 0, 100],
            line_width_min_pixels=1,
        )],
        tooltip={"html": "<b>{station_name}</b><br/>AQI: {aqi}<br/>Category: {category}<br/>Last Updated: {last_updated}",
                 "style": {"color": "white"}}
    ))


def render_alerts_tab(df):
    """Renders health alerts and advice based on current AQI levels."""
    st.markdown('<div class="section-header">🔔 Health Alerts & Recommendations</div>',
                unsafe_allow_html=True)
    max_aqi = df['aqi'].max()
    advice = get_aqi_category_legacy(max_aqi)[3]
    st.info(
        f"**Current Situation:** Based on the highest AQI of **{max_aqi:.0f}**, the recommended action is: **{advice}**", icon="ℹ️")

    alerts = {
        "Hazardous": (df[df['aqi'] > 300], "alert-hazardous"),
        "Very Unhealthy": (df[(df['aqi'] > 200) & (df['aqi'] <= 300)], "alert-very-unhealthy"),
        "Unhealthy": (df[(df['aqi'] > 150) & (df['aqi'] <= 200)], "alert-unhealthy")
    }
    has_alerts = False
    for level, (subset, card_class) in alerts.items():
        if not subset.empty:
            has_alerts = True
            st.markdown(
                f"**{subset.iloc[0]['emoji']} {level} Conditions Detected**")
            for _, row in subset.sort_values('aqi', ascending=False).iterrows():
                st.markdown(
                    f'<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;"><span style="font-weight: 600;">{row["station_name"]}</span> <span style="font-weight: 700; font-size: 1.2rem;">AQI {row["aqi"]:.0f}</span></div>', unsafe_allow_html=True)

    if not has_alerts:
        st.success("✅ No significant air quality alerts at the moment. AQI levels are currently within the good to moderate range for most areas.", icon="✅")


def render_kriging_tab(df):
    st.subheader("Spatial Interpolation (Kriging)")
    delhi_bounds_tuple = (28.40, 28.88, 76.84, 77.35)
    delhi_polygon = st.session_state.get("delhi_polygon", None)

    if delhi_polygon is None:
        st.error("Delhi boundary could not be loaded.")
        return

    if len(df) < 3:
        st.error("Not enough AQI stations within Delhi boundary for kriging interpolation (minimum 3 required).")
        return

    with st.spinner("Performing spatial interpolation..."):
        try:
            lon_grid, lat_grid, z = perform_kriging_correct(
                df, delhi_bounds_tuple, polygon=delhi_polygon, resolution=250
            )

            st.session_state["kriging_output"] = (lon_grid, lat_grid, z)
            st.success("✅ Kriging interpolation completed successfully!")

            heatmap_df = pd.DataFrame({
                "lon": lon_grid.flatten(),
                "lat": lat_grid.flatten(),
                "aqi": z.flatten()
            })
            
            heatmap_df = heatmap_df.dropna(subset=['aqi'])

            fig = px.density_mapbox(
                heatmap_df,
                lat="lat",
                lon="lon",
                z="aqi",
                radius=15,
                center=dict(lat=28.6139, lon=77.2090),
                zoom=9.5,
                mapbox_style="carto-positron",
                color_continuous_scale=[
                    "#009E60", "#FFD600", "#F97316",
                    "#DC2626", "#9333EA", "#7E22CE"
                ],
                range_color=[0, 400],
                title="Interpolated AQI Heatmap across Delhi"
            )
            
            fig.update_layout(
                margin=dict(t=40, b=0, l=0, r=0),
                coloraxis_colorbar=dict(
                    title="AQI",
                    thicknessmode="pixels",
                    thickness=15,
                    lenmode="pixels",
                    len=300
                )
            )

            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error performing kriging: {str(e)}")


def render_analytics_tab(df):
    """Renders charts and data analytics."""
    st.markdown('<div class="section-header">📊 Data Analytics</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("**AQI Category Distribution**")
        category_counts = df['category'].value_counts()
        fig = px.pie(
            values=category_counts.values, names=category_counts.index, hole=0.4,
            color=category_counts.index,
            color_discrete_map={
                "Good": "#009E60", "Moderate": "#FFD600", "Unhealthy for Sensitive Groups": "#F97316",
                "Unhealthy": "#DC2626", "Very Unhealthy": "#9333EA", "Hazardous": "#7E22CE"
            }
        )
        fig.update_traces(textinfo='percent+label',
                          pull=[0.05]*len(category_counts.index))
        fig.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(255,255,255,0.9)',
            plot_bgcolor='rgba(255,255,255,0.9)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Top 10 Most Polluted Stations**")
        top_10 = df.nlargest(10, 'aqi').sort_values('aqi', ascending=True)
        fig = px.bar(
            top_10, x='aqi', y='station_name', orientation='h',
            color='aqi', color_continuous_scale=px.colors.sequential.Reds
        )
        fig.update_layout(
            xaxis_title="AQI",
            yaxis_title="",
            showlegend=False,
            margin=dict(t=20, b=20, l=0, r=20),
            paper_bgcolor='rgba(255,255,255,0.9)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            xaxis=dict(gridcolor='#DDDDDD'),
            yaxis=dict(gridcolor='#DDDDDD')
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Full Station Data**")
    display_df = df[['station_name', 'aqi', 'category',
                     'last_updated']].sort_values('aqi', ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_dummy_forecast_tab():
    """Render a dummy 24-hour AQI forecast using simulated data."""
    st.markdown('<div class="section-header">📈 24-Hour AQI Forecast (Sample)</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 1rem;">
        <p style="color: #764ba2; margin: 0; font-weight: 500;">
        This sample forecast simulates how the Air Quality Index (AQI) may change over the next 24 hours.
        </p>
    </div>
    """, unsafe_allow_html=True)

    hours = np.arange(0, 24)
    base_aqi = 120 + 40 * np.sin(hours / 3) + np.random.normal(0, 5, size=24)
    timestamps = [datetime.now() + timedelta(hours=i) for i in range(24)]
    forecast_df = pd.DataFrame({
        "timestamp": timestamps,
        "forecast_aqi": np.clip(base_aqi, 40, 300)
    })

    fig = px.line(
        forecast_df,
        x="timestamp",
        y="forecast_aqi",
        title="Predicted AQI Trend for Next 24 Hours (Simulated)",
        markers=True,
        line_shape="spline"
    )
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Predicted AQI",
        showlegend=False,
        margin=dict(t=40, b=20, l=0, r=20),
        paper_bgcolor='rgba(255,255,255,0.9)',
        plot_bgcolor='rgba(255,255,255,0.9)',
        title_font_color="#764ba2",
        font_color="#764ba2",
        xaxis=dict(gridcolor='#E3E3E3'),
        yaxis=dict(gridcolor='#E3E3E3')
    )

    st.plotly_chart(fig, use_container_width=True)

    avg_aqi = forecast_df["forecast_aqi"].mean()
    max_aqi = forecast_df["forecast_aqi"].max()
    min_aqi = forecast_df["forecast_aqi"].min()

    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 10px; border-left: 5px solid #667eea; margin-top: 1rem; color: #333;">
        <b>Average Forecasted AQI:</b> {avg_aqi:.1f}  
        <br><b>Expected Range:</b> {min_aqi:.1f} – {max_aqi:.1f}
        <br><b>Air Quality Outlook:</b> Moderate to Unhealthy range over the next day.
    </div>
    """, unsafe_allow_html=True)


# ==========================
# MAIN APP EXECUTION
# ==========================
aqi_data_raw = fetch_live_data()

if aqi_data_raw.empty:
    st.error("⚠️ **Could not fetch live AQI data.** The API may be down or there's a network issue. Please try again later.", icon="🚨")
    render_header(aqi_data_raw)
else:
    # Filter data to Delhi boundary
    delhi_gdf = st.session_state.get("delhi_gdf", None)
    delhi_polygon = st.session_state.get("delhi_polygon", None)
    
    aqi_data_filtered = pd.DataFrame()
    
    if delhi_polygon is not None:
        geometry = [Point(xy) for xy in zip(aqi_data_raw['lon'], aqi_data_raw['lat'])]
        stations_gdf = gpd.GeoDataFrame(aqi_data_raw, crs="epsg:4326", geometry=geometry)
        clipped_gdf = gpd.clip(stations_gdf, delhi_polygon)
        
        if not clipped_gdf.empty:
            aqi_data_filtered = pd.DataFrame(clipped_gdf.drop(columns='geometry'))
    
    if aqi_data_filtered.empty:
        st.warning("⚠️ **No monitoring stations found inside the Delhi boundary.** Showing all available data for the region.", icon="⚠️")
        aqi_data_to_display = aqi_data_raw
    else:
        st.success(f"✅ Loaded {len(aqi_data_filtered)} monitoring stations inside the Delhi boundary.", icon="🛰️")
        aqi_data_to_display = aqi_data_filtered

    render_header(aqi_data_to_display)

    # Tabs with AI Health Advisor as primary tab
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["🤖 AI Health Advisor", "🗺️ Live Map", "🔔 Alerts", "📊 Analytics", "📈 Forecast", "🔥 Kriging Heatmap"])

    with tab1:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_personalized_health_advisor_tab(aqi_data_to_display)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_map_tab(aqi_data_to_display)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_alerts_tab(aqi_data_to_display)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_analytics_tab(aqi_data_to_display)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_dummy_forecast_tab()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab6:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_kriging_tab(aqi_data_to_display)
            st.markdown('</div>', unsafe_allow_html=True)
