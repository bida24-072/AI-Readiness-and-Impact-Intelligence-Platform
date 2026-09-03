import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardBuilder:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        logger.info("DashboardBuilder initialized")
    
    def create_dashboard(self, risk_data, training_data, usage_data):
        logger.info("Creating dashboard visualizations")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('AI Readiness and Impact Intelligence Dashboard', fontsize=20)
        
        risk_counts = risk_data['risk_category'].value_counts()
        axes[0, 0].pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Employee Adoption Risk Distribution')
        
        training_impact = training_data.groupby('program_id')['score'].mean()
        axes[0, 1].hist(training_impact, bins=20, edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('Training Score Distribution')
        axes[0, 1].set_xlabel('Average Score')
        axes[0, 1].set_ylabel('Number of Programs')
        
        tool_usage = usage_data.groupby('tool_name')['minutes_used'].sum().sort_values()
        axes[1, 0].barh(tool_usage.index, tool_usage.values)
        axes[1, 0].set_title('Total AI Tool Usage by Tool')
        axes[1, 0].set_xlabel('Total Minutes Used')
        
        merged = training_data.merge(usage_data, on='employee_id', how='inner')
        efficiency_by_hours = merged.groupby('employee_id').agg({
            'time_spent_hours': 'sum',
            'minutes_used': 'sum'
        })
        axes[1, 1].scatter(efficiency_by_hours['time_spent_hours'], 
                          efficiency_by_hours['minutes_used'],
                          alpha=0.6)
        axes[1, 1].set_title('Training Hours vs Tool Usage')
        axes[1, 1].set_xlabel('Total Training Hours')
        axes[1, 1].set_ylabel('Total Usage Minutes')
        
        plt.tight_layout()
        
        dashboard_path = self.data_path / 'processed' / 'dashboard.png'
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        logger.info(f"Dashboard saved to {dashboard_path}")
        return fig
    
    def create_impact_report(self, risk_data):
        logger.info("Creating impact summary report")
        
        report = {
            'Total Employees': len(risk_data),
            'High Risk Employees': len(risk_data[risk_data['risk_category'] == 'High Risk']),
            'Medium Risk Employees': len(risk_data[risk_data['risk_category'] == 'Medium Risk']),
            'Low Risk Employees': len(risk_data[risk_data['risk_category'] == 'Low Risk']),
            'Average Adoption Probability': risk_data['adoption_probability'].mean(),
            'Median Adoption Probability': risk_data['adoption_probability'].median()
        }
        
        report_df = pd.DataFrame(report.items(), columns=['Metric', 'Value'])
        report_path = self.data_path / 'processed' / 'impact_report.csv'
        report_df.to_csv(report_path, index=False)
        
        logger.info(f"Impact report saved to {report_path}")
        return report_df

if __name__ == "__main__":
    data_path = Path.cwd() / 'data'
    builder = DashboardBuilder(data_path)
    
    risk_data = pd.read_csv(data_path / 'processed' / 'risk_predictions.csv')
    training_data = pd.read_csv(data_path / 'processed' / 'sample_training.csv')
    usage_data = pd.read_csv(data_path / 'processed' / 'sample_usage.csv')
    
    fig = builder.create_dashboard(risk_data, training_data, usage_data)
    report = builder.create_impact_report(risk_data)
    
    print("Dashboard created and saved to data/processed/dashboard.png")
    print("Impact report saved to data/processed/impact_report.csv")
    print("\nImpact Report Summary:")
    print(report)