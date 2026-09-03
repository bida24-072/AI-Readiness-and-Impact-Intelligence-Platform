import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdoptionPredictor:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.model = None
        self.label_encoders = {}
        logger.info("AdoptionPredictor initialized")
    
    def prepare_features(self, employee_data, training_data, usage_data):
        logger.info("Preparing features for modeling")
        
        training_agg = training_data.groupby('employee_id').agg({
            'program_id': 'count',
            'score': 'mean',
            'time_spent_hours': 'sum'
        }).rename(columns={
            'program_id': 'trainings_completed',
            'score': 'avg_score',
            'time_spent_hours': 'total_training_hours'
        })
        
        usage_agg = usage_data.groupby('employee_id').agg({
            'tool_name': 'nunique',
            'minutes_used': 'sum',
            'tasks_completed': 'sum'
        }).rename(columns={
            'tool_name': 'unique_tools_used',
            'minutes_used': 'total_usage_minutes',
            'tasks_completed': 'total_tasks_completed'
        })
        
        features = employee_data.merge(training_agg, on='employee_id', how='left')
        features = features.merge(usage_agg, on='employee_id', how='left')
        
        features = features.fillna(0)
        
        features['adopted'] = (features['total_usage_minutes'] > 120).astype(int)
        
        categorical_cols = ['job_function', 'department', 'seniority_level']
        for col in categorical_cols:
            le = LabelEncoder()
            features[col] = le.fit_transform(features[col].astype(str))
            self.label_encoders[col] = le
        
        logger.info(f"Features prepared: {features.shape}")
        return features
    
    def train_model(self, features):
        logger.info("Training adoption prediction model")
        
        feature_cols = ['job_function', 'department', 'seniority_level', 
                       'trainings_completed', 'avg_score', 'total_training_hours',
                       'unique_tools_used', 'total_tasks_completed']
        
        X = features[feature_cols]
        y = features['adopted']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        logger.info("Model evaluation:")
        logger.info(classification_report(y_test, y_pred))
        
        importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        logger.info("Feature importance:")
        logger.info(importance)
        
        return self.model
    
    def save_model(self, model_path):
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, model_path)
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path):
        self.model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
    
    def predict_adoption_risk(self, employee_data):
        if self.model is None:
            raise ValueError("Model not loaded. Please load a trained model first.")
        
        feature_cols = ['job_function', 'department', 'seniority_level', 
                       'trainings_completed', 'avg_score', 'total_training_hours',
                       'unique_tools_used', 'total_tasks_completed']
        
        X = employee_data[feature_cols]
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]
        
        results = employee_data.copy()
        results['adoption_risk'] = predictions
        results['adoption_probability'] = probabilities
        
        results['risk_category'] = pd.cut(
            results['adoption_probability'],
            bins=[0, 0.3, 0.7, 1.0],
            labels=['High Risk', 'Medium Risk', 'Low Risk']
        )
        
        return results

if __name__ == "__main__":
    data_path = Path.cwd() / 'data'
    predictor = AdoptionPredictor(data_path)
    
    employees = pd.read_csv(data_path / 'processed' / 'sample_employees.csv')
    training = pd.read_csv(data_path / 'processed' / 'sample_training.csv')
    usage = pd.read_csv(data_path / 'processed' / 'sample_usage.csv')
    
    features = predictor.prepare_features(employees, training, usage)
    model = predictor.train_model(features)
    
    model_path = Path.cwd() / 'models' / 'adoption_model.pkl'
    predictor.save_model(model_path)
    
    results = predictor.predict_adoption_risk(features)
    results.to_csv(data_path / 'processed' / 'risk_predictions.csv', index=False)
    print("Predictions saved to data/processed/risk_predictions.csv")