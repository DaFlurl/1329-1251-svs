"""
Security Tool for AgentDaf1.1
Security monitoring, validation, and protection utilities
"""

import hashlib
import secrets
import re
import time
import json
import ssl
import socket
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
import ipaddress

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: float
    event_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    source_ip: Optional[str]
    user_id: Optional[str]
    description: str
    details: Dict[str, Any]
    resolved: bool = False

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    name: str
    enabled: bool = True
    max_login_attempts: int = 5
    lockout_duration: int = 300  # seconds
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    session_timeout: int = 3600  # seconds
    allowed_ip_ranges: Optional[List[str]] = None
    blocked_ip_ranges: Optional[List[str]] = None

class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_password(password: str, policy: SecurityPolicy) -> Tuple[bool, List[str]]:
        """Validate password against security policy"""
        errors = []
        
        if len(password) < policy.password_min_length:
            errors.append(f"Password must be at least {policy.password_min_length} characters")
        
        if policy.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letters")
        
        if policy.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letters")
        
        if policy.password_require_numbers and not re.search(r'/d', password):
            errors.append("Password must contain numbers")
        
        if policy.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special characters")
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        
        if password.lower() in weak_passwords:
            errors.append("Password is too common")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+/.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_ip_allowed(ip: str, allowed_ranges: List[str], blocked_ranges: List[str]) -> bool:
        """Check if IP is allowed based on ranges"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check blocked ranges first
            for blocked_range in blocked_ranges or []:
                if ip_obj in ipaddress.ip_network(blocked_range, strict=False):
                    return False
            
            # If no allowed ranges, allow all (except blocked)
            if not allowed_ranges:
                return True
            
            # Check allowed ranges
            for allowed_range in allowed_ranges:
                if ip_obj in ipaddress.ip_network(allowed_range, strict=False):
                    return True
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not input_string:
            return ""
        
        # Limit length
        if len(input_string) > max_length:
            input_string = input_string[:max_length]
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '/x00', '/n', '/r', '/t']
        for char in dangerous_chars:
            input_string = input_string.replace(char, '')
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(/b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)/b)',
            r'(--|#|//*|/*/)',
            r'(/bOR/b.*=.*/bOR/b)',
            r'(/bAND/b.*=.*/bAND/b)',
            r'(/'/'.*/'/')',
            r'(1=1|1 = 1)'
        ]
        
        for pattern in sql_patterns:
            input_string = re.sub(pattern, '', input_string, flags=re.IGNORECASE)
        
        return input_string.strip()
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return password_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash, _ = SecurityValidator.hash_password(password, salt)
        return computed_hash == password_hash

class SecurityMonitor:
    """Security monitoring and event tracking"""
    
    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self.events: deque = deque(maxlen=max_events)
        self.policies: Dict[str, SecurityPolicy] = {}
        self.blocked_ips: Dict[str, float] = {}  # IP -> unblock_time
        self.failed_attempts: Dict[str, List[float]] = defaultdict(list)
        self.active_sessions: Dict[str, Dict] = {}
        
        # Setup default policy
        self.policies["default"] = SecurityPolicy(
            name="default",
            max_login_attempts=5,
            lockout_duration=300,
            password_min_length=8
        )
    
    def add_policy(self, policy: SecurityPolicy):
        """Add security policy"""
        self.policies[policy.name] = policy
        logger.info(f"Added security policy: {policy.name}")
    
    def get_policy(self, name: str = "default") -> SecurityPolicy:
        """Get security policy"""
        return self.policies.get(name, self.policies["default"])
    
    def log_event(self, event_type: str, severity: str, description: str,
                  source_ip: str = None, user_id: str = None, **details):
        """Log security event"""
        event = SecurityEvent(
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            description=description,
            details=details
        )
        
        self.events.append(event)
        
        # Log to system logger
        log_level = {
            "LOW": logging.INFO,
            "MEDIUM": logging.WARNING,
            "HIGH": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }.get(severity, logging.INFO)
        
        logger.log(log_level, f"Security Event: {description}", extra=details)
        
        # Auto-block IPs for critical events
        if severity == "CRITICAL" and source_ip:
            self.block_ip(source_ip, duration=3600)  # 1 hour
    
    def record_failed_login(self, username: str, ip: str, policy_name: str = "default"):
        """Record failed login attempt"""
        policy = self.get_policy(policy_name)
        key = f"{username}@{ip}"
        
        self.failed_attempts[key].append(time.time())
        
        # Clean old attempts (older than lockout duration)
        cutoff_time = time.time() - policy.lockout_duration
        self.failed_attempts[key] = [
            attempt for attempt in self.failed_attempts[key] 
            if attempt > cutoff_time
        ]
        
        # Check if should block
        if len(self.failed_attempts[key]) >= policy.max_login_attempts:
            self.block_ip(ip, policy.lockout_duration)
            self.log_event(
                "LOGIN_BLOCKED",
                "HIGH",
                f"IP blocked due to multiple failed login attempts",
                source_ip=ip,
                user_id=username,
                attempts=len(self.failed_attempts[key])
            )
    
    def block_ip(self, ip: str, duration: int = 300):
        """Block IP address for specified duration"""
        unblock_time = time.time() + duration
        self.blocked_ips[ip] = unblock_time
        
        self.log_event(
            "IP_BLOCKED",
            "MEDIUM",
            f"IP address blocked for {duration} seconds",
            source_ip=ip
        )
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        if ip not in self.blocked_ips:
            return False
        
        # Check if block has expired
        if time.time() > self.blocked_ips[ip]:
            del self.blocked_ips[ip]
            return False
        
        return True
    
    def create_session(self, user_id: str, ip: str, policy_name: str = "default") -> str:
        """Create user session"""
        policy = self.get_policy(policy_name)
        session_id = SecurityValidator.generate_secure_token()
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "ip": ip,
            "created_at": time.time(),
            "last_activity": time.time(),
            "expires_at": time.time() + policy.session_timeout
        }
        
        self.active_sessions[session_id] = session_data
        
        self.log_event(
            "SESSION_CREATED",
            "LOW",
            f"Session created for user {user_id}",
            source_ip=ip,
            user_id=user_id,
            session_id=session_id
        )
        
        return session_id
    
    def validate_session(self, session_id: str, ip: str = None) -> Optional[Dict]:
        """Validate session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # Check expiration
        if time.time() > session["expires_at"]:
            del self.active_sessions[session_id]
            return None
        
        # Check IP if provided
        if ip and session["ip"] != ip:
            self.log_event(
                "SESSION_IP_MISMATCH",
                "HIGH",
                f"Session IP mismatch for user {session['user_id']}",
                source_ip=ip,
                user_id=session["user_id"],
                session_id=session_id,
                original_ip=session["ip"]
            )
            return None
        
        # Update last activity
        session["last_activity"] = time.time()
        
        return session
    
    def destroy_session(self, session_id: str):
        """Destroy session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            del self.active_sessions[session_id]
            
            self.log_event(
                "SESSION_DESTROYED",
                "LOW",
                f"Session destroyed for user {session['user_id']}",
                user_id=session["user_id"],
                session_id=session_id
            )
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time > session["expires_at"]:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.destroy_session(session_id)
    
    def get_events(self, 
                   hours: int = 24,
                   severity: str = None,
                   event_type: str = None,
                   source_ip: str = None) -> List[SecurityEvent]:
        """Get security events with filters"""
        cutoff_time = time.time() - (hours * 3600)
        filtered_events = []
        
        for event in self.events:
            if event.timestamp < cutoff_time:
                continue
            
            if severity and event.severity != severity:
                continue
            
            if event_type and event.event_type != event_type:
                continue
            
            if source_ip and event.source_ip != source_ip:
                continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary statistics"""
        current_time = time.time()
        last_24h = current_time - 24 * 3600
        
        events_24h = [e for e in self.events if e.timestamp > last_24h]
        
        severity_counts = defaultdict(int)
        event_type_counts = defaultdict(int)
        
        for event in events_24h:
            severity_counts[event.severity] += 1
            event_type_counts[event.event_type] += 1
        
        return {
            "total_events_24h": len(events_24h),
            "severity_breakdown": dict(severity_counts),
            "event_type_breakdown": dict(event_type_counts),
            "blocked_ips": len(self.blocked_ips),
            "active_sessions": len(self.active_sessions),
            "failed_login_attempts": sum(len(attempts) for attempts in self.failed_attempts.values()),
            "policies": list(self.policies.keys())
        }
    
    def export_events(self, filepath: str, hours: int = 24) -> bool:
        """Export security events to file"""
        try:
            events = self.get_events(hours=hours)
            
            data = {
                "export_time": time.time(),
                "hours_covered": hours,
                "events": [asdict(event) for event in events],
                "summary": self.get_security_summary()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Security events exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting security events: {e}")
            return False

class SSLChecker:
    """SSL/TLS certificate checker"""
    
    @staticmethod
    def check_ssl_certificate(hostname: str, port: int = 443) -> Dict[str, Any]:
        """Check SSL certificate for hostname"""
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Safely extract certificate information
                    subject = dict(x[0] for x in cert.get("subject", [])) if cert.get("subject") else {}
                    issuer = dict(x[0] for x in cert.get("issuer", [])) if cert.get("issuer") else {}
                    
                    return {
                        "valid": True,
                        "subject": subject,
                        "issuer": issuer,
                        "version": cert.get("version", ""),
                        "serial_number": cert.get("serialNumber", ""),
                        "not_before": cert.get("notBefore", ""),
                        "not_after": cert.get("notAfter", ""),
                        "subject_alt_name": cert.get("subjectAltName", []),
                        "signature_algorithm": cert.get("signatureAlgorithm", ""),
                        "ocsp": cert.get("OCSP", []),
                        "ca_issuers": cert.get("caIssuers", [])
                    }
                    
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    @staticmethod
    def check_ssl_expiration(hostname: str, port: int = 443, days_threshold: int = 30) -> Dict[str, Any]:
        """Check if SSL certificate is expiring soon"""
        cert_info = SSLChecker.check_ssl_certificate(hostname, port)
        
        if not cert_info["valid"]:
            return cert_info
        
        try:
            from datetime import datetime
            import dateutil.parser
            
            expiry_date = dateutil.parser.parse(cert_info["not_after"])
            current_date = datetime.now()
            days_until_expiry = (expiry_date - current_date).days
            
            return {
                "valid": True,
                "expiry_date": cert_info["not_after"],
                "days_until_expiry": days_until_expiry,
                "expiring_soon": days_until_expiry <= days_threshold,
                "expired": days_until_expiry < 0
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error parsing expiry date: {e}"
            }

# Global security monitor instance
security_monitor = SecurityMonitor()