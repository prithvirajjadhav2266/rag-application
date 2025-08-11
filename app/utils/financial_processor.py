import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import re
from typing import Dict, List, Any, Optional

class FinancialDataProcessor:
    """Process and visualize financial data from RHP documents."""
    
    def __init__(self, plots_dir: str):
        self.plots_dir = plots_dir
        os.makedirs(plots_dir, exist_ok=True)
    
    def extract_financial_tables(self, text: str) -> Dict[str, List[Dict]]:
        """Extract financial data from text and parse into structured format."""
        financial_data = {
            'income_statement': [],
            'balance_sheet': [],
            'cash_flow': [],
            'ratios': []
        }
        
        # Patterns to identify financial statements
        patterns = {
            'revenue': r'(?:revenue|sales|income from operations|total income).*?(\d+(?:,\d+)*(?:\.\d+)?)',
            'profit': r'(?:net profit|profit after tax|net income).*?(\d+(?:,\d+)*(?:\.\d+)?)',
            'assets': r'(?:total assets|current assets).*?(\d+(?:,\d+)*(?:\.\d+)?)',
            'liabilities': r'(?:total liabilities|current liabilities).*?(\d+(?:,\d+)*(?:\.\d+)?)',
            'equity': r'(?:shareholders?\s+equity|total equity).*?(\d+(?:,\d+)*(?:\.\d+)?)'
        }
        
        # Extract numerical data
        for category, pattern in patterns.items():
            matches = re.finditer(pattern, text.lower(), re.IGNORECASE)
            for match in matches:
                value = self._parse_financial_value(match.group(1))
                if value:
                    financial_data['income_statement'].append({
                        'metric': category,
                        'value': value,
                        'year': self._extract_year(match.group(0))
                    })
        
        return financial_data
    
    def _parse_financial_value(self, value_str: str) -> Optional[float]:
        """Parse financial value from string format."""
        try:
            # Remove commas and convert to float
            clean_value = value_str.replace(',', '')
            return float(clean_value)
        except (ValueError, AttributeError):
            return None
    
    def _extract_year(self, text: str) -> Optional[str]:
        """Extract year from financial statement text."""
        year_pattern = r'20\d{2}'
        match = re.search(year_pattern, text)
        return match.group() if match else None
    
    def create_revenue_trend_plot(self, financial_data: Dict) -> str:
        """Create revenue trend visualization."""
        revenue_data = [item for item in financial_data.get('income_statement', []) 
                       if item['metric'] == 'revenue']
        
        if not revenue_data:
            return None
        
        # Sort by year
        revenue_data.sort(key=lambda x: x.get('year', '0'))
        
        years = [item.get('year', 'N/A') for item in revenue_data]
        values = [item['value'] for item in revenue_data]
        
        # Create Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Revenue Trend Over Years',
            xaxis_title='Year',
            yaxis_title='Revenue (in Crores)',
            template='plotly_white',
            height=400
        )
        
        # Save plot
        plot_filename = f'revenue_trend_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        plot_path = os.path.join(self.plots_dir, plot_filename)
        fig.write_html(plot_path)
        
        return plot_filename
    
    def create_financial_dashboard(self, financial_data: Dict) -> str:
        """Create comprehensive financial dashboard."""
        # Extract data for dashboard
        metrics = {}
        for statement in financial_data.get('income_statement', []):
            metric = statement['metric']
            year = statement.get('year', 'Latest')
            if metric not in metrics:
                metrics[metric] = {}
            metrics[metric][year] = statement['value']
        
        if not metrics:
            return None
        
        # Create subplots
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue Trend', 'Profit Trend', 'Asset Distribution', 'Key Ratios'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Revenue trend
        if 'revenue' in metrics:
            years = list(metrics['revenue'].keys())
            values = list(metrics['revenue'].values())
            fig.add_trace(
                go.Scatter(x=years, y=values, name='Revenue', line=dict(color='#2E86AB')),
                row=1, col=1
            )
        
        # Profit trend
        if 'profit' in metrics:
            years = list(metrics['profit'].keys())
            values = list(metrics['profit'].values())
            fig.add_trace(
                go.Scatter(x=years, y=values, name='Profit', line=dict(color='#A23B72')),
                row=1, col=2
            )
        
        # Asset distribution
        asset_types = ['assets', 'liabilities', 'equity']
        asset_values = []
        asset_labels = []
        for asset_type in asset_types:
            if asset_type in metrics:
                latest_year = max(metrics[asset_type].keys())
                asset_values.append(metrics[asset_type][latest_year])
                asset_labels.append(asset_type.title())
        
        if asset_values:
            fig.add_trace(
                go.Pie(labels=asset_labels, values=asset_values, name="Assets"),
                row=2, col=1
            )
        
        fig.update_layout(
            title_text="Financial Dashboard",
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        # Save dashboard
        dashboard_filename = f'financial_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        dashboard_path = os.path.join(self.plots_dir, dashboard_filename)
        fig.write_html(dashboard_path)
        
        return dashboard_filename
    
    def generate_financial_summary(self, financial_data: Dict) -> Dict[str, Any]:
        """Generate financial summary statistics."""
        summary = {
            'total_metrics': 0,
            'years_covered': set(),
            'key_metrics': {},
            'growth_rates': {}
        }
        
        for statement in financial_data.get('income_statement', []):
            summary['total_metrics'] += 1
            if statement.get('year'):
                summary['years_covered'].add(statement['year'])
            
            metric = statement['metric']
            if metric not in summary['key_metrics']:
                summary['key_metrics'][metric] = []
            summary['key_metrics'][metric].append({
                'year': statement.get('year'),
                'value': statement['value']
            })
        
        # Calculate growth rates
        for metric, values in summary['key_metrics'].items():
            if len(values) >= 2:
                sorted_values = sorted(values, key=lambda x: x.get('year', '0'))
                if len(sorted_values) >= 2:
                    old_value = sorted_values[0]['value']
                    new_value = sorted_values[-1]['value']
                    if old_value > 0:
                        growth_rate = ((new_value - old_value) / old_value) * 100
                        summary['growth_rates'][metric] = round(growth_rate, 2)
        
        summary['years_covered'] = sorted(list(summary['years_covered']))
        
        return summary