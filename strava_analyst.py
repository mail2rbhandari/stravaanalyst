import streamlit as st
import os
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from stravalib.client import Client

os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

st.set_page_config(page_title="EnduraAnalyst", layout="wide")
st.title("🏃‍♂️ EnduraAnalyst: Live Strava Personal Analyst")
st.markdown("### Your Personal Endurance Sports Coach")

# Auto code handling
if "code" in st.query_params:
    st.session_state.auth_code = st.query_params["code"]

st.sidebar.header("🔑 Strava Login")
client_id = st.sidebar.text_input("Client ID", type="password", key="cid")
client_secret = st.sidebar.text_input("Client Secret", type="password", key="csec")

if client_id and client_secret:
    if st.sidebar.button("Login with Strava"):
        redirect_uri = "https://stravaanalyst1.streamlit.app"  # Your deployed URL
        auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=read,activity:read"
        st.sidebar.markdown(f"[🔗 Authorize on Strava]({auth_url})")
        st.sidebar.info("After approval, the code will be in URL - click Connect below")

    code = st.session_state.get("auth_code") or st.sidebar.text_input("Authorization Code", key="code_input")
    
    if code and st.sidebar.button("Exchange & Connect"):
        try:
            client = Client()
            token = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=code)
            st.session_state.token = token
            st.success("✅ Connected Successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Auth Error: {e}")

# Main App
if "token" in st.session_state:
    client = Client(access_token=st.session_state.token['access_token'])
    st.success("✅ Live Connection Active")
    
    try:
        activities = list(client.get_activities(limit=100))
        df = pd.DataFrame([{
            'name': a.name,
            'sport_type': str(a.sport_type),
            'distance_km': a.distance / 1000 if a.distance else 0,
            'moving_time_min': getattr(a.moving_time, 'total_seconds', lambda: 0)() / 60,
            'elevation_m': float(a.total_elevation_gain or 0),
            'start_date': a.start_date.date() if a.start_date else None,
            'hr_avg': float(a.average_heartrate or 0),
        } for a in activities])
        
        if not df.empty:
            st.dataframe(df.head())
            tab1, tab2 = st.tabs(["Overview", "Trends"])
            with tab1:
                st.metric("Total Distance", f"{df['distance_km'].sum():.1f} km")
                fig = px.bar(df, x='start_date', y='distance_km', color='sport_type')
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Data Error: {e}")
else:
    st.info("Login using the sidebar")

st.caption("Built for Robin - EnduraRank MVP")
