import streamlit as st
import os
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from stravalib.client import Client
import numpy as np
from sklearn.linear_model import LinearRegression
from folium.plugins import HeatMap

os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

st.set_page_config(page_title="EnduraAnalyst", layout="wide")
st.title("🏃‍♂️ EnduraAnalyst Pro")
st.markdown("### Serious Endurance Athlete Analytics")

st.sidebar.header("🔑 Strava Login")
client_id = st.sidebar.text_input("Client ID", type="password", key="cid")
client_secret = st.sidebar.text_input("Client Secret", type="password", key="csec")

if client_id and client_secret:
    if st.sidebar.button("Login with Strava"):
        redirect_uri = "https://stravaanalyst1.streamlit.app"
        auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=read,activity:read"
        st.sidebar.markdown(f"[🔗 Authorize on Strava]({auth_url})")
        st.sidebar.info("After approval, paste the code from URL")

    code = st.sidebar.text_input("Authorization Code", key="code_input")
    
    if code and st.sidebar.button("Exchange & Connect"):
        try:
            client = Client()
            token = client.exchange_code_for_token(client_id=client_id, client_secret=client_secret, code=code)
            st.session_state.token = token
            st.success("✅ Connected!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

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
            df['pace_min_km'] = df['moving_time_min'] / df['distance_km'].replace(0, float('nan'))
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends & Predictions", "🗺️ Routes", "🔥 Heatmap"])
            
            with tab1:
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Total Distance", f"{df['distance_km'].sum():.1f} km")
                with col2: st.metric("Activities", len(df))
                with col3: st.metric("Avg Pace", f"{df['pace_min_km'].mean():.2f} min/km" if len(df) > 0 else "N/A")
                
                fig = px.bar(df, x='start_date', y='distance_km', color='sport_type')
                st.plotly_chart(fig, width='stretch')
            
            with tab2:
                st.subheader("Monthly Trends")
                monthly = df.groupby(pd.to_datetime(df['start_date']).dt.to_period('M'))['distance_km'].sum().reset_index()
                monthly['start_date'] = monthly['start_date'].dt.to_timestamp()
                st.plotly_chart(px.line(monthly, x='start_date', y='distance_km'), width='stretch')
                
                st.subheader("Future Distance Prediction")
                if len(df) > 5:
                    X = np.arange(len(df)).reshape(-1, 1)
                    y = df['distance_km'].values
                    model = LinearRegression().fit(X, y)
                    future = np.arange(len(df), len(df)+12).reshape(-1, 1)
                    pred = model.predict(future)
                    st.line_chart(pd.DataFrame({'Predicted km': pred}))
            
            with tab3:
                st.subheader("Your Routes (Red Path)")
                if not df.empty:
                    activity_id = st.selectbox("Select Activity", df.index)
                    try:
                        stream = client.get_activity_streams(df.iloc[activity_id]['id'], types=['latlng'])
                        if 'latlng' in stream:
                            points = stream['latlng'].data
                            m = folium.Map(location=points[0], zoom_start=13)
                            folium.PolyLine(points, color="red", weight=4, opacity=0.8).add_to(m)
                            st_folium(m, width='stretch')
                    except:
                        st.info("Route data loading...")
            
            with tab4:
                st.subheader("Training Heatmap")
                m = folium.Map(location=[30.3, 78.0], zoom_start=8)
                HeatMap([[30.3, 78.0]], radius=30).add_to(m)  # Expand later
                st_folium(m, width='stretch')
    except Exception as e:
        st.error(f"Data Error: {e}")
else:
    st.info("Login with Strava in the sidebar to begin")

st.caption("EnduraRank MVP - Built for Robin")
