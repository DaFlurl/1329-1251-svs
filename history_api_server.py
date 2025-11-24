#!/usr/bin/env python3
"""
History API Server for AgentDaf1 Scoreboard
Provides REST API endpoints for file history and version management
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path
import zipfile
import tempfile

from file_history_manager import FileHistoryManager

app = Flask(__name__)
CORS(app)

# Initialize history manager
history_manager = FileHistoryManager()

@app.route('/api/history/files', methods=['GET'])
def get_files_history():
    """Get history of all files with their versions"""
    try:
        history = history_manager.load_history()
        files_summary = {}
        
        for file_path, file_entry in history["files"].items():
            files_summary[file_path] = {
                "created": file_entry["created"],
                "current_version": file_entry["current_version"],
                "total_changes": len(file_entry["changes"]),
                "last_modified": file_entry["last_modified"],
                "versions": []
            }
            
            # Add version details
            for change in file_entry["changes"]:
                files_summary[file_path]["versions"].append({
                    "version": change["version"],
                    "timestamp": change["timestamp"],
                    "type": change["type"],
                    "description": change["description"],
                    "author": change["author"],
                    "has_backup": change.get("backup") is not None
                })
        
        return jsonify({
            "success": True,
            "data": files_summary,
            "total_files": len(files_summary)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/files/<path:filename>', methods=['GET'])
def get_file_history(filename):
    """Get detailed history for a specific file"""
    try:
        file_path = history_manager.base_dir / filename
        file_history = history_manager.get_file_history(file_path)
        
        if not file_history:
            return jsonify({"success": False, "error": "File not found in history"}), 404
        
        return jsonify({
            "success": True,
            "data": file_history
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/restore', methods=['POST'])
def restore_file():
    """Restore a file to a specific version"""
    try:
        data = request.json
        filename = data.get('filename')
        version = data.get('version')
        
        if not filename:
            return jsonify({"success": False, "error": "Filename is required"}), 400
        
        file_path = history_manager.base_dir / filename
        success = history_manager.restore_file(file_path, version=version)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"File {filename} restored to version {version}"
            })
        else:
            return jsonify({"success": False, "error": "Restore failed"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/download/<path:filename>/<version>', methods=['GET'])
def download_version(filename, version):
    """Download a specific version of a file"""
    try:
        file_path = history_manager.base_dir / filename
        file_history = history_manager.get_file_history(file_path)
        
        # Find the specific version
        target_backup = None
        for change in file_history.get("changes", []):
            if str(change["version"]) == version and change.get("backup"):
                target_backup = change["backup"]
                break
        
        if not target_backup:
            return jsonify({"success": False, "error": "Version not found"}), 404
        
        backup_path = Path(target_backup["backup_path"])
        if backup_path.exists():
            return send_file(backup_path, as_attachment=True)
        else:
            return jsonify({"success": False, "error": "Backup file not found"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/compare', methods=['POST'])
def compare_versions():
    """Compare two versions of a file"""
    try:
        data = request.json
        filename = data.get('filename')
        version1 = data.get('version1')
        version2 = data.get('version2')
        
        if not all([filename, version1, version2]):
            return jsonify({"success": False, "error": "Missing required parameters"}), 400
        
        file_path = history_manager.base_dir / filename
        file_history = history_manager.get_file_history(file_path)
        
        # Find both versions
        versions = {}
        for change in file_history.get("changes", []):
            version_str = str(change["version"])
            if version_str in [version1, version2] and change.get("backup"):
                versions[version_str] = change
        
        if len(versions) < 2:
            return jsonify({"success": False, "error": "One or both versions not found"}), 404
        
        # Read file contents
        comparison = {}
        for ver, change in versions.items():
            backup_path = Path(change["backup"]["backup_path"])
            if backup_path.exists():
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        comparison[ver] = {
                            "content": f.read(),
                            "timestamp": change["timestamp"],
                            "description": change["description"]
                        }
                except Exception as e:
                    comparison[ver] = {"error": str(e)}
        
        return jsonify({
            "success": True,
            "data": {
                "filename": filename,
                "comparison": comparison
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/export', methods=['GET'])
def export_history():
    """Export complete history as JSON"""
    try:
        report = history_manager.generate_report()
        if report:
            return jsonify({
                "success": True,
                "data": report
            })
        else:
            return jsonify({"success": False, "error": "Failed to generate report"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/backup/download', methods=['GET'])
def download_all_backups():
    """Download all backup files as a ZIP archive"""
    try:
        # Create temporary ZIP file
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"scoreboard_backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for backup_file in history_manager.backups_dir.rglob("*"):
                if backup_file.is_file():
                    # Add file to ZIP with relative path
                    arcname = backup_file.relative_to(history_manager.backups_dir)
                    zipf.write(backup_file, arcname)
            
            # Also include the history JSON
            history_json_path = history_manager.history_file
            if history_json_path.exists():
                zipf.write(history_json_path, "file_history.json")
        
        return send_file(zip_path, as_attachment=True, download_name="scoreboard_backups.zip")
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/cleanup', methods=['POST'])
def cleanup_old_backups():
    """Clean up old backup files"""
    try:
        data = request.json
        keep_days = data.get('keep_days', 30)
        
        removed_count = history_manager.cleanup_old_backups(keep_days)
        
        return jsonify({
            "success": True,
            "message": f"Cleaned up {removed_count} old backup files",
            "removed_count": removed_count
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/stats', methods=['GET'])
def get_history_stats():
    """Get history statistics"""
    try:
        report = history_manager.generate_report()
        if report:
            return jsonify({
                "success": True,
                "data": {
                    "total_files": report["summary"]["total_files"],
                    "total_changes": report["summary"]["total_changes"],
                    "history_size_mb": report["summary"]["history_size_mb"],
                    "last_updated": report["generated_at"]
                }
            })
        else:
            return jsonify({"success": False, "error": "Failed to generate stats"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting History API Server...")
    print("📊 Available endpoints:")
    print("  GET  /api/history/files - Get all files history")
    print("  GET  /api/history/files/<filename> - Get specific file history")
    print("  POST /api/history/restore - Restore file version")
    print("  GET  /api/history/download/<filename>/<version> - Download version")
    print("  POST /api/history/compare - Compare two versions")
    print("  GET  /api/history/export - Export complete history")
    print("  GET  /api/history/backup/download - Download all backups")
    print("  POST /api/history/cleanup - Clean old backups")
    print("  GET  /api/history/stats - Get statistics")
    print(f"🌐 Server running on http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True)