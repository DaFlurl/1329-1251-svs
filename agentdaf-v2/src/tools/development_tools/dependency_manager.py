#!/usr/bin/env python3
"""
Dependency Manager Tool
Manages package dependencies, vulnerability scanning, automated updates, and license compliance.
"""

import os
import sys
import json
import sqlite3
import threading
import subprocess
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import packaging.version
import packaging.requirements

@dataclass
class Package:
    """Represents a package dependency"""
    name: str
    version: str
    installed_version: Optional[str] = None
    latest_version: Optional[str] = None
    license: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    dependencies: List[str] = None
    vulnerabilities: List[Dict] = None
    update_available: bool = False
    security_risk: bool = False
    last_checked: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.vulnerabilities is None:
            self.vulnerabilities = []

@dataclass
class Vulnerability:
    """Represents a security vulnerability"""
    id: str
    package_name: str
    affected_versions: List[str]
    patched_versions: List[str]
    severity: str  # low, medium, high, critical
    description: str
    references: List[str]
    discovered_date: str
    cve_id: Optional[str] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []

@dataclass
class UpdatePolicy:
    """Represents an update policy"""
    name: str
    auto_update: bool = False
    update_schedule: str = "weekly"  # daily, weekly, monthly
    allow_major_updates: bool = False
    allow_pre_release: bool = False
    exclude_packages: List[str] = None
    include_only: List[str] = None
    license_whitelist: List[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.exclude_packages is None:
            self.exclude_packages = []
        if self.include_only is None:
            self.include_only = []
        if self.license_whitelist is None:
            self.license_whitelist = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class DependencyManager:
    """Manages package dependencies and security"""
    
    def __init__(self, db_path: str = "dependency_manager.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        
        # Package manager configurations
        self.package_managers = {
            'pip': {
                'list_cmd': ['pip', 'list', '--format=json'],
                'install_cmd': ['pip', 'install'],
                'uninstall_cmd': ['pip', 'uninstall', '-y'],
                'outdated_cmd': ['pip', 'list', '--outdated', '--format=json'],
                'requirements_file': 'requirements.txt',
                'lock_file': 'requirements.lock'
            },
            'npm': {
                'list_cmd': ['npm', 'list', '--json', '--depth=0'],
                'install_cmd': ['npm', 'install'],
                'uninstall_cmd': ['npm', 'uninstall'],
                'outdated_cmd': ['npm', 'outdated', '--json'],
                'requirements_file': 'package.json',
                'lock_file': 'package-lock.json'
            },
            'yarn': {
                'list_cmd': ['yarn', 'list', '--json', '--depth=0'],
                'install_cmd': ['yarn', 'add'],
                'uninstall_cmd': ['yarn', 'remove'],
                'outdated_cmd': ['yarn', 'outdated', '--json'],
                'requirements_file': 'package.json',
                'lock_file': 'yarn.lock'
            }
        }
        
        # Vulnerability databases
        self.vulnerability_sources = [
            'https://pypi.org/pypi',
            'https://osv.dev/v1/',
            'https://api.github.com/advisories'
        ]
        
        # License categories
        self.license_categories = {
            'permissive': ['MIT', 'BSD', 'Apache-2.0', 'ISC', 'Unlicense'],
            'copyleft': ['GPL', 'LGPL', 'AGPL', 'MPL'],
            'commercial': ['Commercial', 'Proprietary'],
            'uncategorized': []
        }
    
    def _init_database(self):
        """Initialize SQLite database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS packages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    installed_version TEXT,
                    latest_version TEXT,
                    license TEXT,
                    description TEXT,
                    homepage TEXT,
                    dependencies TEXT,
                    vulnerabilities TEXT,
                    update_available BOOLEAN DEFAULT FALSE,
                    security_risk BOOLEAN DEFAULT FALSE,
                    last_checked TEXT,
                    package_manager TEXT DEFAULT 'pip',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, version, package_manager)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vulnerability_id TEXT NOT NULL,
                    package_name TEXT NOT NULL,
                    affected_versions TEXT,
                    patched_versions TEXT,
                    severity TEXT,
                    description TEXT,
                    references TEXT,
                    discovered_date TEXT,
                    cve_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(vulnerability_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS update_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    auto_update BOOLEAN DEFAULT FALSE,
                    update_schedule TEXT DEFAULT 'weekly',
                    allow_major_updates BOOLEAN DEFAULT FALSE,
                    allow_pre_release BOOLEAN DEFAULT FALSE,
                    exclude_packages TEXT,
                    include_only TEXT,
                    license_whitelist TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_type TEXT NOT NULL,
                    package_manager TEXT DEFAULT 'pip',
                    total_packages INTEGER,
                    vulnerable_packages INTEGER,
                    outdated_packages INTEGER,
                    scan_duration REAL,
                    scan_results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS update_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_name TEXT NOT NULL,
                    old_version TEXT,
                    new_version TEXT,
                    update_type TEXT,
                    package_manager TEXT DEFAULT 'pip',
                    success BOOLEAN,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_packages_name ON packages(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_packages_update_available ON packages(update_available)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_packages_security_risk ON packages(security_risk)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vulnerabilities_package ON vulnerabilities(package_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity)")
    
    def scan_dependencies(self, package_manager: str = 'pip', project_path: str = None) -> Dict[str, Any]:
        """Scan project dependencies"""
        try:
            with self.lock:
                start_time = datetime.now()
                
                if package_manager not in self.package_managers:
                    raise ValueError(f"Unsupported package manager: {package_manager}")
                
                # Get installed packages
                installed_packages = self._get_installed_packages(package_manager, project_path)
                
                # Get outdated packages
                outdated_packages = self._get_outdated_packages(package_manager, project_path)
                
                # Check for vulnerabilities
                vulnerable_packages = self._check_vulnerabilities(installed_packages)
                
                # Update database
                self._update_packages_database(installed_packages, package_manager)
                
                # Record scan history
                scan_duration = (datetime.now() - start_time).total_seconds()
                self._record_scan_history(
                    scan_type="full_dependency_scan",
                    package_manager=package_manager,
                    total_packages=len(installed_packages),
                    vulnerable_packages=len(vulnerable_packages),
                    outdated_packages=len(outdated_packages),
                    scan_duration=scan_duration,
                    scan_results={
                        'installed_packages': len(installed_packages),
                        'outdated_packages': len(outdated_packages),
                        'vulnerable_packages': len(vulnerable_packages)
                    }
                )
                
                return {
                    'status': 'success',
                    'package_manager': package_manager,
                    'installed_packages': len(installed_packages),
                    'outdated_packages': len(outdated_packages),
                    'vulnerable_packages': len(vulnerable_packages),
                    'scan_duration': scan_duration,
                    'packages': [asdict(pkg) for pkg in installed_packages],
                    'outdated': outdated_packages,
                    'vulnerable': vulnerable_packages
                }
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _get_installed_packages(self, package_manager: str, project_path: str = None) -> List[Package]:
        """Get list of installed packages"""
        try:
            config = self.package_managers[package_manager]
            cmd = config['list_cmd'].copy()
            
            # Change to project directory if specified
            cwd = project_path if project_path else None
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
            
            if result.returncode != 0:
                raise Exception(f"Failed to list packages: {result.stderr}")
            
            packages_data = json.loads(result.stdout)
            packages = []
            
            if package_manager == 'pip':
                for pkg_data in packages_data:
                    package = Package(
                        name=pkg_data['name'],
                        version=pkg_data['version'],
                        installed_version=pkg_data['version']
                    )
                    packages.append(package)
            
            elif package_manager in ['npm', 'yarn']:
                dependencies = packages_data.get('dependencies', {})
                for name, info in dependencies.items():
                    package = Package(
                        name=name,
                        version=info.get('version', 'unknown'),
                        installed_version=info.get('version', 'unknown')
                    )
                    packages.append(package)
            
            return packages
            
        except Exception as e:
            raise Exception(f"Error getting installed packages: {str(e)}")
    
    def _get_outdated_packages(self, package_manager: str, project_path: str = None) -> List[Dict]:
        """Get list of outdated packages"""
        try:
            config = self.package_managers[package_manager]
            cmd = config['outdated_cmd'].copy()
            
            cwd = project_path if project_path else None
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
            
            if result.returncode != 0:
                return []  # Some package managers return non-zero for no outdated packages
            
            outdated = []
            
            if package_manager == 'pip':
                try:
                    outdated_data = json.loads(result.stdout)
                    for pkg_data in outdated_data:
                        outdated.append({
                            'name': pkg_data['name'],
                            'current_version': pkg_data['version'],
                            'latest_version': pkg_data['latest_version'],
                            'type': pkg_data.get('type', 'minor')
                        })
                except json.JSONDecodeError:
                    pass  # No outdated packages
            
            elif package_manager in ['npm', 'yarn']:
                try:
                    outdated_data = json.loads(result.stdout)
                    # Parse npm/yarn outdated format
                    for name, info in outdated_data.items():
                        outdated.append({
                            'name': name,
                            'current_version': info.get('current', 'unknown'),
                            'latest_version': info.get('latest', 'unknown'),
                            'type': self._determine_update_type(info.get('current', ''), info.get('latest', ''))
                        })
                except json.JSONDecodeError:
                    pass
            
            return outdated
            
        except Exception as e:
            raise Exception(f"Error getting outdated packages: {str(e)}")
    
    def _determine_update_type(self, current: str, latest: str) -> str:
        """Determine the type of update (major, minor, patch)"""
        try:
            current_ver = packaging.version.parse(current)
            latest_ver = packaging.version.parse(latest)
            
            if current_ver.major < latest_ver.major:
                return 'major'
            elif current_ver.minor < latest_ver.minor:
                return 'minor'
            elif current_ver.micro < latest_ver.micro:
                return 'patch'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def _check_vulnerabilities(self, packages: List[Package]) -> List[Dict]:
        """Check packages for known vulnerabilities"""
        vulnerable_packages = []
        
        for package in packages:
            try:
                # Check against local vulnerability database
                vulnerabilities = self._get_package_vulnerabilities(package.name, package.version)
                
                if vulnerabilities:
                    package.vulnerabilities = vulnerabilities
                    package.security_risk = True
                    vulnerable_packages.append({
                        'package': package.name,
                        'version': package.version,
                        'vulnerabilities': [asdict(vuln) for vuln in vulnerabilities]
                    })
                
                # Update package with latest info from PyPI/npm
                self._update_package_info(package)
                
            except Exception as e:
                continue  # Skip package if vulnerability check fails
        
        return vulnerable_packages
    
    def _get_package_vulnerabilities(self, package_name: str, version: str) -> List[Vulnerability]:
        """Get vulnerabilities for a specific package version"""
        vulnerabilities = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM vulnerabilities 
                    WHERE package_name = ? AND (
                        affected_versions LIKE ? OR 
                        affected_versions = '*'
                    )
                """, (package_name, f'%{version}%'))
                
                rows = cursor.fetchall()
                
                for row in rows:
                    vulnerability = Vulnerability(
                        id=row[1],
                        package_name=row[2],
                        affected_versions=json.loads(row[3]) if row[3] else [],
                        patched_versions=json.loads(row[4]) if row[4] else [],
                        severity=row[5],
                        description=row[6],
                        references=json.loads(row[7]) if row[7] else [],
                        discovered_date=row[8],
                        cve_id=row[9]
                    )
                    vulnerabilities.append(vulnerability)
                    
        except Exception as e:
            pass
        
        return vulnerabilities
    
    def _update_package_info(self, package: Package):
        """Update package with latest information from package registry"""
        try:
            # For Python packages, check PyPI
            if hasattr(self, '_get_pypi_info'):
                pypi_info = self._get_pypi_info(package.name)
                if pypi_info:
                    package.latest_version = pypi_info.get('latest_version')
                    package.description = pypi_info.get('description')
                    package.license = pypi_info.get('license')
                    package.homepage = pypi_info.get('homepage')
                    package.update_available = (
                        package.installed_version != package.latest_version and
                        package.latest_version is not None
                    )
                    package.last_checked = datetime.now().isoformat()
        except:
            pass  # Skip if package info update fails
    
    def _get_pypi_info(self, package_name: str) -> Optional[Dict]:
        """Get package information from PyPI"""
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                info = data.get('info', {})
                releases = data.get('releases', {})
                
                # Get latest version
                latest_version = info.get('version')
                
                return {
                    'latest_version': latest_version,
                    'description': info.get('summary'),
                    'license': info.get('license'),
                    'homepage': info.get('home_page'),
                    'author': info.get('author'),
                    'author_email': info.get('author_email')
                }
        except:
            pass
        
        return None
    
    def _update_packages_database(self, packages: List[Package], package_manager: str):
        """Update packages in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for package in packages:
                    conn.execute("""
                        INSERT OR REPLACE INTO packages 
                        (name, version, installed_version, latest_version, license, 
                         description, homepage, dependencies, vulnerabilities, 
                         update_available, security_risk, last_checked, package_manager)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        package.name,
                        package.version,
                        package.installed_version,
                        package.latest_version,
                        package.license,
                        package.description,
                        package.homepage,
                        json.dumps(package.dependencies),
                        json.dumps([asdict(v) for v in package.vulnerabilities]),
                        package.update_available,
                        package.security_risk,
                        package.last_checked,
                        package_manager
                    ))
        except Exception as e:
            raise Exception(f"Error updating packages database: {str(e)}")
    
    def _record_scan_history(self, scan_type: str, package_manager: str, 
                            total_packages: int, vulnerable_packages: int, 
                            outdated_packages: int, scan_duration: float, 
                            scan_results: Dict):
        """Record scan history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO scan_history 
                    (scan_type, package_manager, total_packages, vulnerable_packages, 
                     outdated_packages, scan_duration, scan_results)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_type, package_manager, total_packages, vulnerable_packages,
                    outdated_packages, scan_duration, json.dumps(scan_results)
                ))
        except Exception as e:
            pass  # Log error but don't fail
    
    def update_package(self, package_name: str, version: str = None, 
                      package_manager: str = 'pip', project_path: str = None) -> Dict[str, Any]:
        """Update a specific package"""
        try:
            with self.lock:
                config = self.package_managers[package_manager]
                
                # Get current version
                current_version = self._get_package_current_version(package_name, package_manager, project_path)
                
                # Build install command
                if version:
                    package_spec = f"{package_name}=={version}"
                else:
                    package_spec = package_name
                
                cmd = config['install_cmd'].copy() + [package_spec]
                
                # Execute update
                cwd = project_path if project_path else None
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
                
                success = result.returncode == 0
                error_message = result.stderr if not success else None
                
                # Get new version
                new_version = None
                if success:
                    new_version = self._get_package_current_version(package_name, package_manager, project_path)
                
                # Record update history
                self._record_update_history(
                    package_name=package_name,
                    old_version=current_version,
                    new_version=new_version,
                    update_type="manual",
                    package_manager=package_manager,
                    success=success,
                    error_message=error_message
                )
                
                # Update package in database
                if success:
                    self._update_single_package(package_name, new_version, package_manager)
                
                return {
                    'status': 'success' if success else 'error',
                    'package': package_name,
                    'old_version': current_version,
                    'new_version': new_version,
                    'success': success,
                    'error_message': error_message
                }
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _get_package_current_version(self, package_name: str, package_manager: str, project_path: str = None) -> Optional[str]:
        """Get current version of a package"""
        try:
            packages = self._get_installed_packages(package_manager, project_path)
            for package in packages:
                if package.name == package_name:
                    return package.installed_version
            return None
        except:
            return None
    
    def _update_single_package(self, package_name: str, version: str, package_manager: str):
        """Update single package in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE packages 
                    SET installed_version = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ? AND package_manager = ?
                """, (version, package_name, package_manager))
        except:
            pass
    
    def _record_update_history(self, package_name: str, old_version: str, 
                              new_version: str, update_type: str, 
                              package_manager: str, success: bool, 
                              error_message: str = None):
        """Record package update history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO update_history 
                    (package_name, old_version, new_version, update_type, 
                     package_manager, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    package_name, old_version, new_version, update_type,
                    package_manager, success, error_message
                ))
        except:
            pass
    
    def create_update_policy(self, policy: UpdatePolicy) -> Dict[str, Any]:
        """Create an automated update policy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO update_policies 
                    (name, auto_update, update_schedule, allow_major_updates, 
                     allow_pre_release, exclude_packages, include_only, license_whitelist)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    policy.name,
                    policy.auto_update,
                    policy.update_schedule,
                    policy.allow_major_updates,
                    policy.allow_pre_release,
                    json.dumps(policy.exclude_packages),
                    json.dumps(policy.include_only),
                    json.dumps(policy.license_whitelist)
                ))
                
                return {'status': 'success', 'policy_id': conn.lastrowid}
                
        except sqlite3.IntegrityError:
            return {'status': 'error', 'message': 'Policy name already exists'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_update_policies(self) -> List[Dict]:
        """Get all update policies"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM update_policies ORDER BY created_at DESC
                """)
                
                policies = []
                for row in cursor.fetchall():
                    policy = {
                        'id': row[0],
                        'name': row[1],
                        'auto_update': bool(row[2]),
                        'update_schedule': row[3],
                        'allow_major_updates': bool(row[4]),
                        'allow_pre_release': bool(row[5]),
                        'exclude_packages': json.loads(row[6]) if row[6] else [],
                        'include_only': json.loads(row[7]) if row[7] else [],
                        'license_whitelist': json.loads(row[8]) if row[8] else [],
                        'created_at': row[9],
                        'updated_at': row[10]
                    }
                    policies.append(policy)
                
                return policies
                
        except Exception as e:
            return []
    
    def check_license_compliance(self, project_path: str = None, 
                                 package_manager: str = 'pip') -> Dict[str, Any]:
        """Check license compliance for all packages"""
        try:
            with self.lock:
                packages = self._get_installed_packages(package_manager, project_path)
                
                license_report = {
                    'total_packages': len(packages),
                    'licensed_packages': 0,
                    'unlicensed_packages': 0,
                    'permissive_licenses': 0,
                    'copyleft_licenses': 0,
                    'commercial_licenses': 0,
                    'uncategorized_licenses': 0,
                    'license_details': []
                }
                
                for package in packages:
                    # Update package info to get license
                    self._update_package_info(package)
                    
                    license_info = {
                        'name': package.name,
                        'version': package.version,
                        'license': package.license or 'Unknown',
                        'category': 'uncategorized'
                    }
                    
                    if package.license:
                        license_report['licensed_packages'] += 1
                        
                        # Categorize license
                        license_lower = package.license.lower()
                        categorized = False
                        
                        for category, licenses in self.license_categories.items():
                            for license_name in licenses:
                                if license_name.lower() in license_lower:
                                    license_info['category'] = category
                                    license_report[f'{category}_licenses'] += 1
                                    categorized = True
                                    break
                            if categorized:
                                break
                    else:
                        license_report['unlicensed_packages'] += 1
                    
                    license_report['license_details'].append(license_info)
                
                return {
                    'status': 'success',
                    'compliance_report': license_report
                }
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def generate_dependency_report(self, format_type: str = 'json') -> Dict[str, Any]:
        """Generate comprehensive dependency report"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get package statistics
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_packages,
                        COUNT(CASE WHEN update_available = 1 THEN 1 END) as outdated_packages,
                        COUNT(CASE WHEN security_risk = 1 THEN 1 END) as vulnerable_packages,
                        COUNT(CASE WHEN license IS NOT NULL THEN 1 END) as licensed_packages
                    FROM packages
                """)
                
                stats = cursor.fetchone()
                
                # Get recent scan history
                cursor = conn.execute("""
                    SELECT * FROM scan_history 
                    ORDER BY created_at DESC LIMIT 10
                """)
                
                recent_scans = []
                for row in cursor.fetchall():
                    recent_scans.append({
                        'id': row[0],
                        'scan_type': row[1],
                        'package_manager': row[2],
                        'total_packages': row[3],
                        'vulnerable_packages': row[4],
                        'outdated_packages': row[5],
                        'scan_duration': row[6],
                        'created_at': row[8]
                    })
                
                # Get vulnerable packages
                cursor = conn.execute("""
                    SELECT name, version, vulnerabilities FROM packages 
                    WHERE security_risk = 1
                """)
                
                vulnerable_packages = []
                for row in cursor.fetchall():
                    vulnerable_packages.append({
                        'name': row[0],
                        'version': row[1],
                        'vulnerabilities': json.loads(row[2]) if row[2] else []
                    })
                
                # Get update policies
                policies = self.get_update_policies()
                
                report = {
                    'generated_at': datetime.now().isoformat(),
                    'statistics': {
                        'total_packages': stats[0],
                        'outdated_packages': stats[1],
                        'vulnerable_packages': stats[2],
                        'licensed_packages': stats[3]
                    },
                    'recent_scans': recent_scans,
                    'vulnerable_packages': vulnerable_packages,
                    'update_policies': policies,
                    'recommendations': self._generate_recommendations(stats)
                }
                
                if format_type == 'json':
                    return {'status': 'success', 'report': report}
                else:
                    return {'status': 'success', 'report': str(report)}
                    
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _generate_recommendations(self, stats: Tuple) -> List[str]:
        """Generate recommendations based on statistics"""
        recommendations = []
        
        total_packages, outdated_packages, vulnerable_packages, licensed_packages = stats
        
        if vulnerable_packages > 0:
            recommendations.append(f"Immediate action required: {vulnerable_packages} packages have security vulnerabilities")
        
        if outdated_packages > total_packages * 0.3:
            recommendations.append("Consider updating outdated packages to maintain security and compatibility")
        
        if licensed_packages < total_packages * 0.8:
            recommendations.append("Many packages lack proper license information - review for compliance")
        
        if total_packages > 100:
            recommendations.append("Large dependency tree detected - consider dependency optimization")
        
        if not recommendations:
            recommendations.append("Dependency management appears to be in good health")
        
        return recommendations
    
    def get_package_details(self, package_name: str, package_manager: str = 'pip') -> Dict[str, Any]:
        """Get detailed information about a specific package"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM packages 
                    WHERE name = ? AND package_manager = ?
                """, (package_name, package_manager))
                
                row = cursor.fetchone()
                if not row:
                    return {'status': 'error', 'message': 'Package not found'}
                
                package = {
                    'id': row[0],
                    'name': row[1],
                    'version': row[2],
                    'installed_version': row[3],
                    'latest_version': row[4],
                    'license': row[5],
                    'description': row[6],
                    'homepage': row[7],
                    'dependencies': json.loads(row[8]) if row[8] else [],
                    'vulnerabilities': json.loads(row[9]) if row[9] else [],
                    'update_available': bool(row[10]),
                    'security_risk': bool(row[11]),
                    'last_checked': row[12],
                    'package_manager': row[13],
                    'created_at': row[14],
                    'updated_at': row[15]
                }
                
                # Get update history for this package
                cursor = conn.execute("""
                    SELECT * FROM update_history 
                    WHERE package_name = ? 
                    ORDER BY created_at DESC LIMIT 10
                """, (package_name,))
                
                update_history = []
                for row in cursor.fetchall():
                    update_history.append({
                        'id': row[0],
                        'package_name': row[1],
                        'old_version': row[2],
                        'new_version': row[3],
                        'update_type': row[4],
                        'package_manager': row[5],
                        'success': bool(row[6]),
                        'error_message': row[7],
                        'created_at': row[8]
                    })
                
                package['update_history'] = update_history
                
                return {'status': 'success', 'package': package}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def cleanup_database(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old scan history and update records"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_date = datetime.now() - timedelta(days=days_old)
                
                # Clean old scan history
                cursor = conn.execute("""
                    DELETE FROM scan_history 
                    WHERE created_at < ?
                """, (cutoff_date.isoformat(),))
                
                scan_history_deleted = cursor.rowcount
                
                # Clean old update history
                cursor = conn.execute("""
                    DELETE FROM update_history 
                    WHERE created_at < ?
                """, (cutoff_date.isoformat(),))
                
                update_history_deleted = cursor.rowcount
                
                return {
                    'status': 'success',
                    'scan_history_deleted': scan_history_deleted,
                    'update_history_deleted': update_history_deleted,
                    'cutoff_date': cutoff_date.isoformat()
                }
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get dependency manager status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get package counts
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_packages,
                        COUNT(CASE WHEN update_available = 1 THEN 1 END) as outdated,
                        COUNT(CASE WHEN security_risk = 1 THEN 1 END) as vulnerable,
                        COUNT(DISTINCT package_manager) as managers_used
                    FROM packages
                """)
                
                package_stats = cursor.fetchone()
                
                # Get scan statistics
                cursor = conn.execute("""
                    SELECT COUNT(*) as total_scans,
                           AVG(scan_duration) as avg_duration
                    FROM scan_history
                """)
                
                scan_stats = cursor.fetchone()
                
                # Get policy count
                cursor = conn.execute("SELECT COUNT(*) FROM update_policies")
                policy_count = cursor.fetchone()[0]
                
                return {
                    'status': 'active',
                    'packages': {
                        'total': package_stats[0],
                        'outdated': package_stats[1],
                        'vulnerable': package_stats[2],
                        'managers_used': package_stats[3]
                    },
                    'scans': {
                        'total': scan_stats[0] or 0,
                        'avg_duration': round(scan_stats[1] or 0, 2)
                    },
                    'policies': policy_count,
                    'supported_managers': list(self.package_managers.keys())
                }
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

# CLI interface
if __name__ == "__main__":
    manager = DependencyManager()
    
    if len(sys.argv) < 2:
        logger.info("Dependency Manager Tool")
        logger.info("Usage: python dependency_manager.py <command> [options]")
        logger.info("/nCommands:")
        logger.info("  scan [manager] [path]     - Scan dependencies")
        logger.info("  update <package> [version] - Update package")
        logger.info("  license-check [path]      - Check license compliance")
        logger.info("  report                    - Generate dependency report")
        logger.info("  policies                  - List update policies")
        logger.info("  package <name>            - Get package details")
        logger.info("  status                    - Get manager status")
        logger.info("  cleanup [days]            - Clean up old records")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "scan":
        manager_type = sys.argv[2] if len(sys.argv) > 2 else 'pip'
        project_path = sys.argv[3] if len(sys.argv) > 3 else None
        result = manager.scan_dependencies(manager_type, project_path)
        logger.info(json.dumps(result, indent=2))
    
    elif command == "update":
        package_name = sys.argv[2]
        version = sys.argv[3] if len(sys.argv) > 3 else None
        result = manager.update_package(package_name, version)
        logger.info(json.dumps(result, indent=2))
    
    elif command == "license-check":
        project_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = manager.check_license_compliance(project_path)
        logger.info(json.dumps(result, indent=2))
    
    elif command == "report":
        result = manager.generate_dependency_report()
        logger.info(json.dumps(result, indent=2))
    
    elif command == "policies":
        policies = manager.get_update_policies()
        logger.info(json.dumps({'status': 'success', 'policies': policies}, indent=2))
    
    elif command == "package":
        package_name = sys.argv[2]
        result = manager.get_package_details(package_name)
        logger.info(json.dumps(result, indent=2))
    
    elif command == "status":
        status = manager.get_status()
        logger.info(json.dumps(status, indent=2))
    
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        result = manager.cleanup_database(days)
        logger.info(json.dumps(result, indent=2))
    
    else:
        logger.info(f"Unknown command: {command}")
        sys.exit(1)