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

# Auto handle code from URL (for deployed version)
query_params = st.query_params
if "code" in query_params:
    st.session_state.auth_code = query_params["code"]

# Sidebar
st.sidebar.header("🔑 Strava Login")
client_id = st.sidebar.text_input("Client ID", type="password", key="cid")
client_secret = st.sidebar.text_input("Client Secret", type="password", key="csec")

client = Client()

if client_id and client_secret:
    if st.sidebar.button("Login with Strava"):
        auth_url = client.authorization_url(
            client_id=client_id,
            redirect_uri=st.runtime.get_instance()._get_base_url() or "http://localhost:8501",
            scope=["read", "activity:read"]
        )
        st.sidebar.markdown(f"[🔗 Authorize]({auth_url})")

    code = st.session_state.get("auth_code") or st.sidebar.text_input("Authorization Code", key="code_input")
    
    if code and st.sidebar.button("Connect"):
        try:
            token = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=code)
            st.session_state.token = token
            st.success("✅ Connected!")
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
            'moving_time_min': getattr(a.moving_time, 'total_seconds', lambda: getattr(a.moving_time, 'seconds', 0))() / 60,
            'elevation_m': float(a.total_elevation_gain or 0),
            'start_date': a.start_date.date() if a.start_date else None,
            'hr_avg': float(a.average_heartrate or 0),
        } for a in activities])
        
        if not df.empty:
            st.dataframe(df.head(10))
            # Tabs
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "🗺️ Maps"])
            with tab1:
                col1, col2 = st.columns(2)
                with col1: st.metric("Total Distance", f"{df['distance_km'].sum():.1f} km")
                with col2: st.metric("Activities", len(df))
                fig = px.bar(df, x='start_date', y='distance_km', color='sport_type', title="Distance Over Time")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                monthly = df.groupby(df['start_date'].astype('datetime64[ns]').dt.to_period('M'))['distance_km'].sum().reset_index()
                monthly['start_date'] = monthly['start_date'].dt.to_timestamp()
                st.plotly_chart(px.line(monthly, x='start_date', y='distance_km'))
            
            with tab3:
                m = folium.Map(location=[30.3, 78.0], zoom_start=8)
                st_folium(m, width=700)
        else:
            st.warning("No activities found.")
    except Exception as e:
        st.error(f"Data Error: {e}")
else:
    st.info("Login with Strava using the sidebar")

st.caption("Built for Robin's EnduraRank")
