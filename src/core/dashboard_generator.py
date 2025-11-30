"""
Dashboard Generator module for creating dynamic HTML dashboards.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DashboardGenerator:
    """Generates dynamic HTML dashboards with charts and widgets."""
    
    def __init__(self):
        """Initialize the dashboard generator."""
        self.charts = []
        self.widgets = []
        self.dashboards = {}
        self.dashboard_counter = 1
    
    def create_dashboard(self, title: str, data: Dict[str, Any]) -> str:
        """
        Create a dynamic dashboard with the given title and data.
        
        Args:
            title: Dashboard title
            data: Dictionary containing dashboard data
            
        Returns:
            HTML string of the dashboard
        """
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chart-container {{
            width: 100%;
            height: 400px;
            margin: 20px 0;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .metric-label {{
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>{title}</h1>
        <div class="metrics-grid">
"""
            
            # Add metric cards
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    display_value = f"{value:,.2f}" if isinstance(value, float) else str(value)
                else:
                    display_value = str(value)
                    
                html_content += f"""
            <div class="metric-card">
                <div class="metric-label">{key.replace('_', ' ').title()}</div>
                <div class="metric-value">{display_value}</div>
            </div>
"""
            
            html_content += """
        </div>
    </div>
    
    <script>
        // Initialize charts when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            const charts = [];
"""
            
            # Add chart configurations
            chart_index = 0
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    html_content += f"""
            charts.push({{
                type: 'line',
                data: {value},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: true
                        }}
                    }}
                }}
            }});
            
            const chartContainers = document.querySelectorAll('.chart-container');
            chartContainers.forEach((container, index) => {{
                if (charts[index]) {{
                    new Chart(container, charts[index]);
                }}
            }});
        }});
    </script>
</body>
</html>
"""
            
            logger.info(f"Generated dashboard: {title}")
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            return f"<html><body><h1>Error generating dashboard: {e}</h1></body></html>"
    
    def create_widget(self, widget_type: str, config: Dict[str, Any]) -> str:
        """
        Create a specific widget type.
        
        Args:
            widget_type: Type of widget
            config: Widget configuration
            
        Returns:
            HTML string for a widget
        """
        try:
            if widget_type == "chart":
                return self._create_chart_widget(config)
            elif widget_type == "metric":
                return self._create_metric_widget(config)
            elif widget_type == "table":
                return self._create_table_widget(config)
            else:
                return f"<div>Unknown widget type: {widget_type}</div>"
                
        except Exception as e:
            logger.error(f"Error creating widget {widget_type}: {e}")
            return f"<div>Error creating widget: {e}</div>"
    
    def _extract_excel_data(self, file, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract data from Excel file for dashboard generation.
        
        Args:
            file: File object or path
            sheet_name: Name of sheet to process (optional)
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            import pandas as pd
            import io
            
            # Handle both file path and file object
            if hasattr(file, 'read'):
                # File object from Flask upload
                file_bytes = file.read()
                if sheet_name:
                    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)
                else:
                    df = pd.read_excel(io.BytesIO(file_bytes))
                sheet_names = pd.ExcelFile(io.BytesIO(file_bytes)).sheet_names
            else:
                # File path
                if sheet_name:
                    df = pd.read_excel(file, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(file)
                sheet_names = pd.ExcelFile(file).sheet_names
            
            # Convert DataFrame to dictionary
            data = {
                'columns': df.columns.tolist(),
                'data': df.to_dict('records'),
                'shape': df.shape,
                'sheet_names': sheet_names if not sheet_name else [sheet_name]
            }
            
            file_identifier = getattr(file, 'filename', str(file))
            logger.info(f"Successfully extracted Excel data: {file_identifier}")
            return data
            
        except Exception as e:
            file_identifier = getattr(file, 'filename', str(file))
            logger.error(f"Error extracting Excel data {file_identifier}: {e}")
            return {'error': str(e)}
    
    def process_excel_file(self, file, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process Excel file and return data for dashboard generation.
        
        Args:
            file: File object or path
            sheet_name: Name of sheet to process (optional)
            
        Returns:
            Dictionary containing processed data and dashboard ID
        """
        try:
            # Extract data from Excel
            data = self._extract_excel_data(file, sheet_name)
            
            if 'error' in data:
                return {
                    'success': False,
                    'error': data['error']
                }
            
            # Generate dashboard ID
            dashboard_id = f"dashboard_{self.dashboard_counter}"
            self.dashboard_counter += 1
            
            # Store dashboard data
            self.dashboards[dashboard_id] = {
                'id': dashboard_id,
                'data': data,
                'created_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'dashboard_id': dashboard_id,
                'data': data
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get dashboard data by ID.
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            Dashboard data or None if not found
        """
        return self.dashboards.get(dashboard_id)
    
    def _create_chart_widget(self, config: Dict[str, Any]) -> str:
        """Create a chart widget."""
        chart_type = config.get("type", "line")
        data = config.get("data", [])
        return f"""
        <div class="chart-container">
            <canvas id="chart_{len(self.charts)}"></canvas>
        </div>
        <script>
            new Chart(document.getElementById('chart_{len(self.charts)}'), {{
                type: '{chart_type}',
                data: {json.dumps(data)},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: true
                        }}
                    }}
                }}
            }});
        </script>
        """
    
    def _create_metric_widget(self, config: Dict[str, Any]) -> str:
        """Create a metric display widget."""
        label = config.get("label", "Metric")
        value = config.get("value", 0)
        return f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """
    
    def _create_table_widget(self, config: Dict[str, Any]) -> str:
        """Create a table widget."""
        headers = config.get("headers", [])
        rows = config.get("rows", [])
        html_content = ""
        
        # Create table with headers
        html_content += f"""
        <div class="table-container">
            <table border="1" style="width: 100%; border-collapse: collapse;">
                <tr>
        """
        for header in headers:
            html_content += f"                    <th>{header}</th>"
        
        html_content += """
                </tr>
        """
        
        # Create table rows
        for row in rows:
            html_content += f"""
                <tr>
        """
            for cell in row:
                html_content += f'<td class="table-cell">{cell}</td>'
        
            html_content += """
                </tr>
        """
        
        html_content += """
            </table>
        </div>
        """
        
        return html_content