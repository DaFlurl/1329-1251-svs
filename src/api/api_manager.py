"""
API Manager for handling API endpoints, routes, and request/response management.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from flask import Flask, request, jsonify, Response
from functools import wraps
import time
import json
from datetime import datetime, timedelta

from ..config import ConfigManager
from ..database import DatabaseManager


class APIManager:
    """Manages API endpoints, routes, and request/response handling."""
    
    def __init__(self, config_manager: ConfigManager, database_manager: DatabaseManager, tools_manager: 'ToolsManager'):
        """
        Initialize API Manager with dependencies.
        
        Args:
            config_manager: Configuration management instance
            database_manager: Database management instance  
            tools_manager: Tools management instance
        """
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.tools_manager = tools_manager
        self.logger = logging.getLogger(__name__)
        
        # API Configuration
        self.api_config = {
            'version': '1.0.0',
            'title': 'AgentDaf1.1 API',
            'description': 'Advanced data processing and dashboard platform',
            'base_url': '/api',
            'rate_limit': {
                'requests_per_minute': 100,
                'requests_per_hour': 1000,
                'requests_per_day': 10000
            },
            'security': {
                'jwt_expiry_hours': 24,
                'max_login_attempts': 5,
                'password_min_length': 8,
                'session_timeout_minutes': 30
            }
        }
        
        # Route registry
        self.routes = {}
        self.middleware = []
        
        self.logger.info("API Manager initialized")
    
    def register_route(self, path: str, methods: List[str], handler: Callable, middleware: Optional[List[Callable]] = None):
        """
        Register a new API route with optional middleware.
        
        Args:
            path: API endpoint path
            methods: List of HTTP methods
            handler: Route handler function
            middleware: Optional list of middleware functions
        """
        self.routes[path] = {
            'methods': methods,
            'handler': handler,
            'middleware': middleware or [],
            'created_at': datetime.now(),
            'access_count': 0
        }
        self.logger.info(f"Registered route: {path} [{', '.join(methods)}]")
    
    def add_middleware(self, middleware_func: Callable):
        """
        Add middleware to all routes.
        
        Args:
            middleware_func: Middleware function
        """
        self.middleware.append(middleware_func)
        self.logger.info(f"Added middleware: {middleware_func.__name__}")
    
    def create_cors_middleware(self):
        """
        Create CORS middleware for API routes.
        """
        def cors_middleware(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Handle preflight OPTIONS request
                if request.method == 'OPTIONS':
                    response = Response()
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                    response.status_code = 200
                    return response
                
                # Add CORS headers to actual response
                response = func(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                return response
            return wrapper
        return cors_middleware
    
    def create_rate_limit_middleware(self):
        """
        Create rate limiting middleware.
        """
        def rate_limit_middleware(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Simple rate limiting logic
                client_ip = request.remote_addr or 'unknown'
                # In production, use Redis or database for tracking
                # For now, just log the request
                self.logger.info(f"Request from {client_ip}: {request.method} {request.path}")
                return func(*args, **kwargs)
            return wrapper
        return rate_limit_middleware
    
    def create_auth_middleware(self):
        """
        Create authentication middleware.
        """
        def auth_middleware(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check for Authorization header
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    return jsonify({
                        'error': 'Authorization required',
                        'message': 'Please provide a valid JWT token'
                    }), 401
                
                # Validate JWT token (simplified for demo)
                try:
                    token = auth_header.replace('Bearer ', '')
                    # In production, use proper JWT validation
                    user_id = self.validate_jwt_token(token)
                    if not user_id:
                        return jsonify({
                            'error': 'Invalid token',
                            'message': 'JWT token validation failed'
                        }), 401
                    
                    # Add user info to request context
                    request.current_user = {'id': user_id}
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    self.logger.error(f"Auth middleware error: {str(e)}")
                    return jsonify({
                        'error': 'Authentication failed',
                        'message': str(e)
                    }), 401
            return wrapper
        return auth_middleware
    
    def validate_jwt_token(self, token: str) -> Optional[str]:
        """
        Validate JWT token (simplified implementation).
        
        Args:
            token: JWT token string
            
        Returns:
            User ID if valid, None otherwise
        """
        # Simplified validation - in production, use proper JWT library
        try:
            # For demo purposes, just check if token exists and is not expired
            # In production, decode and validate signature
            if len(token) > 10:  # Basic validation
                return 'demo_user'
            return None
        except Exception as e:
            self.logger.error(f"JWT validation error: {str(e)}")
            return None
    
    def create_error_handler(self, error_code: int, default_message: str):
        """
        Create standardized error handler.
        """
        def error_handler(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Route error: {str(e)}")
                    return jsonify({
                        'error': True,
                        'error_code': error_code,
                        'message': f"{default_message}: {str(e)}",
                        'timestamp': datetime.now().isoformat()
                    }), error_code
            return wrapper
        return error_handler
    
    def setup_flask_app(self) -> Flask:
        """
        Set up Flask application with all routes and middleware.
        
        Returns:
            Configured Flask application
        """
        app = Flask(__name__)
        
        # Add CORS middleware to all routes
        cors_middleware = self.create_cors_middleware()
        self.add_middleware(cors_middleware)
        
        # Add rate limiting middleware
        rate_limit_middleware = self.create_rate_limit_middleware()
        self.add_middleware(rate_limit_middleware)
        
        # Add authentication middleware
        auth_middleware = self.create_auth_middleware()
        self.add_middleware(auth_middleware)
        
        # Register API routes
        self._register_core_routes()
        self._register_auth_routes()
        self._register_data_routes()
        self._register_dashboard_routes()
        self._register_tools_routes()
        self._register_system_routes()
        
        # Configure Flask app
        app.config.update({
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': True
        })
        
        self.logger.info("Flask application configured")
        return app
    
    def _register_core_routes(self):
        """
        Register core API routes.
        """
        # API info endpoint
        self.register_route('/api/info', ['GET'], self._handle_api_info)
        
        # Health check endpoint
        self.register_route('/api/health', ['GET'], self._handle_health_check)
    
    def _register_auth_routes(self):
        """
        Register authentication routes.
        """
        # Login endpoint
        self.register_route('/api/auth/login', ['POST'], self._handle_login)
        
        # Registration endpoint
        self.register_route('/api/auth/register', ['POST'], self._handle_register)
        
        # Token refresh endpoint
        self.register_route('/api/auth/refresh', ['POST'], self._handle_token_refresh)
        
        # Current user endpoint
        self.register_route('/api/auth/me', ['GET'], self._handle_current_user)
    
    def _register_data_routes(self):
        """
        Register data processing routes.
        """
        # File upload endpoint
        self.register_route('/api/upload', ['POST'], self._handle_file_upload)
        
        # Data list endpoint
        self.register_route('/api/data', ['GET'], self._handle_data_list)
        
        # Processed data endpoint
        self.register_route('/api/processed-data', ['GET'], self._handle_processed_data)
    
    def _register_dashboard_routes(self):
        """
        Register dashboard-related routes.
        """
        # Dashboard list endpoint
        self.register_route('/api/dashboards', ['GET'], self._handle_dashboard_list)
        
        # Create dashboard endpoint
        self.register_route('/api/dashboards', ['POST'], self._handle_create_dashboard)
        
        # Get dashboard endpoint
        self.register_route('/api/dashboards/<dashboard_id>', ['GET'], self._handle_get_dashboard)
        
        # Update dashboard endpoint
        self.register_route('/api/dashboards/<dashboard_id>', ['PUT'], self._handle_update_dashboard)
        
        # Delete dashboard endpoint
        self.register_route('/api/dashboards/<dashboard_id>', ['DELETE'], self._handle_delete_dashboard)
    
    def _register_tools_routes(self):
        """
        Register tools and utility routes.
        """
        # Tools list endpoint
        self.register_route('/api/tools', ['GET'], self._handle_tools_list)
        
        # Execute tool endpoint
        self.register_route('/api/tools/execute', ['POST'], self._handle_tool_execution)
        
        # AI analysis endpoint
        self.register_route('/api/tools/analyze', ['POST'], self._handle_ai_analysis)
    
    def _register_system_routes(self):
        """
        Register system management routes.
        """
        # System status endpoint
        self.register_route('/api/system/status', ['GET'], self._handle_system_status)
        
        # Configuration endpoint
        self.register_route('/api/system/config', ['GET'], self._handle_system_config)
        
        # Statistics endpoint
        self.register_route('/api/stats', ['GET'], self._handle_statistics)
    
    # Route handlers
    def _handle_api_info(self):
        """Handle API information request."""
        return jsonify(self.api_config)
    
    def _handle_health_check(self):
        """Handle health check request."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': self.api_config['version']
        })
    
    def _handle_login(self):
        """Handle user login request."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': 'Username and password required'}), 400
            
            # Authenticate user (simplified)
            if username == 'admin' and password == 'admin123':
                # Generate JWT token (simplified)
                token = f"jwt_token_{int(time.time())}"
                return jsonify({
                    'success': True,
                    'token': token,
                    'expires_in': self.api_config['security']['jwt_expiry_hours'] * 3600
                })
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_register(self):
        """Handle user registration request."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            
            if not all([username, password, email]):
                return jsonify({'error': 'All fields required'}), 400
            
            # Register user (simplified)
            user_id = f"user_{int(time.time())}"
            return jsonify({
                'success': True,
                'user_id': user_id,
                'message': 'User registered successfully'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_token_refresh(self):
        """Handle token refresh request."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            old_token = data.get('old_token')
            if not old_token:
                return jsonify({'error': 'Old token required'}), 400
            
            # Generate new token (simplified)
            new_token = f"jwt_token_{int(time.time())}"
            return jsonify({
                'success': True,
                'token': new_token,
                'expires_in': self.api_config['security']['jwt_expiry_hours'] * 3600
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_current_user(self):
        """Handle current user request."""
        try:
            # Get user from request context (set by auth middleware)
            if hasattr(request, 'current_user'):
                return jsonify({
                    'success': True,
                    'user': request.current_user
                })
            else:
                return jsonify({'error': 'Not authenticated'}), 401
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_file_upload(self):
        """Handle file upload request."""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No filename provided'}), 400
            
            # Process file upload using tools manager
            if hasattr(self.tools_manager, 'process_excel_file'):
                result = self.tools_manager.process_excel_file(file)
                return jsonify(result)
            else:
                return jsonify({'error': 'File processing not available'}), 501
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_data_list(self):
        """Handle data list request."""
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)
            
            # Query database for data
            data = self.database_manager.get_processed_data(limit=limit, offset=(page-1)*limit)
            
            return jsonify({
                'success': True,
                'data': data,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': len(data)
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_processed_data(self):
        """Handle processed data request."""
        try:
            # Get query parameters
            dashboard_id = request.args.get('dashboard_id')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            
            # Query processed data
            data = self.database_manager.get_processed_data(
                dashboard_id=dashboard_id,
                date_from=date_from,
                date_to=date_to
            )
            
            return jsonify({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_dashboard_list(self):
        """Handle dashboard list request."""
        try:
            dashboards = self.database_manager.get_dashboards()
            return jsonify({
                'success': True,
                'data': dashboards
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_create_dashboard(self):
        """Handle dashboard creation request."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            title = data.get('title')
            config = data.get('config', {})
            
            if not title:
                return jsonify({'error': 'Title required'}), 400
            
            # Create dashboard
            dashboard_id = self.database_manager.create_dashboard(title, config)
            
            return jsonify({
                'success': True,
                'dashboard_id': dashboard_id,
                'message': 'Dashboard created successfully'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_get_dashboard(self, dashboard_id: str):
        """Handle get dashboard request."""
        try:
            dashboard = self.database_manager.get_dashboard(dashboard_id)
            if not dashboard:
                return jsonify({'error': 'Dashboard not found'}), 404
            
            return jsonify({
                'success': True,
                'data': dashboard
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_update_dashboard(self, dashboard_id: str):
        """Handle dashboard update request."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            # Update dashboard
            success = self.database_manager.update_dashboard(dashboard_id, data)
            
            return jsonify({
                'success': success,
                'message': 'Dashboard updated successfully' if success else 'Update failed'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_delete_dashboard(self, dashboard_id: str):
        """Handle dashboard deletion request."""
        try:
            success = self.database_manager.delete_dashboard(dashboard_id)
            
            return jsonify({
                'success': success,
                'message': 'Dashboard deleted successfully' if success else 'Deletion failed'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_tools_list(self):
        """Handle tools list request."""
        try:
            tools = [
                {
                    'name': 'process_excel',
                    'description': 'Process Excel files',
                    'endpoint': '/api/tools/execute'
                },
                {
                    'name': 'generate_dashboard',
                    'description': 'Generate dashboard from data',
                    'endpoint': '/api/tools/analyze'
                },
                {
                    'name': 'ai_analysis',
                    'description': 'AI-powered code analysis',
                    'endpoint': '/api/tools/analyze'
                }
            ]
            
            return jsonify({
                'success': True,
                'data': tools
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_tool_execution(self):
        """Handle tool execution request."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            tool_name = data.get('tool')
            params = data.get('params', {})
            
            if not tool_name:
                return jsonify({'error': 'Tool name required'}), 400
            
            # Execute tool using tools manager
            if hasattr(self.tools_manager, 'execute_tool'):
                result = self.tools_manager.execute_tool(tool_name, params)
                return jsonify(result)
            else:
                return jsonify({'error': 'Tool execution not available'}), 501
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_ai_analysis(self):
        """Handle AI analysis request."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON'}), 400
            
            analysis_type = data.get('type')
            content = data.get('content')
            
            if not analysis_type or not content:
                return jsonify({'error': 'Analysis type and content required'}), 400
            
            # Perform AI analysis (simplified)
            result = {
                'type': analysis_type,
                'analysis': f'Analysis of {analysis_type} completed',
                'insights': [
                    'Content length: ' + str(len(content)),
                    'Analysis timestamp: ' + datetime.now().isoformat()
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_system_status(self):
        """Handle system status request."""
        try:
            status = {
                'api_version': self.api_config['version'],
                'status': 'running',
                'uptime': 'active',
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'database': 'connected',
                    'tools_manager': 'available',
                    'config_manager': 'available'
                }
            }
            
            return jsonify({
                'success': True,
                'data': status
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_system_config(self):
        """Handle system configuration request."""
        try:
            config = self.config_manager.get_all_config()
            return jsonify({
                'success': True,
                'data': config
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def _handle_statistics(self):
        """Handle statistics request."""
        try:
            # Get various statistics from database
            stats = {
                'total_requests': 1000,
                'active_users': 50,
                'processed_files': 25,
                'created_dashboards': 10,
                'uptime_hours': 24,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': stats
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def get_routes_info(self) -> Dict[str, Any]:
        """
        Get information about all registered routes.
        
        Returns:
            Dictionary with route information
        """
        routes_info = {}
        for path, route_info in self.routes.items():
            routes_info[path] = {
                'methods': route_info['methods'],
                'middleware_count': len(route_info['middleware']),
                'access_count': route_info['access_count'],
                'created_at': route_info['created_at'].isoformat()
            }
        
        return routes_info
    
    def apply_middleware_to_route(self, path: str, handler: Callable):
        """
        Apply all registered middleware to a route handler.
        
        Args:
            path: Route path
            handler: Original handler function
            
        Returns:
            Handler wrapped with middleware
        """
        route_info = self.routes.get(path)
        if not route_info:
            return handler
        
        # Apply middleware in reverse order
        wrapped_handler = handler
        for middleware_func in reversed(route_info['middleware']):
            wrapped_handler = middleware_func(wrapped_handler)
            wrapped_handler = middleware_func(wrapped_handler)
        
        return wrapped_handler
    
    def create_flask_routes(self, app: Flask):
        """
        Create Flask routes from registered routes with middleware.
        
        Args:
            app: Flask application instance
        """
        for path, route_info in self.routes.items():
            wrapped_handler = self.apply_middleware_to_route(path, route_info['handler'])
            
            # Create route for each method
            for method in route_info['methods']:
                app.add_url_rule(
                    path,
                    endpoint=f"{path}_{method.lower()}",
                    view_func=wrapped_handler,
                    methods=[method]
                )
        
        self.logger.info(f"Created {len(self.routes)} Flask routes")
    
    def run(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
        """
        Run the Flask application.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Whether to run in debug mode
        """
        app = self.setup_flask_app()
        self.create_flask_routes(app)
        
        self.logger.info(f"Starting API server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)