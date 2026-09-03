import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        logger.info(f"DataLoader initialized with path: {self.data_path}")
    
    def load_employee_data(self):
        try:
            file_path = self.data_path / 'raw' / 'employees.csv'
            df = pd.read_csv(file_path)
            logger.info(f"Loaded employee data: {len(df)} records")
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return self.generate_sample_employee_data()
    
    def load_training_data(self):
        try:
            file_path = self.data_path / 'raw' / 'training_completions.csv'
            df = pd.read_csv(file_path)
            logger.info(f"Loaded training data: {len(df)} records")
            return df
        except FileNotFoundError:
            logger.error("Training data file not found")
            return self.generate_sample_training_data()
    
    def load_usage_data(self):
        try:
            file_path = self.data_path / 'raw' / 'ai_tool_usage.csv'
            df = pd.read_csv(file_path)
            logger.info(f"Loaded usage data: {len(df)} records")
            return df
        except FileNotFoundError:
            logger.error("Usage data file not found")
            return self.generate_sample_usage_data()
    
    def generate_sample_employee_data(self):
        np.random.seed(42)
        n = 1000
        data = {
            'employee_id': range(1, n+1),
            'job_function': np.random.choice(['Analyst', 'Consultant', 'Manager', 'Director', 'Partner'], n),
            'department': np.random.choice(['Tax', 'Audit', 'Advisory', 'Consulting'], n),
            'seniority_level': np.random.choice(['Junior', 'Senior', 'Lead', 'Executive'], n),
            'hire_date': pd.date_range('2015-01-01', periods=n, freq='D')
        }
        df = pd.DataFrame(data)
        
        df.to_csv(self.data_path / 'processed' / 'sample_employees.csv', index=False)
        logger.info(f"Generated {n} sample employee records")
        return df
    
    def generate_sample_training_data(self):
        np.random.seed(123)
        n = 5000
        data = {
            'completion_id': range(1, n+1),
            'employee_id': np.random.randint(1, 1001, n),
            'program_id': np.random.randint(1, 51, n),
            'completion_date': pd.date_range('2024-01-01', periods=n, freq='H'),
            'score': np.random.uniform(60, 100, n),
            'time_spent_hours': np.random.uniform(2, 20, n)
        }
        df = pd.DataFrame(data)
        df.to_csv(self.data_path / 'processed' / 'sample_training.csv', index=False)
        logger.info(f"Generated {n} sample training records")
        return df
    
    def generate_sample_usage_data(self):
        np.random.seed(456)
        n = 3000
        data = {
            'usage_id': range(1, n+1),
            'employee_id': np.random.randint(1, 1001, n),
            'tool_name': np.random.choice(['ChatGPT', 'Copilot', 'GitHub Copilot', 'AWS CodeWhisperer', 'Tableau AI'], n),
            'usage_date': pd.date_range('2024-01-01', periods=n, freq='H'),
            'minutes_used': np.random.randint(10, 240, n),
            'tasks_completed': np.random.randint(1, 20, n)
        }
        df = pd.DataFrame(data)
        df.to_csv(self.data_path / 'processed' / 'sample_usage.csv', index=False)
        logger.info(f"Generated {n} sample usage records")
        return df

if __name__ == "__main__":
    loader = DataLoader(Path.cwd() / 'data')
    employees = loader.load_employee_data()
    training = loader.load_training_data()
    usage = loader.load_usage_data()
    print("Data loading complete. Sample data generated in data/processed/")