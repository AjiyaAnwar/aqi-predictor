"""
Feature Engineering for AQI Prediction
"""
import pandas as pd
import numpy as np
from datetime import datetime

class AQIFeatureEngineer:
    def create_features(self, df):
        """Create features from raw data"""
        features = df.copy()
        
        # Time features
        features['hour'] = features['timestamp'].dt.hour
        features['day_of_week'] = features['timestamp'].dt.dayofweek
        features['month'] = features['timestamp'].dt.month
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Lag features
        features['pm2_5_lag_1h'] = features['pm2_5'].shift(1)
        features['pm2_5_lag_24h'] = features['pm2_5'].shift(24)
        
        # Rolling averages
        features['pm2_5_6h_avg'] = features['pm2_5'].rolling(6).mean()
        features['pm2_5_24h_avg'] = features['pm2_5'].rolling(24).mean()
        
        # Daily aggregates
        features['date'] = features['timestamp'].dt.date
        daily_avg = features.groupby('date')['aqi'].transform('mean')
        features['daily_avg_aqi'] = daily_avg
        
        # Target: next day's average AQI
        features['next_day_avg_aqi'] = features.groupby('date')['aqi'].transform(
            lambda x: x.shift(-24).mean()
        )
        
        return features
    
    def create_daily_data(self, df):
        """Create daily aggregated dataset"""
        daily = df.groupby('date').agg({
            'aqi': ['mean', 'max', 'min', 'std'],
            'pm2_5': 'mean',
            'pm10': 'mean',
            'ozone': 'mean'
        }).round(2)
        
        # Flatten columns
        daily.columns = ['_'.join(col).strip() for col in daily.columns.values]
        daily = daily.reset_index()
        daily = daily.rename(columns={
            'aqi_mean': 'daily_avg_aqi',
            'aqi_max': 'daily_max_aqi',
            'aqi_min': 'daily_min_aqi',
            'aqi_std': 'daily_std_aqi'
        })
        
        # Date features
        daily['date'] = pd.to_datetime(daily['date'])
        daily['day_of_week'] = daily['date'].dt.dayofweek
        daily['day_name'] = daily['date'].dt.day_name()
        
        # Lag features
        daily['prev_day_aqi'] = daily['daily_avg_aqi'].shift(1)
        daily['prev_week_aqi'] = daily['daily_avg_aqi'].shift(7)
        
        # Target: next day's AQI
        daily['next_day_aqi'] = daily['daily_avg_aqi'].shift(-1)
        
        return daily

print("✅ Feature engineering module created!")
