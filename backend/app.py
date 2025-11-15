import streamlit as st
import pandas as pd
import numpy as np
import requests
import pydeck as pdk
import plotly.express as px
from datetime import datetime, timedelta
from krigging import perform_kriging_correct
from krigging import get_aqi_at_location
import geopandas as gpd
from shapely.geometry import Point
import pyproj
from shapely.ops import transform
import smtplib
from email.message import EmailMessage

# Import AI Agent Logic with Gemini
from agent_logic import (
    get_personalized_recommendation,
    get_aqi_trend_advice,
    get_delhi_specific_context,
    get_aqi_category
)

# ==========================
# PAGE CONFIGURATION
# ==========================
st.set_page_config(
    layout="wide",
    page_title="Delhi Air Quality Dashboard - AI Powered",
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
# EMAIL TO SMS CONFIGURATION
# ==========================
SENDER_EMAIL = "anumaliknr@gmail.com"
GMAIL_APP_PASSWORD = "xczo lasg vcek olqp"

SMS_GATEWAYS = {
    "Airtel": "@airtelmail.com",
    "Jio": "@jionet.com", 
    "Vi (Vodafone Idea)": "@myvi.in",
    "BSNL": "@bsnlmail.com",
    "AT&T (USA)": "@txt.att.net",
    "T-Mobile (USA)": "@tmomail.net",
    "Verizon (USA)": "@vtext.com",
    "Sprint (USA)": "@messaging.sprintpcs.com"
}

def send_sms_via_email(phone_number, carrier_gateway, message, subject="AQI Alert"):
    """Send SMS using Email-to-SMS gateway via Gmail SMTP"""
    try:
        phone_clean = ''.join(filter(str.isdigit, phone_number))
        gateway_address = f"{phone_clean}{carrier_gateway}"
        
        msg = EmailMessage()
        msg.set_content(message)
        msg["From"] = SENDER_EMAIL
        msg["To"] = gateway_address
        msg["Subject"] = subject
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        return True, f"SMS sent successfully to {phone_clean}"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Check Gmail credentials."
    except Exception as e:
        return False, f"SMS sending failed: {str(e)}"

def run_agent(aqi_value, conditions_list, forecast=None):
    """Run the AI agent to get personalized recommendations"""
    try:
        rec = get_personalized_recommendation(aqi_value, conditions_list or [])
        trend = get_aqi_trend_advice(aqi_value, forecast or [])
        ctx = get_delhi_specific_context(aqi_value, rec.get("risk_profile", "general"))
        return rec, trend, ctx
    except Exception as e:
        st.error(f"Agent error: {e}")
        # Return fallback data
        return {
            "aqi_value": aqi_value,
            "aqi_category": get_aqi_category(aqi_value),
            "summary": "Air quality information available.",
            "precautions": ["Monitor air quality", "Use protection when needed"],
            "recommended_activities": ["Stay informed", "Follow guidelines"],
            "ai_powered": False
        }, {"trend": "unknown", "advice": "Monitor conditions"}, {"seasonal_context": "N/A"}

# ==========================
# CUSTOM CSS FOR STYLING
# ==========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #90CAF9 100%);
    }

    header, footer, #MainMenu {
        visibility: hidden;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: #0D47A1;
        padding: 1.5rem 0 0.5rem 0;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(13, 71, 161, 0.2);
        letter-spacing: -1px;
    }

    .subtitle {
        font-size: 1.2rem;
        color: #1565C0;
        text-align: center;
        padding-bottom: 1.5rem;
        font-weight: 500;
    }

    .metric-card {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid #BBDEFB;
        box-shadow: 0 4px 20px rgba(33, 150, 243, 0.15);
        text-align: center;
        height: 100%;
    }
    .metric-card-label {
        font-size: 1rem;
        font-weight: 600;
        color: #1565C0;
        margin-bottom: 0.5rem;
    }
    .metric-card-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0D47A1;
        margin: 0.5rem 0;
    }
    .metric-card-delta {
        font-size: 0.9rem;
        color: #1976D2;
        font-weight: 500;
    }

    .weather-widget {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid #BBDEFB;
        box-shadow: 0 4px 20px rgba(33, 150, 243, 0.15);
        height: 100%;
    }
    .weather-temp {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0D47A1;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent;
        padding: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        background-color: white;
        border-radius: 15px;
        padding: 1rem 2rem;
        border: 2px solid #BBDEFB;
        color: #262730;
        box-shadow: 0 2px 10px rgba(33, 150, 243, 0.1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E3F2FD;
        border-color: #2196F3;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white !important;
        border-color: #1976D2;
    }

    .content-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid #BBDEFB;
        box-shadow: 0 10px 40px rgba(33, 150, 243, 0.2);
        margin-top: 1.5rem;
    }

    .alert-card {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        font-weight: 600;
    }
    .alert-hazardous { 
        background: linear-gradient(135deg, #EF5350 0%, #E53935 100%);
        box-shadow: 0 4px 15px rgba(239, 83, 80, 0.3);
    }
    .alert-very-unhealthy { 
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
    }
    .alert-unhealthy { 
        background: linear-gradient(135deg, #FFA726 0%, #FB8C00 100%);
        box-shadow: 0 4px 15px rgba(255, 167, 38, 0.3);
    }

    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0D47A1;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #BBDEFB;
    }

    .ai-message-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.2);
    }
    .ai-message-card h3 {
        color: #2E7D32;
        margin-top: 0;
        font-size: 1.3rem;
    }
    .ai-message-card p {
        color: #388E3C;
        line-height: 1.6;
        margin-bottom: 0;
    }
    
    .ai-badge {
        display: inline-block;
        background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stAlert"] {
        background-color: white;
        border-left: 5px solid #2196F3;
        border-radius: 10px;
        color: #0D47A1;
    }

    div[data-testid="stSuccess"] {
        background-color: white;
        border-left: 5px solid #4CAF50;
        border-radius: 10px;
        color: #2E7D32;
    }

    div[data-testid="stError"] {
        background-color: white;
        border-left: 5px solid #EF5350;
        border-radius: 10px;
        color: #C62828;
    }

    div[data-testid="stDataFrame"] {
        border: 2px solid #BBDEFB;
        border-radius: 10px;
        background-color: white;
    }
    
    div[data-testid="stPlotlyChart"] {
        background-color: white;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .element-container {
        background-color: transparent;
    }
    
    .block-container {
        background-color: transparent;
        padding-top: 2rem;
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
                get_aqi_category_visual).apply(pd.Series)
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            df = df.dropna(subset=['lat', 'lon'])
            return df
        return pd.DataFrame()
    except requests.RequestException:
        return pd.DataFrame()


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


def get_aqi_category_visual(aqi):
    """Categorizes AQI value for visual display"""
    category_name = get_aqi_category(aqi)
    
    visual_mapping = {
        "Good": ([0, 158, 96], "✅", "Enjoy outdoor activities."),
        "Moderate": ([255, 214, 0], "🟡", "Unusually sensitive people should consider reducing prolonged exertion."),
        "Unhealthy for Sensitive Groups": ([249, 115, 22], "🟠", "Sensitive groups should reduce prolonged exertion."),
        "Unhealthy": ([220, 38, 38], "🔴", "Everyone may begin to experience health effects."),
        "Very Unhealthy": ([147, 51, 234], "🟣", "Health alert: everyone may experience more serious health effects."),
        "Hazardous": ([126, 34, 206], "☠️", "Health warnings of emergency conditions."),
        "Severe": ([107, 0, 25], "⚠️", "Severe health emergency."),
        "Severe+": ([75, 0, 18], "🚨", "Extreme health emergency.")
    }
    
    color, emoji, advice = visual_mapping.get(category_name, ([128, 128, 128], "❓", "Unknown"))
    return category_name, color, emoji, advice


def render_kriging_tab(df):
    st.subheader("Spatial Interpolation (Kriging)")
    delhi_bounds_tuple = (28.40, 28.88, 76.84, 77.35)
    delhi_polygon = st.session_state.get("delhi_polygon", None)

    if delhi_polygon is None:
        st.error("Delhi boundary could not be loaded.")
        return

    if len(df) < 3:
        st.error("Not enough AQI stations for kriging interpolation (minimum 3 required).")
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
                heatmap_df, lat="lat", lon="lon", z="aqi", radius=15,
                center=dict(lat=28.6139, lon=77.2090), zoom=9.5,
                mapbox_style="carto-positron",
                color_continuous_scale=["#009E60", "#FFD600", "#F97316", "#DC2626", "#9333EA", "#7E22CE"],
                range_color=[0, 400],
                title="Interpolated AQI Heatmap across Delhi"
            )
            
            fig.update_layout(
                margin=dict(t=40, b=0, l=0, r=0),
                coloraxis_colorbar=dict(title="AQI", thicknessmode="pixels", thickness=15, lenmode="pixels", len=300)
            )

            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error performing kriging: {str(e)}")


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
    st.markdown('<div class="main-title">🤖 Delhi Air Quality Dashboard - AI Powered</div>', unsafe_allow_html=True)
    last_update_time = df['last_updated'].max() if not df.empty and 'last_updated' in df.columns else "N/A"
    st.markdown(f'<p class="subtitle">Real-time monitoring with Gemini AI • Last updated: {last_update_time}</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    if not df.empty:
        with c1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-card-label">Average AQI</div><div class="metric-card-value">{df["aqi"].mean():.1f}</div><div class="metric-card-delta">{get_aqi_category(df["aqi"].mean())}</div></div>',
                unsafe_allow_html=True)
        with c2:
            min_station = df.loc[df["aqi"].idxmin()]["station_name"]
            st.markdown(
                f'<div class="metric-card"><div class="metric-card-label">Minimum AQI</div><div class="metric-card-value">{df["aqi"].min():.0f}</div><div class="metric-card-delta">{min_station}</div></div>',
                unsafe_allow_html=True)
        with c3:
            max_station = df.loc[df["aqi"].idxmax()]["station_name"]
            st.markdown(
                f'<div class="metric-card"><div class="metric-card-label">Maximum AQI</div><div class="metric-card-value">{df["aqi"].max():.0f}</div><div class="metric-card-delta">{max_station}</div></div>',
                unsafe_allow_html=True)

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
                <div style="text-align: left; font-size: 0.9rem; color: #1976D2; margin-top: 1rem; font-weight: 500;">
                    {desc}<br/>Humidity: {current['relative_humidity_2m']}%<br/>Wind: {current['wind_speed_10m']} km/h
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="weather-widget">
                <div class="metric-card-label">Current Weather</div>
                <div style="color: #1976D2; margin-top: 1rem;">Weather data unavailable</div>
            </div>
            """, unsafe_allow_html=True)


def render_map_tab(df):
    """Renders the interactive map of AQI stations."""
    st.markdown('<div class="section-header">📍 Interactive Air Quality Map (Stations inside Delhi)</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No monitoring stations found inside the Delhi boundary.")
        return

    st.markdown("""
    <div style="background-color: white; padding: 1rem; border-radius: 10px; border: 2px solid #BBDEFB; margin-bottom: 1rem;">
        <div style="font-weight: 700; color: #0D47A1; margin-bottom: 0.75rem; font-size: 1.1rem;">AQI Color Legend</div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(0, 158, 96);"></div>
                <span style="color: #1E293B; font-weight: 500;">Good (0-50)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(255, 214, 0);"></div>
                <span style="color: #1E293B; font-weight: 500;">Moderate (51-100)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(249, 115, 22);"></div>
                <span style="color: #1E293B; font-weight: 500;">Unhealthy for Sensitive (101-150)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(220, 38, 38);"></div>
                <span style="color: #1E293B; font-weight: 500;">Unhealthy (151-200)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(147, 51, 234);"></div>
                <span style="color: #1E293B; font-weight: 500;">Very Unhealthy (201-300)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: rgb(126, 34, 206);"></div>
                <span style="color: #1E293B; font-weight: 500;">Hazardous (300+)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.pydeck_chart(pdk.Deck(
        map_style="light",
        initial_view_state=pdk.ViewState(latitude=DELHI_LAT, longitude=DELHI_LON, zoom=9.5, pitch=50),
        layers=[pdk.Layer(
            "ScatterplotLayer", data=df, get_position='[lon, lat]', get_fill_color='color',
            get_radius=250, pickable=True, opacity=0.8, stroked=True,
            get_line_color=[0, 0, 0, 100], line_width_min_pixels=1,
        )],
        tooltip={"html": "<b>{station_name}</b><br/>AQI: {aqi}<br/>Category: {category}<br/>Last Updated: {last_updated}",
                 "style": {"color": "white"}}
    ))


def render_alerts_tab(df):
    """Renders health alerts and advice based on current AQI levels."""
    st.markdown('<div class="section-header">🔔 Health Alerts & Recommendations</div>', unsafe_allow_html=True)
    max_aqi = df['aqi'].max()
    advice = get_aqi_category_visual(max_aqi)[2]
    st.info(f"**Current Situation:** Based on the highest AQI of **{max_aqi:.0f}**, the recommended action is: **{advice}**", icon="ℹ️")

    alerts = {
        "Hazardous": (df[df['aqi'] > 300], "alert-hazardous"),
        "Very Unhealthy": (df[(df['aqi'] > 200) & (df['aqi'] <= 300)], "alert-very-unhealthy"),
        "Unhealthy": (df[(df['aqi'] > 150) & (df['aqi'] <= 200)], "alert-unhealthy")
    }
    has_alerts = False
    for level, (subset, card_class) in alerts.items():
        if not subset.empty:
            has_alerts = True
            st.markdown(f"**{subset.iloc[0]['emoji']} {level} Conditions Detected**")
            for _, row in subset.sort_values('aqi', ascending=False).iterrows():
                st.markdown(
                    f'<div class="alert-card {card_class}"><span style="font-weight: 600;">{row["station_name"]}</span> <span style="font-weight: 700; font-size: 1.2rem;">AQI {row["aqi"]:.0f}</span></div>',
                    unsafe_allow_html=True)

    if not has_alerts:
        st.success("✅ No significant air quality alerts at the moment.", icon="✅")


def render_alert_subscription_tab(df):
    st.subheader("📩 Real-Time AQI Alerts (via SMS) - AI Powered")

    polygon = st.session_state.get("delhi_polygon", None)
    if polygon is None:
        st.error("Delhi boundary polygon not loaded.")
        return

    kriging_data = st.session_state.get("kriging_output", None)
    if kriging_data is None:
        st.info("🔄 Generating kriging interpolation automatically...")
        
        if len(df) < 3:
            st.error("Not enough AQI stations for interpolation (minimum 3 required).")
            return
            
        delhi_bounds_tuple = (28.40, 28.88, 76.84, 77.35)
        
        try:
            with st.spinner("Performing spatial interpolation..."):
                lon_grid, lat_grid, z_grid = perform_kriging_correct(
                    df, delhi_bounds_tuple, polygon=polygon, resolution=200
                )
                st.session_state["kriging_output"] = (lon_grid, lat_grid, z_grid)
                st.success("✅ Kriging data generated successfully!")
                kriging_data = (lon_grid, lat_grid, z_grid)
        except Exception as e:
            st.error(f"Error generating kriging data: {str(e)}")
            return
    
    lon_grid, lat_grid, z_grid = kriging_data

    st.markdown("### 📍 Select Your Location")
    
    location_method = st.radio(
        "Choose how to provide your location:",
        ["🗺️ Select from Map/Dropdown", "✍️ Enter Coordinates Manually"],
        horizontal=True
    )
    
    user_lat = None
    user_lon = None
    
    if location_method == "🗺️ Select from Map/Dropdown":
        st.info("💡 Select a popular location in Delhi or choose from monitoring stations")
        
        popular_locations = {
            "Connaught Place": (28.6315, 77.2167),
            "India Gate": (28.6129, 77.2295),
            "Red Fort": (28.6562, 77.2410),
            "Qutub Minar": (28.5244, 77.1855),
            "Lotus Temple": (28.5535, 77.2588),
            "Chandni Chowk": (28.6506, 77.2303),
            "Karol Bagh": (28.6519, 77.1906),
            "Dwarka": (28.5921, 77.0460),
            "Rohini": (28.7496, 77.0670),
            "Nehru Place": (28.5494, 77.2501)
        }
        
        station_locations = {}
        for _, row in df.iterrows():
            station_locations[f"📍 {row['station_name']} (AQI: {row['aqi']:.0f})"] = (row['lat'], row['lon'])
        
        all_locations = {**popular_locations, **station_locations}
        
        selected_location = st.selectbox("Select Location:", options=list(all_locations.keys()))
        
        user_lat, user_lon = all_locations[selected_location]
        st.success(f"✅ Selected: {selected_location} ({user_lat:.4f}, {user_lon:.4f})")
        
    else:
        st.info("💡 Enter latitude and longitude coordinates")
        col1, col2 = st.columns(2)
        with col1:
            user_lat = st.number_input("Latitude", format="%.6f", step=0.000001, value=28.6139)
        with col2:
            user_lon = st.number_input("Longitude", format="%.6f", step=0.000001, value=77.2090)

    st.markdown("---")
    st.markdown("### 📱 SMS Alert Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        phone_number = st.text_input(
            "Phone Number (with country code)", 
            placeholder="+919876543210 or 919876543210",
            help="Enter phone number with country code (e.g., +91 for India)."
        )
        
    with col2:
        carrier_name = st.selectbox(
            "Select Carrier (for Gateway)",
            options=list(SMS_GATEWAYS.keys()),
            help="Select your mobile carrier to route the SMS correctly."
        )

    if st.button("🚀 Get AI-Powered AQI Alert via SMS", type="primary", use_container_width=True):
        if not phone_number:
            st.warning("⚠️ Please enter a phone number!")
            return

        if user_lat is None or user_lon is None:
            st.warning("⚠️ Please provide your location!")
            return

        try:
            aqi_value, outside = get_aqi_at_location(user_lat, user_lon, lat_grid, lon_grid, z_grid, polygon)

            if np.isnan(aqi_value):
                st.error("❌ Could not determine AQI for this location.")
                return

            if outside:
                st.warning("⚠️ Your location is outside Delhi boundary. Using nearest interpolated value.")

            # Get AI-powered recommendations
            with st.spinner("🤖 AI Agent analyzing air quality..."):
                rec, trend, ctx = run_agent(aqi_value, [])

            # Build AI-powered message
            message = f"""🤖 AI-Powered Delhi AQI Alert

📍 Location: {user_lat:.4f}, {user_lon:.4f}
📊 AQI: {int(aqi_value)} • {rec['aqi_category']}

🧠 AI Analysis:
{rec['summary'][:120]}...

⚠️ Key Precautions:
{', '.join(rec['precautions'][:2])}

🌆 Delhi Context:
{ctx.get('seasonal_context', 'N/A')[:100]}

Powered by Gemini AI
Stay safe!
"""
            gateway = SMS_GATEWAYS[carrier_name]
            
            with st.spinner("📤 Sending AI-powered SMS..."):
                success, status_msg = send_sms_via_email(phone_number, gateway, message)
                
                if success:
                    st.success(f"✅ {status_msg}")
                    st.info("ℹ️ AI-powered alert sent! SMS delivery depends on carrier gateway.")
                    
                    # Show what was sent
                    with st.expander("📧 View AI-Generated Alert"):
                        st.text(message)
                else:
                    st.error(f"❌ Failed: {status_msg}")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


def render_dummy_forecast_tab():
    """Render a dummy 24-hour AQI forecast."""
    st.markdown('<div class="section-header">📈 24-Hour AQI Forecast (Sample)</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #E3F2FD; padding: 1rem; border-radius: 10px; border-left: 4px solid #2196F3; margin-bottom: 1rem;">
        <p style="color: #0D47A1; margin: 0; font-weight: 500;">
        This sample forecast simulates AQI changes over the next 24 hours.
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
        forecast_df, x="timestamp", y="forecast_aqi",
        title="Predicted AQI Trend for Next 24 Hours (Simulated)",
        markers=True, line_shape="spline"
    )
    fig.update_layout(
        xaxis_title="Time", yaxis_title="Predicted AQI", showlegend=False,
        margin=dict(t=40, b=20, l=0, r=20), paper_bgcolor='white', plot_bgcolor='white',
        title_font_color="#0D47A1", font_color="#0D47A1",
        xaxis=dict(gridcolor='#E3F2FD'), yaxis=dict(gridcolor='#E3F2FD')
    )

    st.plotly_chart(fig, use_container_width=True)

    avg_aqi = forecast_df["forecast_aqi"].mean()
    max_aqi = forecast_df["forecast_aqi"].max()
    min_aqi = forecast_df["forecast_aqi"].min()

    st.markdown(f"""
    <div style="background-color: white; padding: 1rem; border-radius: 10px; border-left: 5px solid #1976D2; margin-top: 1rem; color: #1E293B;">
        <b>Average Forecasted AQI:</b> {avg_aqi:.1f}  
        <br><b>Expected Range:</b> {min_aqi:.1f} – {max_aqi:.1f}
        <br><b>Air Quality Outlook:</b> Moderate to Unhealthy range expected.
    </div>
    """, unsafe_allow_html=True)


def render_analytics_tab(df):
    """Renders charts and data analytics."""
    st.markdown('<div class="section-header">📊 Data Analytics</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("**AQI Category Distribution**")
        category_counts = df['category'].value_counts()
        fig = px.pie(
            values=category_counts.values, names=category_counts.index, hole=0.4,
            color=category_counts.index,
            color_discrete_map={
                "Good": "#009E60", "Moderate": "#FFD600", 
                "Unhealthy for Sensitive Groups": "#F97316",
                "Unhealthy": "#DC2626", "Very Unhealthy": "#9333EA", 
                "Hazardous": "#7E22CE"
            }
        )
        fig.update_traces(textinfo='percent+label', pull=[0.05]*len(category_counts.index))
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), 
                         paper_bgcolor='#F5F5F5', plot_bgcolor='#F5F5F5')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Top 10 Most Polluted Stations**")
        top_10 = df.nlargest(10, 'aqi').sort_values('aqi', ascending=True)
        fig = px.bar(
            top_10, x='aqi', y='station_name', orientation='h',
            color='aqi', color_continuous_scale=px.colors.sequential.Reds
        )
        fig.update_layout(
            xaxis_title="AQI", yaxis_title="", showlegend=False,
            margin=dict(t=20, b=20, l=0, r=20), paper_bgcolor='#F5F5F5', 
            plot_bgcolor='#F5F5F5',
            xaxis=dict(gridcolor='#DDDDDD'), yaxis=dict(gridcolor='#DDDDDD')
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Full Station Data**")
    display_df = df[['station_name', 'aqi', 'category', 'last_updated']].sort_values('aqi', ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ==========================
# MAIN APP EXECUTION
# ==========================
aqi_data_raw = fetch_live_data()

if aqi_data_raw.empty:
    st.error("⚠️ **Could not fetch live AQI data.** Please try again later.", icon="🚨")
    render_header(aqi_data_raw)
else:
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
        st.warning("⚠️ **No stations inside Delhi boundary.** Showing all available data.", icon="⚠️")
        aqi_data_to_display = aqi_data_raw
    else:
        st.success(f"✅ Loaded {len(aqi_data_filtered)} stations inside Delhi boundary.", icon="🛰️")
        aqi_data_to_display = aqi_data_filtered

    render_header(aqi_data_to_display)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🗺️ Live Map",
        "🔔 Alerts & Health",
        "📊 Analytics",
        "📱 SMS Alerts",
        "📈 Forecast",
        "🔥 Kriging Heatmap",
        "🧍 Individual Advisor",
        "👨‍👩‍👧 Family Advisor"
    ])

    with tab1:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_map_tab(aqi_data_to_display)
            st.markdown('</div>', unsafe_allow_html=True)
            
    with tab2:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_alerts_tab(aqi_data_to_display)
            st.markdown('</div>', unsafe_allow_html=True)
            
    with tab3:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_analytics_tab(aqi_data_to_display)
            st.markdown('</div>', unsafe_allow_html=True)
            
    with tab4:
        with st.container():
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            render_alert_subscription_tab(aqi_data_to_display)
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
    
    with tab7:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("🤖 AI-Powered Personal AQI Advisor")
        
        # Check if Gemini is available
        try:
            from agent_logic import GEMINI_AVAILABLE, GEMINI_API_KEY
            if GEMINI_AVAILABLE and GEMINI_API_KEY:
                st.markdown('<span class="ai-badge">🤖 Powered by Gemini AI</span>', unsafe_allow_html=True)
            else:
                st.info("💡 Set GEMINI_API_KEY environment variable to enable AI-powered recommendations")
        except:
            pass

        if aqi_data_to_display.empty:
            st.warning("No AQI data available.")
        else:
            aqi_data_to_display['dist'] = aqi_data_to_display.apply(
                lambda r: ((r['lat']-DELHI_LAT)**2 + (r['lon']-DELHI_LON)**2)**0.5, axis=1
            )
            nearest = aqi_data_to_display.loc[aqi_data_to_display['dist'].idxmin()]
            est_aqi = nearest['aqi']

            st.metric("Estimated AQI at Your Location", int(est_aqi), 
                     delta=f"{get_aqi_category(est_aqi)}")

            st.markdown("#### 🏥 Your Health Profile")
            conds = st.text_input(
                "Enter your health conditions (comma-separated):",
                placeholder="e.g., asthma, child, elderly, pregnant",
                help="Be specific: asthma, COPD, heart disease, pregnant, child, elderly, etc."
            )
            cond_list = [c.strip() for c in conds.split(",") if c.strip()]
            
            if cond_list:
                st.info(f"📋 Health conditions: {', '.join(cond_list)}")

            if st.button("🤖 Get AI-Powered Personalized Advice", type="primary", use_container_width=True):
                with st.spinner("🤖 AI Agent analyzing your situation..."):
                    rec, trend, ctx = run_agent(est_aqi, cond_list)

                # Display AI-powered recommendations
                ai_badge = "🤖 AI" if rec.get("ai_powered") else "📋 Rules"
                
                st.markdown(
                    f"""<div class='ai-message-card'>
                    <span class="ai-badge">{ai_badge}</span>
                    <h3>{rec['aqi_category']} (AQI {rec['aqi_value']:.0f})</h3>
                    <p>{rec['summary']}</p>
                    </div>""",
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander("⚠️ Precautions", expanded=True):
                        for p in rec["precautions"]:
                            st.write("• " + p)

                with col2:
                    with st.expander("✅ Recommended Activities", expanded=True):
                        for a in rec["recommended_activities"]:
                            st.write("• " + a)

                with st.expander("🏥 Health Implications"):
                    st.write(rec.get("health_implications", "No specific health implications noted."))

                with st.expander("🌆 Delhi-Specific Context"):
                    st.write(ctx.get("seasonal_context", "No specific context available."))
                
                # Show trend if available
                if trend and trend.get("trend") != "unknown":
                    st.markdown("#### 📈 Trend Analysis")
                    trend_icon = "⬆️" if trend["trend"] == "worsening" else "⬇️" if trend["trend"] == "improving" else "➡️"
                    st.info(f"{trend_icon} **{trend['trend'].title()}:** {trend['advice']}")

        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab8:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("👨‍👩‍👧 AI-Powered Family AQI Advisor")
        
        # Check if Gemini is available
        try:
            from agent_logic import GEMINI_AVAILABLE, GEMINI_API_KEY
            if GEMINI_AVAILABLE and GEMINI_API_KEY:
                st.markdown('<span class="ai-badge">🤖 Powered by Gemini AI</span>', unsafe_allow_html=True)
        except:
            pass

        if "family" not in st.session_state:
            st.session_state.family = []

        st.markdown("#### 👥 Add Family Members")
        
        with st.form("add_family"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name:", placeholder="e.g., John")
                age = st.number_input("Age:", 1, 120, 30)
            with col2:
                conds = st.text_input(
                    "Health conditions:", 
                    placeholder="e.g., asthma, child",
                    help="Enter relevant health conditions or age group"
                )
            
            submit = st.form_submit_button("➕ Add Family Member", use_container_width=True)
            if submit and name:
                st.session_state.family.append({
                    "name": name,
                    "age": age,
                    "conds": [c.strip() for c in conds.split(",") if c.strip()]
                })
                st.success(f"✅ Added {name} to family members")
                st.rerun()

        if st.session_state.family:
            st.markdown("#### 👨‍👩‍👧‍👦 Current Family Members")
            
            # Display family members in a nice format
            for idx, m in enumerate(st.session_state.family):
                col1, col2 = st.columns([4, 1])
                with col1:
                    conditions_text = ', '.join(m['conds']) if m['conds'] else 'No specific conditions'
                    st.write(f"**{m['name']}** • {m['age']} years • {conditions_text}")
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}", help=f"Remove {m['name']}"):
                        st.session_state.family.pop(idx)
                        st.rerun()

            st.markdown("---")
            
            if st.button("🤖 Generate AI Family Recommendations", type="primary", use_container_width=True):
                if aqi_data_to_display.empty:
                    st.warning("No AQI data available for analysis.")
                else:
                    est_aqi = aqi_data_to_display['aqi'].mean()
                    
                    st.markdown(f"### 📊 Family Analysis for AQI {est_aqi:.0f}")
                    
                    with st.spinner("🤖 AI analyzing recommendations for each family member..."):
                        for m in st.session_state.family:
                            rec, _, _ = run_agent(est_aqi, m['conds'])
                            
                            ai_badge = "🤖" if rec.get("ai_powered") else "📋"
                            
                            st.markdown(
                                f"""<div class='metric-card' style='text-align: left; margin: 1rem 0;'>
                                <h4>{ai_badge} {m['name']} ({m['age']} years)</h4>
                                <p><b>Category:</b> {rec['aqi_category']}</p>
                                <p>{rec['summary']}</p>
                                <details>
                                <summary style='cursor: pointer; color: #2196F3; font-weight: 600;'>View Details</summary>
                                <div style='margin-top: 1rem;'>
                                <p><b>Key Precautions:</b></p>
                                <ul>{''.join([f'<li>{p}</li>' for p in rec['precautions'][:3]])}</ul>
                                <p><b>Recommended Activities:</b></p>
                                <ul>{''.join([f'<li>{a}</li>' for a in rec['recommended_activities'][:3]])}</ul>
                                </div>
                                </details>
                                </div>""",
                                unsafe_allow_html=True
                            )
            
            if st.button("🗑️ Clear All Family Members"):
                st.session_state.family = []
                st.rerun()
        else:
            st.info("👥 No family members added yet. Use the form above to add family members.")

        st.markdown('</div>', unsafe_allow_html=True)
