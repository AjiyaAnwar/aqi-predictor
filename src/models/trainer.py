"""
Simple Model Training for AQI Prediction
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

class SimpleAQIModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.feature_importance = None
    
    def train(self, X, y):
        """Train the model"""
        print(f"🤖 Training model with {len(X)} samples...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Predictions
        y_pred = self.model.predict(X_test)
        
        # Evaluate
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print("📊 Model Performance:")
        print(f"   MAE: {mae:.2f}")
        print(f"   RMSE: {rmse:.2f}")
        print(f"   R² Score: {r2:.3f}")
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\n📈 Top 5 Important Features:")
            for idx, row in self.feature_importance.head().iterrows():
                print(f"   {row['feature']}: {row['importance']:.3f}")
        
        return mae, rmse, r2
    
    def predict(self, X):
        """Make predictions"""
        return self.model.predict(X)
    
    def save(self, filename="models/aqi_model.joblib"):
        """Save the model"""
        os.makedirs("models", exist_ok=True)
        joblib.dump({
            'model': self.model,
            'feature_importance': self.feature_importance
        }, filename)
        print(f"💾 Model saved to: {filename}")
    
    def load(self, filename="models/aqi_model.joblib"):
        """Load a saved model"""
        if os.path.exists(filename):
            data = joblib.load(filename)
            self.model = data['model']
            self.feature_importance = data['feature_importance']
            print(f"✅ Model loaded from: {filename}")
            return True
        else:
            print(f"❌ Model file not found: {filename}")
            return False

def create_sample_data():
    """Create sample data for testing"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    data = pd.DataFrame({
        'date': dates,
        'daily_avg_aqi': np.random.uniform(50, 200, 100),
        'pm2_5_mean': np.random.uniform(20, 100, 100),
        'pm10_mean': np.random.uniform(30, 150, 100),
        'day_of_week': [d.dayofweek for d in dates],
        'prev_day_aqi': np.random.uniform(50, 200, 100),
        'next_day_aqi': np.random.uniform(50, 200, 100)
    })
    
    return data

if __name__ == "__main__":
    print("🧪 Testing model training...")
    
    # Create sample data
    data = create_sample_data()
    
    # Prepare features and target
    X = data[['daily_avg_aqi', 'pm2_5_mean', 'pm10_mean', 'day_of_week', 'prev_day_aqi']]
    y = data['next_day_aqi']
    
    # Train model
    model = SimpleAQIModel()
    model.train(X, y)
    
    # Save model
    model.save()
    
    print("✅ Model training test complete!")
