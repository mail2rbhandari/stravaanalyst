import streamlit as st
import os
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from stravalib.client import Client
import numpy as np
from sklearn.linear_model import LinearRegression

os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

st.set_page_config(page_title="EnduraAnalyst", layout="wide")
st.title("🏃‍♂️ EnduraAnalyst: Live Strava Personal Analyst")
st.markdown("### Your Personal Endurance Sports Coach")

# ... (keep the sidebar login code from previous version) ...

# Main Dashboard
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
            df = df.dropna(subset=['start_date'])
            df['pace_min_km'] = df['moving_time_min'] / df['distance_km'].replace(0, float('nan'))
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends & Predictions", "🗺️ Maps", "🔥 Heatmap"])
            
            with tab1:
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Total Distance", f"{df['distance_km'].sum():.1f} km")
                with col2: st.metric("Activities", len(df))
                with col3: st.metric("Avg Pace", f"{df['pace_min_km'].mean():.2f} min/km")
                fig = px.bar(df, x='start_date', y='distance_km', color='sport_type')
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.subheader("Monthly Trends")
                monthly = df.groupby(df['start_date'].astype('datetime64[ns]').dt.to_period('M'))['distance_km'].sum().reset_index()
                monthly['start_date'] = monthly['start_date'].dt.to_timestamp()
                st.plotly_chart(px.line(monthly, x='start_date', y='distance_km'))
                
                st.subheader("Simple Future Prediction")
                if len(df) > 5:
                    X = np.arange(len(df)).reshape(-1, 1)
                    y = df['distance_km'].values
                    model = LinearRegression().fit(X, y)
                    future_x = np.arange(len(df), len(df)+12).reshape(-1, 1)
                    pred = model.predict(future_x)
                    st.line_chart(pd.DataFrame({'Predicted Distance (km)': pred}))
            
            with tab3:
                st.subheader("Activity Map")
                m = folium.Map(location=[30.3, 78.0], zoom_start=8)  # Dehradun area
                st_folium(m, width=700)
                st.info("Full route maps coming soon (using activity streams)")
            
            with tab4:
                st.subheader("Training Heatmap")
                st.info("Heatmap of activity frequency by day/month (full version)")
                # Placeholder
                heatmap_data = df.groupby('start_date')['distance_km'].sum()
                st.bar_chart(heatmap_data)
                
    except Exception as e:
        st.error(f"Data Error: {e}")
else:
    st.info("Use sidebar to login with Strava")

st.caption("Built for Robin - EnduraRank MVP")
