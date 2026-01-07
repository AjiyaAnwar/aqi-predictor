"""
Complete AQI Data Collector for Karachi
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

class KarachiAQICollector:
    def __init__(self):
        self.lat = 24.8607
        self.lon = 67.0011
        self.city = "Karachi"
        self.base_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    def get_current_aqi(self):
        """Get current AQI data"""
        print("📡 Fetching current AQI...")
        
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "current": ["pm2_5", "pm10", "us_aqi", "european_aqi"],
            "timezone": "Asia/Karachi"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                
                if current:
                    print("✅ Current AQI Data:")
                    print(f"   US AQI: {current.get('us_aqi', 'N/A')}")
                    print(f"   PM2.5: {current.get('pm2_5', 'N/A')} µg/m³")
                    print(f"   PM10: {current.get('pm10', 'N/A')} µg/m³")
                    return current
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return {}
    
    def get_historical_data(self, days=7):
        """Get historical AQI data"""
        print(f"📊 Fetching {days} days of historical data...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "hourly": ["pm2_5", "pm10", "ozone"],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "timezone": "Asia/Karachi"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Create DataFrame
                df = pd.DataFrame(data["hourly"])
                if "time" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["time"])
                    df = df.drop(columns=["time"])
                
                # Add location
                df["city"] = self.city
                df["latitude"] = self.lat
                df["longitude"] = self.lon
                
                # Calculate AQI
                df["aqi"] = self.calculate_aqi(df["pm2_5"])
                df["aqi_category"] = df["aqi"].apply(self.get_aqi_category)
                
                # Save data
                os.makedirs("data/raw", exist_ok=True)
                filename = f"data/raw/karachi_aqi_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                df.to_csv(filename, index=False)
                
                print(f"✅ Collected {len(df)} records")
                print(f"💾 Saved to: {filename}")
                
                return df
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return pd.DataFrame()
    
    def calculate_aqi(self, pm25):
        """Calculate AQI from PM2.5"""
        aqi = np.zeros(len(pm25))
        
        for i, value in enumerate(pm25):
            if pd.isna(value):
                aqi[i] = np.nan
            elif value <= 12.0:
                aqi[i] = value * (50/12.0)
            elif value <= 35.4:
                aqi[i] = 50 + (value - 12.1) * (50/23.3)
            elif value <= 55.4:
                aqi[i] = 100 + (value - 35.5) * (50/19.9)
            elif value <= 150.4:
                aqi[i] = 150 + (value - 55.5) * (50/94.9)
            elif value <= 250.4:
                aqi[i] = 200 + (value - 150.5) * (100/99.9)
            else:
                aqi[i] = 300 + (value - 250.5) * (200/249.9)
        
        return aqi
    
    def get_aqi_category(self, aqi):
        """Get AQI category"""
        if pd.isna(aqi):
            return "Unknown"
        elif aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"

def main():
    """Main function"""
    print("=" * 50)
    print("       KARACHI AQI DATA COLLECTOR")
    print("=" * 50)
    
    collector = KarachiAQICollector()
    
    # Get current data
    current = collector.get_current_aqi()
    
    # Get historical data
    historical = collector.get_historical_data(days=3)
    
    if not historical.empty:
        print("\n📈 Historical Data Summary:")
        print(f"   Records: {len(historical)}")
        print(f"   Date Range: {historical['timestamp'].min()} to {historical['timestamp'].max()}")
        print(f"   Avg AQI: {historical['aqi'].mean():.1f}")
        print(f"   Max AQI: {historical['aqi'].max():.1f}")
        
        # Save current data
        if current:
            os.makedirs("data/processed", exist_ok=True)
            with open("data/processed/current_aqi.json", "w") as f:
                json.dump(current, f, indent=2)
            print(f"\n💾 Current data saved to: data/processed/current_aqi.json")
    
    print("\n" + "=" * 50)
    print("✅ Collection Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
