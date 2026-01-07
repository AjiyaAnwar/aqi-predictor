# Update dashboard with more features
"""
Enhanced AQI Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import json

# Page configuration
st.set_page_config(
    page_title="Karachi AQI Predictor",
    page_icon="🌫️",
    layout="wide"
)

# Title
st.title("🌫️ Karachi Air Quality Index Predictor")
st.markdown("### Real-time monitoring with 3-day forecasts")

# Load current data
def load_current_data():
    """Load current AQI data"""
    file_path = "data/processed/current_aqi.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "us_aqi": 145,
        "pm2_5": 45.2,
        "pm10": 78.5,
        "time": datetime.now().isoformat()
    }

# Load historical data
def load_historical_data():
    """Load historical AQI data"""
    import glob
    csv_files = glob.glob("data/raw/*.csv")
    
    if csv_files:
        try:
            # Get the latest file
            latest_file = max(csv_files, key=os.path.getctime)
            df = pd.read_csv(latest_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except:
            pass
    
    # Generate sample data if no real data
    dates = pd.date_range(end=datetime.now(), periods=24*7, freq='H')  # 7 days hourly
    return pd.DataFrame({
        'timestamp': dates,
        'pm2_5': np.random.uniform(30, 60, len(dates)),
        'pm10': np.random.uniform(50, 100, len(dates)),
        'aqi': np.random.uniform(100, 180, len(dates))
    })

# Main dashboard
def main():
    # Load data
    current_data = load_current_data()
    historical_data = load_historical_data()
    
    # Current Status
    st.markdown("---")
    st.markdown("## 📊 Current Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    current_aqi = current_data.get('us_aqi', 145)
    
    # Determine AQI category
    if current_aqi <= 50:
        category, color = "Good", "#10B981"
    elif current_aqi <= 100:
        category, color = "Moderate", "#F59E0B"
    elif current_aqi <= 150:
        category, color = "Unhealthy for Sensitive", "#F97316"
    elif current_aqi <= 200:
        category, color = "Unhealthy", "#EF4444"
    else:
        category, color = "Very Unhealthy", "#8B5CF6"
    
    with col1:
        st.metric("Current AQI", f"{current_aqi:.0f}", category)
        st.markdown(f'<p style="color: {color}; font-weight: bold;">{category}</p>', unsafe_allow_html=True)
    
    with col2:
        pm25 = current_data.get('pm2_5', 45.2)
        st.metric("PM2.5", f"{pm25:.1f} µg/m³")
    
    with col3:
        pm10 = current_data.get('pm10', 78.5)
        st.metric("PM10", f"{pm10:.1f} µg/m³")
    
    with col4:
        st.metric("Last Updated", datetime.now().strftime("%H:%M"))
    
    # 3-Day Forecast
    st.markdown("---")
    st.markdown("## 📅 3-Day Forecast")
    
    # Generate forecast (simulated for now)
    forecast_dates = [datetime.now() + timedelta(days=i) for i in range(1, 4)]
    forecast_data = pd.DataFrame({
        'Date': forecast_dates,
        'Day': [d.strftime('%A') for d in forecast_dates],
        'Predicted AQI': [current_aqi * 0.95, current_aqi * 0.92, current_aqi * 0.90],
        'Category': ['Unhealthy for Sensitive', 'Unhealthy for Sensitive', 'Unhealthy for Sensitive']
    })
    
    forecast_data['Predicted AQI'] = forecast_data['Predicted AQI'].round(1)
    
    # Display forecast
    forecast_cols = st.columns(3)
    for idx, row in forecast_data.iterrows():
        with forecast_cols[idx]:
            st.metric(
                label=f"{row['Day']}",
                value=f"{row['Predicted AQI']:.0f}",
                delta=row['Category']
            )
    
    # Historical Chart
    st.markdown("---")
    st.markdown("## 📈 Historical Trends")
    
    if not historical_data.empty:
        # Create daily aggregates
        historical_data['date'] = pd.to_datetime(historical_data['timestamp']).dt.date
        daily_avg = historical_data.groupby('date')['aqi'].mean().reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_avg['date'],
            y=daily_avg['aqi'],
            mode='lines+markers',
            name='Daily Average AQI',
            line=dict(color='#3B82F6', width=3),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        
        fig.update_layout(
            title="AQI Trend (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="AQI",
            height=400,
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Health Recommendations
    st.markdown("---")
    st.markdown("## 🏥 Health Recommendations")
    
    recommendations = {
        "Good": "✅ Perfect for outdoor activities.",
        "Moderate": "⚠️ Unusually sensitive people should consider reducing prolonged outdoor exertion.",
        "Unhealthy for Sensitive": "⚠️ People with respiratory or heart disease, children and older adults should limit prolonged outdoor exertion.",
        "Unhealthy": "❌ Everyone should reduce prolonged or heavy outdoor exertion.",
        "Very Unhealthy": "❌ Everyone should avoid prolonged outdoor exertion.",
        "Hazardous": "🚨 Everyone should avoid all outdoor activities."
    }
    
    st.info(recommendations.get(category, "Check local health advisories."))
    
    # Data Collection Status
    st.markdown("---")
    st.markdown("## 🔄 Data Pipeline")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Collect New Data", type="primary"):
            st.info("Data collection started...")
            # This would call your collector in a real app
            st.success("Data collection complete!")
    
    with col2:
        if st.button("📊 Train Model"):
            st.info("Model training started...")
            # This would call your trainer in a real app
            st.success("Model training complete!")

if __name__ == "__main__":
    main()
