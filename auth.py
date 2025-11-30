#!/usr/bin/env python3
"""
AgentDaf1.1 Authentication System
JWT-based user authentication and authorization
"""

import jwt
import bcrypt
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from functools import wraps
from flask import request, jsonify, current_app

class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.token_expiry = timedelta(hours=24)
        self.refresh_token_expiry = timedelta(days=7)
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_tokens(self, user_data: Dict) -> Dict[str, str]:
        """Generate access and refresh tokens"""
        # Access token
        access_payload = {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'role': user_data.get('role', 'user'),
            'permissions': user_data.get('permissions', []),
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm='HS256')
        
        # Refresh token
        refresh_payload = {
            'user_id': user_data['user_id'],
            'exp': datetime.utcnow() + self.refresh_token_expiry,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm='HS256')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(self.token_expiry.total_seconds()),
            'refresh_expires_in': int(self.refresh_token_expiry.total_seconds())
        }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generate new access token from refresh token"""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return None
        
        # Get user data (in real app, fetch from database)
        user_data = {
            'user_id': payload['user_id'],
            'username': f'user_{payload["user_id"]}',
            'role': 'user',
            'permissions': ['read', 'write']
        }
        
        return self.generate_tokens(user_data)

class UserManager:
    """User management system"""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.auth_manager = AuthManager()
        
    def create_user(self, username: str, password: str, email: str = None, role: str = 'user') -> Dict:
        """Create a new user"""
        # Hash password
        hashed_password = self.auth_manager.hash_password(password)
        
        # Store user (in real app, save to database)
        user_data = {
            'user_id': len(username) + 1000,  # Simple ID generation
            'username': username,
            'email': email,
            'password_hash': hashed_password,
            'role': role,
            'permissions': self.get_role_permissions(role),
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True
        }
        
        # Log user creation
        if self.db_manager:
            self.db_manager.log_system_event(
                "INFO", 
                f"User created: {username}", 
                "auth"
            )
        
        return user_data
    
    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role"""
        role_permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users', 'system_config'],
            'moderator': ['read', 'write', 'moderate'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
        return role_permissions.get(role, ['read'])
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        # In real app, fetch from database
        # For demo, create a mock user if not exists
        if username == "admin" and password == "admin123":
            return self.create_user("admin", "admin123", "admin@agentdaf1.com", "admin")
        elif username == "user" and password == "user123":
            return self.create_user("user", "user123", "user@agentdaf1.com", "user")
        
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        # In real app, fetch from database
        return {
            'user_id': user_id,
            'username': f'user_{user_id}',
            'role': 'user',
            'permissions': ['read', 'write']
        }

# Decorators for Flask routes
def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check token in header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        auth_manager = AuthManager()
        payload = auth_manager.verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        if payload.get('type') != 'access':
            return jsonify({'error': 'Invalid token type'}), 401
        
        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

def role_required(*required_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role')
            if user_role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def permission_required(*required_permissions):
    """Decorator to require specific permissions"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_permissions = request.current_user.get('permissions', [])
            
            # Check if user has all required permissions
            if not all(perm in user_permissions for perm in required_permissions):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# Global instances
auth_manager = AuthManager()
user_manager = UserManager()

def get_auth_manager() -> AuthManager:
    """Get global auth manager instance"""
    return auth_manager

def get_user_manager() -> UserManager:
    """Get global user manager instance"""
    return user_manager

# Sample authentication endpoints for Flask
def create_auth_routes(app):
    """Create authentication routes for Flask app"""
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login endpoint"""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        username = data['username']
        password = data['password']
        
        # Authenticate user
        user = user_manager.authenticate_user(username, password)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate tokens
        tokens = auth_manager.generate_tokens(user)
        
        return jsonify({
            'status': 'success',
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'role': user['role'],
                'permissions': user['permissions']
            },
            'tokens': tokens
        })
    
    @app.route('/api/auth/refresh', methods=['POST'])
    def refresh_token():
        """Refresh access token"""
        data = request.get_json()
        
        if not data or not data.get('refresh_token'):
            return jsonify({'error': 'Refresh token required'}), 400
        
        refresh_token = data['refresh_token']
        tokens = auth_manager.refresh_access_token(refresh_token)
        
        if not tokens:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        return jsonify({
            'status': 'success',
            'tokens': tokens
        })
    
    @app.route('/api/auth/logout', methods=['POST'])
    @token_required
    def logout():
        """Logout endpoint (token invalidation would be handled server-side)"""
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        })
    
    @app.route('/api/auth/me', methods=['GET'])
    @token_required
    def get_current_user():
        """Get current user info"""
        return jsonify({
            'status': 'success',
            'user': {
                'user_id': request.current_user['user_id'],
                'username': request.current_user['username'],
                'role': request.current_user['role'],
                'permissions': request.current_user['permissions']
            }
        })
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Register new user"""
        data = request.get_json()
        
        required_fields = ['username', 'password', 'email']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Username, password, and email required'}), 400
        
        # Create user
        user = user_manager.create_user(
            data['username'],
            data['password'],
            data['email'],
            data.get('role', 'user')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 201