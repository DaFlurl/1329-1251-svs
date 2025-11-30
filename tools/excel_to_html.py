#!/usr/bin/env python3
"""
Excel to HTML Dashboard Converter
Processes Excel files and converts them to interactive HTML dashboards
"""

import os
import sys
from datetime import datetime

# Add pandas and openpyxl for Excel processing
try:
    import pandas as pd
    from openpyxl.utils.dataframe import dataframe_to_rows
except ImportError as e:
    logger.info(f"Error importing required libraries: {e}")
    logger.info("Please install: pip install pandas openpyxl")
    sys.exit(1)


def read_excel_file(filepath):
    """Read Excel file and return data as dictionary"""
    try:
        # Read Excel file
        df = pd.read_excel(filepath, engine="openpyxl")

        # Get file info
        file_info = {
            "filename": os.path.basename(filepath),
            "filepath": filepath,
            "file_size": os.path.getsize(filepath),
            "row_count": len(df),
            "columns": list(df.columns),
            "sheets": list(pd.ExcelFile(filepath).sheet_names),
            "created_at": datetime.now().isoformat(),
        }

        # Read data from each sheet
        sheet_data = {}
        for sheet_name in pd.ExcelFile(filepath).sheet_names:
            sheet_df = pd.read_excel(filepath, sheet_name=sheet_name, engine="openpyxl")
            sheet_data[sheet_name] = {
                "data": sheet_df.to_dict("records"),
                "columns": list(sheet_df.columns),
                "row_count": len(sheet_df),
            }

        return {"file_info": file_info, "sheets": sheet_data, "success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


def create_html_dashboard(data, output_path):
    """Create interactive HTML dashboard from Excel data"""

    if not data["success"]:
        return f"<html><body><h1>Error processing file</h1><p>{data.get('error', 'Unknown error')}</p></body></html>"

    file_info = data["file_info"]
    sheets = data["sheets"]

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Dashboard - {file_info['filename']}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .file-info {{ background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 6px; padding: 15px; margin-bottom: 20px; }}
        .sheet-tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .sheet-tab {{ padding: 10px 20px; background: white; border: 1px solid #e5e7eb; border-radius: 6px; cursor: pointer; transition: all 0.3s; }}
        .sheet-tab.active {{ background: #3b82f6; color: white; }}
        .sheet-content {{ display: none; }}
        .sheet-content.active {{ display: block; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .data-table th {{ background: #f3f4f6; padding: 12px; text-align: left; font-weight: bold; border-bottom: 2px solid #e5e7eb; }}
        .data-table td {{ padding: 12px; border-bottom: 1px solid #e5e7eb; }}
        .data-table tr:hover {{ background: #f9fafb; }}
        .chart-container {{ width: 100%; height: 400px; margin: 20px 0; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #1f2937; }}
        .stat-label {{ font-size: 14px; color: #6b7280; margin-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>📊 Excel Dashboard</h1>
            <p>File: <strong>{file_info['filename']}</strong></p>
        </div>
        
        <div class="file-info">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">File Size</div>
                    <div class="stat-value">{file_info['file_size']:,} bytes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Rows</div>
                    <div class="stat-value">{file_info['row_count']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Sheets</div>
                    <div class="stat-value">{len(sheets)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Created</div>
                    <div class="stat-value">{file_info['created_at']}</div>
                </div>
            </div>
        </div>
        
        <div class="sheet-tabs">
    """

    # Create sheet tabs
    for i, (sheet_name, sheet_data) in enumerate(sheets.items()):
        active_class = "active" if i == 0 else ""
        html_content += f"""
            <div class="sheet-tab {active_class}" onclick="showSheet('sheet-{i}')">
                <h3>📋 {sheet_name}</h3>
                <div class="stat-card">
                    <div class="stat-label">Rows</div>
                    <div class="stat-value">{sheet_data['row_count']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Columns</div>
                    <div class="stat-value">{len(sheet_data['columns'])}</div>
                </div>
            </div>
    """

    html_content += """
        </div>
        
        <div id="sheet-0" class="sheet-content active">
            <h3>📋 Data Preview - {list(sheets.keys())[0]}</h3>
            <div class="data-table">
                <table>
                    <thead>
                        <tr>
    """

    # Add table headers for first sheet
    if sheets:
        first_sheet = list(sheets.values())[0]
        columns = first_sheet["columns"]
        html_content += (
            "                            <th>"
            + "</th>/n                            ".join(columns)
            + "</tr>/n                    </thead>/n                    <tbody>/n"
        )

        # Add first 10 rows of data
        data_rows = first_sheet["data"][:10]
        for row in data_rows:
            html_content += "                        <tr>/n"
            for col in columns:
                value = str(row.get(col, ""))
                html_content += f"                            <td>{value[:50]}{'...' if len(value) > 50 else value}</td>/n"
            html_content += "                        </tr>/n"

    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <canvas id="dataChart"></canvas>
            </div>
        </div>
    """

    # Add remaining sheet content with actual data
    for i in range(1, len(sheets)):
        sheet_name = list(sheets.keys())[i]
        sheet_data = sheets[sheet_name]

        html_content += f"""
            <div id="sheet-{i}" class="sheet-content">
                <h3>📋 Data Preview - {sheet_name}</h3>
                <div class="data-table">
                    <table>
                        <thead>
                            <tr>"""

        # Add table headers
        columns = sheet_data["columns"]
        html_content += (
            "                                <th>"
            + "</th>/n                            ".join(columns)
            + "</tr>/n                    </thead>/n                    <tbody>/n"
        )

        # Add data rows (limit to first 20 for performance)
        data_rows = sheet_data["data"][:20]
        for row in data_rows:
            html_content += "                        <tr>/n"
            for col in columns:
                value = str(row.get(col, ""))
                html_content += f"                            <td>{value[:50]}{'...' if len(value) > 50 else value}</td>/n"
            html_content += "                        </tr>/n"

        html_content += """                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <canvas id="chart-{i}"></canvas>
            </div>
        </div>
        """

    html_content += """
    </div>
    
    <script>
        function showSheet(sheetId) {{
            // Hide all sheets
            document.querySelectorAll('.sheet-content').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.sheet-tab').forEach(el => el.classList.remove('active'));
            
            // Show selected sheet
            document.getElementById(sheetId).style.display = 'block';
            document.querySelector(`[onclick="showSheet('{{sheetId}}')"]`).classList.add('active');
        }}
        
        // Chart data
        const chartData = {
            labels: ['Column A', 'Column B', 'Column C', 'Column D', 'Column E'],
            datasets: [{{
                label: 'Sample Data',
                data: [65, 59, 80, 81, 56],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }}]
        }};
        
        // Create chart
        const ctx = document.getElementById('dataChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: chartData,
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: true,
                        text: 'Data Distribution'
                    }}
                }},
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

    # Write HTML file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True, f"Dashboard created: {output_path}"
    except Exception as e:
        return False, f"Error creating dashboard: {e}"


def main():
    if len(sys.argv) != 3:
        logger.info("Usage: python excel_to_html.py <excel_file> <output_html>")
        sys.exit(1)

    excel_file = sys.argv[1]
    output_html = sys.argv[2]

    if not os.path.exists(excel_file):
        logger.info(f"Error: Excel file '{excel_file}' not found")
        sys.exit(1)

    logger.info(f"Processing Excel file: {excel_file}")
    data = read_excel_file(excel_file)

    if data["success"]:
        logger.info(
            f"✅ Successfully read Excel file with {data['file_info']['row_count']} rows and {len(data['sheets'])} sheets"
        )

        # Create output directory if needed
        output_dir = os.path.dirname(output_html)
        os.makedirs(output_dir, exist_ok=True)

        success, message = create_html_dashboard(data, output_html)

        if success:
            logger.info(f"✅ {message}")

            # Update database with transaction handling
            try:
                import sqlite3

                conn = sqlite3.connect("data/agentdaf1.db")
                cursor = conn.cursor()

                # Start transaction
                cursor.execute("BEGIN TRANSACTION")

                try:
                    # Update file status
                    cursor.execute(
                        """
                        INSERT INTO excel_processing_logs (excel_file_id, operation, status, message, created_at)
                        VALUES (?, 'completed', 'Dashboard created successfully', CURRENT_TIMESTAMP)
                        """,
                        (1,),
                    )

                    # Commit transaction
                    conn.commit()
                    logger.info("✅ Database updated with transaction handling")

                except Exception as e:
                    # Rollback on error
                    conn.rollback()
                    logger.info(f"⚠️ Database transaction failed: {e}")

                finally:
                    conn.close()

            except Exception as e:
                logger.info(f"⚠️ Database update failed: {e}")
        else:
            logger.info(f"❌ {message}")
    else:
        logger.info(f"❌ Error reading Excel file: {data['error']}")


if __name__ == "__main__":
    main()
