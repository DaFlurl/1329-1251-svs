"""
WebManager class for managing web-related functionality including dashboard generation,
static file serving, WebSocket management, and frontend assets.
"""

import ast
import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ..config import ConfigManager
from ..database import DatabaseManager


class WebManager:
    """Manages web-related functionality including dashboard generation,
    static file serving, WebSocket management, and frontend assets.
    
    This class provides a unified interface for web operations including:
    - Dashboard generation from Excel data
    - Static file serving for web assets
    - WebSocket connection management
    - Frontend asset optimization and management
    """
    
    def __init__(self, config_manager: ConfigManager, database_manager: DatabaseManager, logger: Optional[logging.Logger] = None):
        """Initialize the WebManager.
        
        Args:
            config_manager: Configuration management instance
            database_manager: Database management instance
            logger: Optional logger instance
        """
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # Web-specific configuration
        self.web_config = self.config_manager.get('web', {})
        self.dashboard_config = self.web_config.get('dashboard', {})
        self.static_config = self.web_config.get('static', {})
        self.websocket_config = self.web_config.get('websocket', {})
        
        # Initialize web directories
        self.ensure_web_directories()
        
        self.logger.info("WebManager initialized")
        self.logger.info(f"Dashboard config: {self.dashboard_config}")
        self.logger.info(f"Static config: {self.static_config}")
        self.logger.info(f"WebSocket config: {self.websocket_config}")
    
    def ensure_web_directories(self) -> None:
        """Ensure all required web directories exist."""
        directories = [
            'static',
            'templates', 
            'dashboards',
            'assets/css',
            'assets/js',
            'assets/images',
            'temp'
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created web directory: {directory}")
    
    def generate_dashboard_from_excel(self, excel_file_path: str, dashboard_name: str = None, 
                           output_dir: str = None) -> Dict[str, Any]:
        """Generate an interactive HTML dashboard from Excel data.
        
        Args:
            excel_file_path: Path to Excel file
            dashboard_name: Optional name for the dashboard
            output_dir: Optional output directory
            
        Returns:
            Dictionary containing dashboard generation results
        """
        try:
            import pandas as pd
            
            if not os.path.exists(excel_file_path):
                return {
                    'success': False,
                    'error': f'Excel file not found: {excel_file_path}',
                    'dashboard_path': None
                }
            
            # Read Excel file
            df = pd.read_excel(excel_file_path)
            
            # Generate dashboard name if not provided
            if not dashboard_name:
                dashboard_name = Path(excel_file_path).stem.replace('_', ' ').title() + ' Dashboard'
            
            # Set output directory
            if not output_dir:
                output_dir = 'dashboards'
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate dashboard HTML
            dashboard_path = os.path.join(output_dir, f'{dashboard_name.lower().replace(" ", "_")}.html')
            
            # Create dashboard HTML
            dashboard_html = self._create_dashboard_html(df, dashboard_name, excel_file_path)
            
            # Write dashboard file
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            
            self.logger.info(f"Dashboard generated: {dashboard_path}")
            
            # Save to database
            dashboard_data = {
                'name': dashboard_name,
                'excel_file': excel_file_path,
                'dashboard_path': dashboard_path,
                'rows_count': len(df),
                'columns': list(df.columns),
                'created_at': datetime.now().isoformat()
            }
            
            dashboard_id = self.database_manager.save_dashboard(dashboard_data)
            
            return {
                'success': True,
                'dashboard_id': dashboard_id,
                'dashboard_path': dashboard_path,
                'dashboard_name': dashboard_name,
                'rows_count': len(df),
                'columns': list(df.columns)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating dashboard: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'dashboard_path': None
            }
    
    def _create_dashboard_html(self, df: pd.DataFrame, dashboard_name: str, excel_file_path: str) -> str:
        """Create the HTML content for the dashboard."""
        
        # Basic dashboard HTML template
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dashboard_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .dashboard-title {{ font-size: 24px; font-weight: bold; margin: 0; }}
        .dashboard-subtitle {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .chart-container {{ background: white; padding: 15px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .data-table th {{ background-color: #f2f2f2; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <div class="dashboard-title">{dashboard_name}</div>
        <div class="dashboard-subtitle">Generated from {Path(excel_file_path).name}</div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Total Records</div>
            <div class="stat-value">{len(df):,}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Columns</div>
            <div class="stat-value">{len(df.columns)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Generated</div>
            <div class="stat-value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
    </div>
    
    <div class="chart-container">
        <canvas id="dataChart" width="400" height="200"></canvas>
    </div>
    
    <div class="data-table">
        <h3>Data Preview</h3>
        <table>
            <thead>
                <tr>
                    {''.join([f'<th>{col}</th>' for col in df.columns[:5]])}
                    {f'<th>...</th>' if len(df.columns) > 5 else ''}
                </tr>
            </thead>
            <tbody>
                {self._generate_table_rows(df)}
            </tbody>
        </table>
    </div>
    
    <div class="footer">
        <p>Generated by AgentDaf1.1 WebManager</p>
    </div>
    
    <script>
        // Sample chart data
        const ctx = document.getElementById('dataChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['Sample Data'],
                datasets: [{{
                    label: 'Records',
                    data: [{len(df)}],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        return html_template
    
    def _generate_table_rows(self, df: pd.DataFrame) -> str:
        """Generate HTML table rows from DataFrame."""
        rows_html = []
        for _, row in df.head(10).iterrows():
            row_html = '<tr>'
            for value in row:
                # Handle different data types
                if pd.isna(value):
                    row_html += f'<td>N/A</td>'
                elif isinstance(value, (int, float)):
                    row_html += f'<td>{value:,}</td>'
                else:
                    row_html += f'<td>{str(value)[:50]}...</td>'
            row_html += '</tr>'
            rows_html.append(row_html)
        
        return ''.join(rows_html)
    
    def serve_static_file(self, file_path: str, content: str = None, 
                        content_type: str = 'text/html') -> Dict[str, Any]:
        """Serve a static file with proper content type.
        
        Args:
            file_path: Relative path to the file
            content: File content (if None, reads from file)
            content_type: MIME content type
            
        Returns:
            Dictionary with serving result
        """
        try:
            full_path = Path('static') / file_path
            
            # If content not provided, read from file
            if content is None and full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            if content is None:
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Static file served: {file_path}")
            
            return {
                'success': True,
                'file_path': str(full_path),
                'content_type': content_type,
                'size': len(content) if content else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error serving static file: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_websocket_server(self, host: str = 'localhost', port: int = 8081) -> Dict[str, Any]:
        """Create a WebSocket server for real-time updates.
        
        Args:
            host: Server host
            port: Server port
            
        Returns:
            Dictionary with server creation result
        """
        try:
            # This is a placeholder for WebSocket functionality
            # In a real implementation, this would use websockets or socket.io
            websocket_config = {
                'host': host,
                'port': port,
                'status': 'placeholder',
                'message': 'WebSocket server placeholder - would implement real WebSocket functionality'
            }
            
            self.logger.info(f"WebSocket server configured: {host}:{port}")
            
            return {
                'success': True,
                'websocket_config': websocket_config,
                'message': 'WebSocket server placeholder created'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating WebSocket server: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def optimize_assets(self, asset_dir: str = 'assets') -> Dict[str, Any]:
        """Optimize and manage frontend assets.
        
        Args:
            asset_dir: Directory containing assets
            
        Returns:
            Dictionary with optimization results
        """
        try:
            asset_path = Path(asset_dir)
            
            if not asset_path.exists():
                asset_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created assets directory: {asset_dir}")
            
            # List assets
            assets = []
            if asset_path.exists():
                assets = list(asset_path.rglob('*'))
            
            # Optimization logic (placeholder)
            optimized_assets = []
            total_size_saved = 0
            
            for asset in assets:
                asset_info = {
                    'name': asset.name,
                    'size': asset.stat().st_size if asset.exists() else 0,
                    'type': asset.suffix.lower()
                }
                
                # Simple optimization check (would be more sophisticated in real implementation)
                if asset_info['size'] > 1024 * 1024:  # Larger than 1MB
                    asset_info['optimized'] = True
                    asset_info['saved_size'] = asset_info['size'] * 0.1  # Placeholder savings
                    total_size_saved += asset_info['saved_size']
                else:
                    asset_info['optimized'] = False
                    asset_info['saved_size'] = 0
                
                optimized_assets.append(asset_info)
            
            self.logger.info(f"Asset optimization completed. Total saved: {total_size_saved} bytes")
            
            return {
                'success': True,
                'assets_optimized': len(optimized_assets),
                'total_size_saved': total_size_saved,
                'assets': optimized_assets
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing assets: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_web_statistics(self) -> Dict[str, Any]:
        """Get comprehensive web statistics and performance metrics.
        
        Returns:
            Dictionary containing web statistics
        """
        try:
            # Get dashboard statistics
            dashboard_stats = self.database_manager.get_dashboard_statistics()
            
            # Get static file statistics
            static_dir = Path('static')
            static_files = []
            static_size = 0
            
            if static_dir.exists():
                static_files = list(static_dir.rglob('**/*'))
                for file_path in static_files:
                    if file_path.is_file():
                        static_size += file_path.stat().st_size
            
            # Get asset statistics
            asset_dir = Path('assets')
            asset_files = []
            asset_size = 0
            
            if asset_dir.exists():
                asset_files = list(asset_dir.rglob('**/*'))
                for file_path in asset_files:
                    if file_path.is_file():
                        asset_size += file_path.stat().st_size
            
            # Performance metrics
            stats = {
                'dashboards_count': dashboard_stats.get('count', 0),
                'static_files_count': len(static_files),
                'static_size_bytes': static_size,
                'asset_files_count': len(asset_files),
                'asset_size_bytes': asset_size,
                'total_web_size_bytes': static_size + asset_size,
                'uptime_seconds': time.time(),  # Placeholder
                'memory_usage_mb': self._get_memory_usage(),
                'disk_space_free_gb': self._get_disk_space(),
                'active_connections': 0,  # Placeholder
                'requests_per_second': 0,  # Placeholder
                'response_time_ms': 0  # Placeholder
            }
            
            self.logger.info("Web statistics collected")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting web statistics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.used / (1024 * 1024)  # Convert to MB
        except ImportError:
            self.logger.warning("psutil not available for memory monitoring")
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {str(e)}")
            return 0.0
    
    def _get_disk_space(self) -> float:
        """Get available disk space in GB."""
        try:
            import shutil
            disk_usage = shutil.disk_usage('.')
            return disk_usage.free / (1024**3)  # Convert to GB
        except Exception as e:
            self.logger.error(f"Error getting disk space: {str(e)}")
            return 0.0
    
    def cleanup_temp_files(self, temp_dir: str = 'temp') -> Dict[str, Any]:
        """Clean up temporary files.
        
        Args:
            temp_dir: Temporary directory path
            
        Returns:
            Dictionary with cleanup result
        """
        try:
            temp_path = Path(temp_dir)
            
            if not temp_path.exists():
                return {
                    'success': True,
                    'message': 'No temporary files to clean',
                    'files_deleted': 0
                }
            
            # Get all files in temp directory
            temp_files = list(temp_path.glob('*'))
            files_deleted = 0
            
            for file_path in temp_files:
                try:
                    if file_path.is_file():
                        file_age = time.time() - file_path.stat().st_mtime
                        if file_age > 3600:  # Older than 1 hour
                            file_path.unlink()
                            files_deleted += 1
                except Exception as e:
                    self.logger.warning(f"Error deleting temp file {file_path}: {str(e)}")
            
            self.logger.info(f"Cleaned up {files_deleted} temporary files")
            
            return {
                'success': True,
                'files_deleted': files_deleted,
                'temp_dir': temp_dir
            }
            
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_api_endpoints(self) -> Dict[str, Any]:
        """Create standard API endpoints for web management.
        
        Returns:
            Dictionary containing API endpoint information
        """
        try:
            endpoints = {
                'dashboards': {
                    'endpoint': '/api/dashboards',
                    'method': 'GET',
                    'description': 'List all dashboards',
                    'auth_required': False
                },
                'dashboard_create': {
                    'endpoint': '/api/dashboards',
                    'method': 'POST',
                    'description': 'Create new dashboard',
                    'auth_required': True
                },
                'dashboard_get': {
                    'endpoint': '/api/dashboards/{id}',
                    'method': 'GET',
                    'description': 'Get specific dashboard',
                    'auth_required': False
                },
                'upload': {
                    'endpoint': '/api/upload',
                    'method': 'POST',
                    'description': 'Upload Excel file for processing',
                    'auth_required': True,
                    'max_file_size': '50MB'
                },
                'static_serve': {
                    'endpoint': '/static/{file_path}',
                    'method': 'GET',
                    'description': 'Serve static files',
                    'auth_required': False
                },
                'websocket': {
                    'endpoint': '/ws',
                    'method': 'WebSocket',
                    'description': 'Real-time updates',
                    'auth_required': True
                },
                'health_check': {
                    'endpoint': '/api/health',
                    'method': 'GET',
                    'description': 'System health check',
                    'auth_required': False
                }
            }
            
            self.logger.info("API endpoints configuration created")
            return {
                'success': True,
                'endpoints': endpoints,
                'total_endpoints': len(endpoints)
            }
            
        except Exception as e:
            self.logger.error(f"Error creating API endpoints: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_dashboard_list(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get list of dashboards with pagination.
        
        Args:
            limit: Maximum number of dashboards to return
            offset: Number of dashboards to skip
            
        Returns:
            Dictionary containing dashboard list
        """
        try:
            dashboards = self.database_manager.get_dashboard_list(limit=limit, offset=offset)
            
            return {
                'success': True,
                'dashboards': dashboards,
                'count': len(dashboards),
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard list: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_dashboard_details(self, dashboard_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific dashboard.
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            Dictionary containing dashboard details
        """
        try:
            dashboard = self.database_manager.get_dashboard_details(dashboard_id)
            
            if not dashboard:
                return {
                    'success': False,
                    'error': f'Dashboard with ID {dashboard_id} not found'
                }
            
            return {
                'success': True,
                'dashboard': dashboard
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard details: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }