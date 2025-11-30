#!/usr/bin/env python3
"""
AgentDaf1.1 Development Toolkit
Modern development tools for project restructuring and maintenance
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import shutil

@dataclass
class ProjectMetrics:
    """Project metrics for analysis"""
    total_files: int = 0
    python_files: int = 0
    js_files: int = 0
    test_files: int = 0
    docker_files: int = 0
    config_files: int = 0
    lines_of_code: int = 0
    test_coverage: float = 0.0
    dependencies: int = 0
    security_issues: int = 0

class DevToolkit:
    """Modern development toolkit for AgentDaf1.1"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or str(Path.cwd()))
        self.metrics = ProjectMetrics()
        
    def analyze_project(self) -> Dict[str, Any]:
        """Comprehensive project analysis"""
        logger.info("Analyzing project structure...")
        
        analysis = {
            "project_root": str(self.project_root),
            "timestamp": datetime.now().isoformat(),
            "metrics": asdict(self._calculate_metrics()),
            "structure": self._analyze_structure(),
            "dependencies": self._analyze_dependencies(),
            "security": self._analyze_security(),
            "recommendations": self._generate_recommendations()
        }
        
        return analysis
    
    def _calculate_metrics(self) -> ProjectMetrics:
        """Calculate project metrics"""
        metrics = ProjectMetrics()
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                metrics.total_files += 1
                
                # Count file types
                if file_path.suffix == '.py':
                    metrics.python_files += 1
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            metrics.lines_of_code += len(f.readlines())
                    except:
                        pass
                elif file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                    metrics.js_files += 1
                elif 'test' in file_path.name.lower():
                    metrics.test_files += 1
                elif file_path.name in ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
                    metrics.docker_files += 1
                elif file_path.suffix in ['.json', '.yaml', '.yml', '.toml', '.ini']:
                    metrics.config_files += 1
        
        # Count dependencies
        req_files = list(self.project_root.rglob("requirements*.txt"))
        package_json = list(self.project_root.rglob("package.json"))
        metrics.dependencies = len(req_files) + len(package_json)
        
        return metrics
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze project structure"""
        structure = {
            "directories": [],
            "key_files": [],
            "issues": []
        }
        
        # Analyze directories
        for item in self.project_root.iterdir():
            if item.is_dir():
                structure["directories"].append({
                    "name": item.name,
                    "files": len(list(item.rglob("*"))),
                    "type": self._classify_directory(item.name)
                })
            elif item.is_file() and item.name in [
                "README.md", "package.json", "requirements.txt", 
                "Dockerfile", "docker-compose.yml", ".gitignore"
            ]:
                structure["key_files"].append(item.name)
        
        # Check for modern structure
        if not (self.project_root / "src").exists():
            structure["issues"].append("Missing src/ directory")
        if not (self.project_root / "tests").exists():
            structure["issues"].append("Missing tests/ directory")
        if not (self.project_root / ".github").exists():
            structure["issues"].append("Missing .github/ for CI/CD")
        
        return structure
    
    def _classify_directory(self, dir_name: str) -> str:
        """Classify directory type"""
        modern_patterns = {
            "src": "source",
            "tests": "testing", 
            "docs": "documentation",
            "scripts": "automation",
            "config": "configuration",
            "infrastructure": "devops",
            "frontend": "ui",
            "backend": "api",
            "services": "microservices",
            "shared": "common",
            "enterprise": "production"
        }
        return modern_patterns.get(dir_name, "other")
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        deps = {
            "python": [],
            "javascript": [],
            "outdated": [],
            "security_issues": []
        }
        
        # Python dependencies
        for req_file in self.project_root.rglob("requirements*.txt"):
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            deps["python"].append(line)
            except:
                pass
        
        # JavaScript dependencies
        for package_file in self.project_root.rglob("package.json"):
            try:
                with open(package_file, 'r') as f:
                    package_data = json.load(f)
                    deps["javascript"].extend(package_data.get("dependencies", {}).keys())
                    deps["javascript"].extend(package_data.get("devDependencies", {}).keys())
            except:
                pass
        
        return deps
    
    def _analyze_security(self) -> Dict[str, Any]:
        """Analyze security aspects"""
        security = {
            "issues": [],
            "recommendations": [],
            "score": 0
        }
        
        # Check for security files
        security_files = [
            ".env.example", ".env", "secrets.txt",
            "docker-compose.override.yml"
        ]
        
        for sec_file in security_files:
            if (self.project_root / sec_file).exists():
                security["issues"].append(f"Potential security file: {sec_file}")
        
        # Check for hardcoded secrets
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if any(keyword in content.lower() for keyword in 
                          ['password', 'secret', 'token', 'api_key']):
                        security["issues"].append(f"Potential hardcoded secrets in {py_file}")
            except:
                pass
        
        # Calculate security score
        security["score"] = max(0, 100 - len(security["issues"]) * 10)
        
        return security
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if self.metrics.test_files < self.metrics.python_files * 0.5:
            recommendations.append("Increase test coverage - add more unit tests")
        
        if not (self.project_root / ".github" / "workflows").exists():
            recommendations.append("Set up CI/CD pipeline with GitHub Actions")
        
        if not any(self.project_root.rglob("tsconfig.json")):
            recommendations.append("Migrate JavaScript to TypeScript for type safety")
        
        if not any(self.project_root.rglob("Dockerfile")):
            recommendations.append("Add Docker containerization")
        
        if not any(self.project_root.rglob("pyproject.toml")):
            recommendations.append("Modernize Python packaging with pyproject.toml")
        
        return recommendations
    
    def create_modern_structure(self) -> bool:
        """Create modern project structure"""
        logger.info("Creating modern project structure...")
        
        modern_dirs = [
            "services/api-gateway",
            "services/auth-service", 
            "services/file-service",
            "services/excel-service",
            "services/analytics-service",
            "services/notification-service",
            "frontend/src/components",
            "frontend/src/pages", 
            "frontend/src/hooks",
            "frontend/src/stores",
            "frontend/src/services",
            "frontend/src/types",
            "frontend/src/utils",
            "frontend/public",
            "frontend/tests",
            "shared/types",
            "shared/schemas", 
            "shared/utils",
            "shared/events",
            "infrastructure/docker",
            "infrastructure/kubernetes",
            "infrastructure/terraform",
            "infrastructure/monitoring",
            "tests/integration",
            "tests/e2e",
            "tests/performance",
            "docs/api",
            "docs/architecture",
            "docs/deployment",
            "scripts",
            ".github/workflows"
        ]
        
        try:
            for dir_path in modern_dirs:
                full_path = self.project_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                
                # Create __init__.py for Python directories
                if any(part in dir_path for part in ["services", "shared"]):
                    (full_path / "__init__.py").touch()
            
            logger.info("Modern structure created successfully")
            return True
            
        except Exception as e:
            logger.info(f"Error creating structure: {e}")
            return False
    
    def setup_typescript(self) -> bool:
        """Set up TypeScript configuration"""
        logger.info("Setting up TypeScript...")
        
        tsconfig = {
            "compilerOptions": {
                "target": "ES2022",
                "lib": ["DOM", "DOM.Iterable", "ES6"],
                "allowJs": True,
                "skipLibCheck": True,
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "forceConsistentCasingInFileNames": True,
                "noFallthroughCasesInSwitch": True,
                "module": "ESNext",
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "baseUrl": ".",
                "paths": {
                    "@/*": ["frontend/src/*"],
                    "@/components/*": ["frontend/src/components/*"],
                    "@/pages/*": ["frontend/src/pages/*"],
                    "@/hooks/*": ["frontend/src/hooks/*"],
                    "@/stores/*": ["frontend/src/stores/*"],
                    "@/services/*": ["frontend/src/services/*"],
                    "@/types/*": ["frontend/src/types/*"],
                    "@/utils/*": ["frontend/src/utils/*"],
                    "@/shared/*": ["shared/*"]
                }
            },
            "include": [
                "frontend/src/**/*",
                "shared/**/*"
            ],
            "exclude": [
                "node_modules",
                "dist",
                "build"
            ]
        }
        
        try:
            with open(self.project_root / "tsconfig.json", 'w') as f:
                json.dump(tsconfig, f, indent=2)
            
            logger.info("TypeScript configuration created")
            return True
            
        except Exception as e:
            logger.info(f"Error setting up TypeScript: {e}")
            return False
    
    def create_ci_cd(self) -> bool:
        """Create CI/CD pipeline"""
        logger.info("Creating CI/CD pipeline...")
        
        workflow = {
            "name": "AgentDaf1.1 CI/CD",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]}
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "strategy": {
                        "matrix": {
                            "python-version": ["3.11", "3.12"]
                        }
                    },
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "${{ matrix.python-version }}"}
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt && pip install pytest pytest-cov black flake8 mypy"
                        },
                        {"name": "Lint with flake8", "run": "flake8 src/"},
                        {"name": "Type check with mypy", "run": "mypy src/"},
                        {"name": "Test with pytest", "run": "pytest --cov=src tests/"},
                        {"name": "Upload coverage", "uses": "codecov/codecov-action@v3"}
                    ]
                },
                "frontend": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Setup Node.js",
                            "uses": "actions/setup-node@v4",
                            "with": {"node-version": "20", "cache": "npm"}
                        },
                        {"name": "Install dependencies", "run": "cd frontend && npm ci"},
                        {"name": "Type check", "run": "cd frontend && npm run type-check"},
                        {"name": "Lint", "run": "cd frontend && npm run lint"},
                        {"name": "Test", "run": "cd frontend && npm test"},
                        {"name": "Build", "run": "cd frontend && npm run build"}
                    ]
                },
                "security": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Run Trivy vulnerability scanner",
                            "uses": "aquasecurity/trivy-action@master",
                            "with": {"scan-type": "fs", "scan-ref": "."}
                        }
                    ]
                }
            }
        }
        
        try:
            workflows_dir = self.project_root / ".github" / "workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            with open(workflows_dir / "ci.yml", 'w') as f:
                json.dump(workflow, f, indent=2)
            
            logger.info("CI/CD pipeline created")
            return True
            
        except Exception as e:
            logger.info(f"Error creating CI/CD: {e}")
            return False
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate analysis report"""
        report = f"""
# AgentDaf1.1 Project Analysis Report

Generated: {analysis['timestamp']}

## Project Metrics
- Total Files: {analysis['metrics']['total_files']}
- Python Files: {analysis['metrics']['python_files']}
- JavaScript/TypeScript Files: {analysis['metrics']['js_files']}
- Test Files: {analysis['metrics']['test_files']}
- Lines of Code: {analysis['metrics']['lines_of_code']}
- Dependencies: {analysis['metrics']['dependencies']}

## Structure Analysis
- Directories: {len(analysis['structure']['directories'])}
- Key Files: {len(analysis['structure']['key_files'])}
- Issues: {len(analysis['structure']['issues'])}

## Security Score: {analysis['security']['score']}/100
- Security Issues: {len(analysis['security']['issues'])}

## 💡 Recommendations
{chr(10).join(f"- {rec}" for rec in analysis['recommendations'])}

## 🚀 Next Steps
1. Run `python dev_toolkit.py --create-structure` to create modern structure
2. Run `python dev_toolkit.py --setup-typescript` for TypeScript setup
3. Run `python dev_toolkit.py --create-cicd` for CI/CD pipeline
4. Review and implement security recommendations
"""
        return report
    
    def fix_imports(self) -> bool:
        """Fix Python import issues"""
        logger.info("Fixing Python imports...")
        
        fixed_files = 0
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix common import issues
                original_content = content
                
                # Add src to path if needed
                if 'from src.' in content and 'sys.path' not in content:
                    lines = content.split('/n')
                    import_index = 0
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            import_index = i
                            break
                    
                    lines.insert(import_index, "import sys")
                    lines.insert(import_index + 1, "from pathlib import Path")
                    lines.insert(import_index + 2, "sys.path.insert(0, str(Path(__file__).parent.parent))")
                    lines.insert(import_index + 3, "")
                    
                    content = '/n'.join(lines)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_files += 1
                    
            except Exception as e:
                logger.info(f"Error fixing {py_file}: {e}")
        
        logger.info(f"Fixed imports in {fixed_files} files")
        return True

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="AgentDaf1.1 Development Toolkit")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--analyze", action="store_true", help="Analyze project")
    parser.add_argument("--create-structure", action="store_true", help="Create modern structure")
    parser.add_argument("--setup-typescript", action="store_true", help="Setup TypeScript")
    parser.add_argument("--create-cicd", action="store_true", help="Create CI/CD pipeline")
    parser.add_argument("--fix-imports", action="store_true", help="Fix Python imports")
    parser.add_argument("--report", help="Generate analysis report file")
    
    args = parser.parse_args()
    
    toolkit = DevToolkit(args.project_root)
    
    if args.analyze or not any([args.create_structure, args.setup_typescript, args.create_cicd, args.fix_imports]):
        analysis = toolkit.analyze_project()
        logger.info(json.dumps(analysis, indent=2))
        
        if args.report:
            report = toolkit.generate_report(analysis)
            with open(args.report, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to {args.report}")
    
    if args.create_structure:
        toolkit.create_modern_structure()
    
    if args.setup_typescript:
        toolkit.setup_typescript()
    
    if args.create_cicd:
        toolkit.create_ci_cd()
    
    if args.fix_imports:
        toolkit.fix_imports()

if __name__ == "__main__":
    main()