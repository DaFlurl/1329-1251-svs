"""
Flask API Framework for AgentDaf1.1
REST API for Excel dashboard system
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS

# Import centralized configurations
from src.config.path_config import PROJECT_ROOT
from src.config.logging_config import get_logger

from src.api.github_integration import GitHubIntegration
from src.config.settings import Config
from src.core.dashboard_generator import DashboardGenerator
from src.core.excel_processor import ExcelProcessor
from src.tools.file_manager import file_manager
from src.tools.memory_manager import memory_manager
from src.core.performance_monitor import PerformanceMonitor
from src.tools.security import security_monitor
from src.core.task_manager import TaskManager

logger = get_logger(__name__)


class FlaskAPI:
    """Main Flask API application"""

    def __init__(self):
        # Set template folder to web/templates
        template_folder = Path(__file__).parent.parent / "web" / "templates"
        self.app = Flask(__name__, template_folder=str(template_folder))
        self.app.config["SECRET_KEY"] = Config.SECRET_KEY
        self.app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

        # Enable CORS
        CORS(self.app)

        # Initialize components
        self.excel_processor = ExcelProcessor()
        self.dashboard_generator = DashboardGenerator()
        self.performance_monitor = PerformanceMonitor()
        self.task_manager = TaskManager()

        # Initialize GitHub integration
        github_config = {
            "GITHUB_TOKEN": getattr(Config, "GITHUB_TOKEN", None),
            "GITHUB_REPO_OWNER": getattr(Config, "GITHUB_REPO_OWNER", None),
            "GITHUB_REPO_NAME": getattr(Config, "GITHUB_REPO_NAME", None),
        }
        self.github_integration = GitHubIntegration(github_config)

        # Setup routes
        self._setup_routes()

        # Setup error handlers
        self._setup_error_handlers()

    def _setup_routes(self):
        """Setup all API routes"""

        @self.app.route("/")
        def index():
            """Main dashboard page"""
            return render_template("index.html")

        @self.app.route("/api/upload", methods=["POST"])
        def upload_file():
            """Upload and process Excel file"""
            try:
                if "file" not in request.files:
                    return jsonify({"error": "No file provided"}), 400

                file = request.files["file"]
                if file.filename == "":
                    return jsonify({"error": "No file selected"}), 400

                if not self._allowed_file(file.filename or ""):
                    return jsonify({"error": "File type not allowed"}), 400

                # Save uploaded file
                filename = self._save_uploaded_file(file)
                if not filename:
                    return jsonify({"error": "Failed to save file"}), 500

                # Process Excel file
                data = self.excel_processor.process_excel_file(filename)
                validation = self.excel_processor.validate_data(data)

                if not validation["is_valid"]:
                    return (
                        jsonify(
                            {
                                "error": "Validation failed",
                                "details": validation["errors"],
                            }
                        ),
                        400,
                    )

                # Generate dashboard
                processed_data = {
                    "players": self.excel_processor.extract_player_data(data),
                    "summary": {
                        "total_players": len(
                            self.excel_processor.extract_player_data(data)
                        ),
                        "filename": file.filename,
                    },
                }
                dashboard_html = self.dashboard_generator.create_dashboard(
                    processed_data, title=f"Dashboard - {file.filename}"
                )

                # Save dashboard
                dashboard_path = os.path.join(
                    Config.UPLOAD_FOLDER,
                    f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                )
                self.dashboard_generator.save_dashboard(dashboard_html, dashboard_path)

                return jsonify(
                    {
                        "success": True,
                        "message": "File processed successfully",
                        "data": {
                            "filename": file.filename,
                            "dashboard_url": f"/dashboard/{os.path.basename(dashboard_path)}",
                            "summary": processed_data["summary"],
                            "validation": validation,
                        },
                    }
                )

            except Exception as e:
                logger.error(f"Upload error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/dashboard/<filename>")
        def serve_dashboard(filename):
            """Serve generated dashboard"""
            try:
                dashboard_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                if os.path.exists(dashboard_path):
                    return send_file(dashboard_path)
                return jsonify({"error": "Dashboard not found"}), 404
            except Exception as e:
                logger.error(f"Dashboard serve error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/dashboards")
        def list_dashboards():
            """List all generated dashboards"""
            try:
                dashboards = []
                upload_folder = Config.UPLOAD_FOLDER

                if os.path.exists(upload_folder):
                    for file in os.listdir(upload_folder):
                        if file.endswith(".html") and file.startswith("dashboard_"):
                            file_path = os.path.join(upload_folder, file)
                            stat = os.stat(file_path)
                            dashboards.append(
                                {
                                    "filename": file,
                                    "url": f"/dashboard/{file}",
                                    "created": datetime.fromtimestamp(
                                        stat.st_ctime
                                    ).isoformat(),
                                    "size": stat.st_size,
                                }
                            )

                dashboards.sort(key=lambda x: x["created"], reverse=True)
                return jsonify({"dashboards": dashboards})

            except Exception as e:
                logger.error(f"List dashboards error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/data/<filename>")
        def get_processed_data(filename):
            """Get processed data for a dashboard"""
            try:
                # Look for corresponding JSON data file
                json_filename = filename.replace(".html", ".json")
                json_path = os.path.join(Config.UPLOAD_FOLDER, json_filename)

                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return jsonify(data)

                return jsonify({"error": "Data not found"}), 404

            except Exception as e:
                logger.error(f"Get data error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/health")
        def health_check():
            """Health check endpoint"""
            return jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0",
                }
            )

        @self.app.route("/api/stats")
        def get_stats():
            """Get system statistics"""
            try:
                stats = {
                    "system": {
                        "uptime": "N/A",  # Would need proper uptime tracking
                        "version": "1.0.0",
                        "environment": Config.ENVIRONMENT,
                    },
                    "dashboards": {
                        "total": (
                            len(
                                [
                                    f
                                    for f in os.listdir(Config.UPLOAD_FOLDER)
                                    if f.endswith(".html")
                                ]
                            )
                            if os.path.exists(Config.UPLOAD_FOLDER)
                            else 0
                        ),
                        "last_generated": self.dashboard_generator.get_dashboard_info(),
                    },
                    "processor": {
                        "files_processed": getattr(
                            self.excel_processor, "files_processed", 0
                        ),
                        "last_processed": getattr(
                            self.excel_processor, "last_processed", None
                        ),
                    },
                }
                return jsonify(stats)

            except Exception as e:
                logger.error(f"Stats error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        # ===== TOOL API ENDPOINTS =====

        @self.app.route("/api/tools/memory/info")
        def get_memory_info():
            """Get current memory information"""
            try:
                info = memory_manager.get_memory_info()
                return jsonify({"success": True, "data": info})
            except Exception as e:
                logger.error(f"Memory info error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/memory/snapshot")
        def take_memory_snapshot():
            """Take memory snapshot"""
            try:
                snapshot = memory_manager.take_snapshot()
                return jsonify({"success": True, "data": snapshot.__dict__})
            except Exception as e:
                logger.error(f"Memory snapshot error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/memory/optimize", methods=["POST"])
        def optimize_memory():
            """Optimize memory usage"""
            try:
                result = memory_manager.optimize_memory()
                return jsonify({"success": True, "data": result})
            except Exception as e:
                logger.error(f"Memory optimization error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/tasks/status")
        def get_task_status():
            """Get task queue status"""
            try:
                status = self.task_manager.get_statistics()
                return jsonify({"success": True, "data": status})
            except Exception as e:
                logger.error(f"Task status error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/tasks/create", methods=["POST"])
        def create_task():
            """Create a new task"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400

                # Simple test task
                def test_task():
                    return {
                        "message": "Task completed successfully",
                        "timestamp": datetime.now().isoformat(),
                    }

                task_id = self.task_manager.add_task(
                    data.get("name", "API Task"),
                    test_task,
                    data.get("description", "Task created via API"),
                )

                return jsonify({"success": True, "data": {"task_id": task_id}})
            except Exception as e:
                logger.error(f"Task creation error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/performance/metrics")
        def get_performance_metrics():
            """Get current performance metrics"""
            try:
                metrics = self.performance_monitor.get_recent_metrics(hours=1)
                return jsonify(
                    {"success": True, "data": metrics.to_dict() if metrics else {}}
                )
            except Exception as e:
                logger.error(f"Performance metrics error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/performance/system")
        def get_system_info():
            """Get system information"""
            try:
                info = self.performance_monitor.get_system_info()
                return jsonify({"success": True, "data": info})
            except Exception as e:
                logger.error(f"System info error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/performance/alerts")
        def get_performance_alerts():
            """Get performance alerts"""
            try:
                hours = request.args.get("hours", 24, type=int)
                alerts = self.performance_monitor.get_active_alerts()
                # Convert datetime timestamps to ISO strings for JSON
                alerts_json = []
                for alert in alerts:
                    if hasattr(alert, "__dict__"):
                        a = alert.__dict__.copy()
                    else:
                        a = dict(alert)
                    if "timestamp" in a and isinstance(a["timestamp"], datetime):
                        a["timestamp"] = a["timestamp"].isoformat()
                    alerts_json.append(a)
                return jsonify({"success": True, "data": alerts_json})
            except Exception as e:
                logger.error(f"Performance alerts error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/files/list")
        def list_files():
            """List files in directory"""
            try:
                directory = request.args.get("directory", ".")
                recursive = request.args.get("recursive", "false").lower() == "true"

                files = file_manager.list_directory(directory, recursive=recursive)
                return jsonify({"success": True, "data": [f.__dict__ for f in files]})
            except Exception as e:
                logger.error(f"File list error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/files/info")
        def get_file_info():
            """Get file information"""
            try:
                file_path = request.args.get("path")
                if not file_path:
                    return jsonify({"error": "File path required"}), 400

                info = file_manager.get_file_info(file_path)
                if not info:
                    return jsonify({"error": "File not found"}), 404

                return jsonify({"success": True, "data": info.__dict__})
            except Exception as e:
                logger.error(f"File info error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/security/summary")
        def get_security_summary():
            """Get security summary"""
            try:
                summary = security_monitor.get_security_summary()
                return jsonify({"success": True, "data": summary})
            except Exception as e:
                logger.error(f"Security summary error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/security/events")
        def get_security_events():
            """Get security events"""
            try:
                hours = request.args.get("hours", 24, type=int)
                severity = request.args.get("severity")
                severity_param = severity or ""
                events = security_monitor.get_events(
                    hours=hours, severity=severity_param
                )
                return jsonify(
                    {"success": True, "data": [event.__dict__ for event in events]}
                )
            except Exception as e:
                logger.error(f"Security events error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/logger/stats")
        def get_logger_stats():
            """Get logger statistics"""
            try:
                logger_instance = get_logger("AgentDaf1.1")
                stats = logger_instance.get_log_stats()
                return jsonify({"success": True, "data": stats})
            except Exception as e:
                logger.error(f"Logger stats error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/api/tools/status")
        def get_tools_status():
            """Get overall tools status"""
            try:
                status = {
                    "memory_manager": "active",
                    "task_manager": "active",
                    "performance_monitor": "active",
                    "file_manager": "active",
                    "security_monitor": "active",
                    "logger": "active",
                    "timestamp": datetime.now().isoformat(),
                }
                return jsonify({"success": True, "data": status})
            except Exception as e:
                logger.error(f"Tools status error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        # ===== GITHUB API ENDPOINTS =====

        @self.app.route("/api/github/info")
        def get_github_info():
            """Get GitHub repository information"""
            try:
                result = self.github_integration.get_repository_info()
                return jsonify(result)
            except Exception as e:
                logger.error(f"GitHub info error: {str(e)}")
                return (
                    jsonify({"success": False, "error": "Internal server error"}),
                    500,
                )

        @self.app.route("/api/github/files")
        def get_github_files():
            """List files in GitHub repository"""
            try:
                path = request.args.get("path", "")
                result = self.github_integration.list_files(path)
                return jsonify(result)
            except Exception as e:
                logger.error(f"GitHub files error: {str(e)}")
                return (
                    jsonify({"success": False, "error": "Internal server error"}),
                    500,
                )

        @self.app.route("/api/github/update", methods=["POST"])
        def update_github_files():
            """Update files in GitHub repository"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"success": False, "error": "No data provided"}), 400

                result = self.github_integration.update_files(data)
                return jsonify(result)
            except Exception as e:
                logger.error(f"GitHub update error: {str(e)}")
                return (
                    jsonify({"success": False, "error": "Internal server error"}),
                    500,
                )

        @self.app.route("/api/github/webhooks")
        def get_github_webhooks():
            """Get GitHub webhook information"""
            try:
                result = self.github_integration.get_webhook_info()
                return jsonify(result)
            except Exception as e:
                logger.error(f"GitHub webhooks error: {str(e)}")
                return (
                    jsonify({"success": False, "error": "Internal server error"}),
                    500,
                )

        @self.app.route("/api/github/create-repo", methods=["POST"])
        def create_github_repo():
            """Create new GitHub repository"""
            try:
                data = request.get_json()
                if not data or "repo_name" not in data:
                    return (
                        jsonify(
                            {"success": False, "error": "Repository name required"}
                        ),
                        400,
                    )

                repo_name = data["repo_name"]
                description = data.get("description", "")
                private = data.get("private", False)

                result = self.github_integration.create_repository(
                    repo_name, description, private
                )
                return jsonify(result)
            except Exception as e:
                logger.error(f"GitHub create repo error: {str(e)}")
                return (
                    jsonify({"success": False, "error": "Internal server error"}),
                    500,
                )

    def _setup_error_handlers(self):
        """Setup error handlers"""

        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Resource not found"}), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            import traceback

            error_details = traceback.format_exc()
            logger.error(f"Internal server error: {str(error)}/n{error_details}")
            if self.app.debug:
                return (
                    jsonify(
                        {"error": "Internal server error", "details": error_details}
                    ),
                    500,
                )
            return jsonify({"error": "Internal server error"}), 500

        @self.app.errorhandler(413)
        def too_large(error):
            return jsonify({"error": "File too large"}), 413

    def _allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        if not filename:
            return False
        return "." in filename and filename.rsplit(".", 1)[1].lower() in {"xlsx", "xls"}

    def _save_uploaded_file(self, file) -> str:
        """Save uploaded file and return path"""
        try:
            filename = file.filename or "uploaded_file.xlsx"
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            file.save(file_path)
            return file_path
        except Exception as e:
            logger.error(f"Save file error: {str(e)}")
            return ""

    def run(self, host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
        """Run the Flask application"""
        logger.info(f"Starting Flask API on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


# Create application instance
def create_app():
    """Application factory"""
    api = FlaskAPI()
    return api.app


if __name__ == "__main__":
    app = FlaskAPI()
    app.run(debug=True)
