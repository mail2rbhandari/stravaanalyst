import streamlit as st
import os
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from stravalib.client import Client
from datetime import datetime

os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

st.set_page_config(page_title="EnduraAnalyst", layout="wide")
st.title("🏃‍♂️ EnduraAnalyst: Live Strava Personal Analyst")
st.markdown("### Your Personal Endurance Sports Coach")

# Sidebar OAuth
st.sidebar.header("🔑 Strava Login")
client_id = st.sidebar.text_input("Client ID", type="password", key="client_id")
client_secret = st.sidebar.text_input("Client Secret", type="password", key="client_secret")

client = Client()

if client_id and client_secret:
    if st.sidebar.button("Login with Strava"):
        auth_url = client.authorization_url(
            client_id=client_id,
            redirect_uri="http://localhost:8501",
            scope=["read", "activity:read"]
        )
        st.sidebar.markdown(f"[🔗 Authorize on Strava]({auth_url})")
        st.sidebar.info("After login → copy 'code=...' from browser URL")

    code = st.sidebar.text_input("Authorization Code", key="auth_code")
    
    if code and st.sidebar.button("Exchange & Connect"):
        try:
            token = client.exchange_code_for_token(
                client_id=client_id, 
                client_secret=client_secret, 
                code=code
            )
            st.session_state.token = token
            st.sidebar.success("✅ Connected!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# Main Dashboard
if "token" in st.session_state:
    client = Client(access_token=st.session_state.token['access_token'])
    st.success("✅ Live Connection Active")
    
    try:
        activities = list(client.get_activities(limit=100))
        df = pd.DataFrame([{
            'name': a.name,
            'sport_type': str(a.sport_type),
            'distance_km': a.distance / 1000,
            'moving_time_min': a.moving_time.total_seconds() / 60,
            'elevation_m': a.total_elevation_gain or 0,
            'start_date': a.start_date.date(),
            'hr_avg': a.average_heartrate or 0,
        } for a in activities])
        
        st.dataframe(df.head())
        st.success(f"Loaded {len(df)} activities!")
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Maps"])
        with tab1:
            st.metric("Total Distance", f"{df['distance_km'].sum():.1f} km")
            fig = px.bar(df, x='start_date', y='distance_km', color='sport_type')
            st.plotly_chart(fig)
        
        with tab2:
            st.plotly_chart(px.line(df.groupby('start_date')['distance_km'].sum().reset_index(), x='start_date', y='distance_km'))
        
        with tab3:
            m = folium.Map(location=[30.3, 78.0], zoom_start=8)
            st_folium(m)
            
    except Exception as e:
        st.error(f"Data fetch error: {e}")
else:
    st.info("Login via sidebar to load your Strava data")