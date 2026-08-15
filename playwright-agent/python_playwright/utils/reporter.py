import os
import time
from datetime import datetime

class Reporter:
    _tests = []
    _current_test = None
    _start_time = None

    @classmethod
    def start_report(cls):
        cls._tests = []
        cls._start_time = datetime.now()

    @classmethod
    def start_test_case(cls, name, description, category="Smoke", author="SURIYAA"):
        cls._current_test = {
            "name": name,
            "description": description,
            "category": category,
            "author": author,
            "start_time": datetime.now(),
            "status": "PASS",
            "steps": []
        }
        cls._tests.append(cls._current_test)

    @classmethod
    def report_step(cls, page, description, status, snap=True, raise_error=True):
        if not cls._current_test:
            # Automatic fallback to prevent crashing if no test case is explicitly started
            cls.start_test_case("Default Scenario", "Auto-created fallback test case")
            
        step_time = datetime.now().strftime("%H:%M:%S")
        status_upper = status.upper()
        
        screenshot_path = None
        if snap and status_upper != "INFO" and status_upper != "SKIPPED":
            if page:
                try:
                    utils_dir = os.path.dirname(os.path.abspath(__file__))
                    reports_dir = os.path.join(os.path.dirname(utils_dir), "reports")
                    os.makedirs(os.path.join(reports_dir, "images"), exist_ok=True)
                    
                    snap_id = int(time.time() * 1000)
                    filename = f"snap_{snap_id}.png"
                    abs_screenshot = os.path.join(reports_dir, "images", filename)
                    
                    page.screenshot(path=abs_screenshot)
                    screenshot_path = f"images/{filename}"
                except Exception as e:
                    print(f"[REPORTER ERROR] Failed to save screenshot: {e}")
                    
        cls._current_test["steps"].append({
            "time": step_time,
            "description": description,
            "status": status_upper,
            "screenshot": screenshot_path
        })
        
        # Cascade statuses (FAIL overrides WARNING, which overrides PASS)
        if status_upper == "FAIL":
            cls._current_test["status"] = "FAIL"
        elif status_upper == "WARNING" and cls._current_test["status"] == "PASS":
            cls._current_test["status"] = "WARNING"
            
        try:
            print(f"[{status_upper}] {description}")
        except UnicodeEncodeError:
            print(f"[{status_upper}] {description.encode('ascii', 'replace').decode('ascii')}")
        
        # Match Java's ExtentReports helper which raises RuntimeException on fail
        if status_upper == "FAIL" and raise_error:
            raise AssertionError(f"Step failed: {description}")

    @classmethod
    def end_result(cls):
        # Calculate metrics using deduplicated tests (latest execution per test)
        unique_tests = {}
        for t in cls._tests:
            unique_tests[t["name"]] = t
        deduplicated = list(unique_tests.values())

        # Make sure reports folder exists
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        reports_dir = os.path.join(os.path.dirname(utils_dir), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(reports_dir, f"extent_report_{timestamp}.html")

        end_time = datetime.now()
        duration = str(end_time - cls._start_time).split(".")[0]
        
        # Calculate dashboard numbers based on deduplicated scenarios
        total_tests = len(deduplicated)
        passed_tests = sum(1 for t in deduplicated if t["status"] in ["PASS", "WARNING"])
        failed_tests = sum(1 for t in deduplicated if t["status"] == "FAIL")
        warning_tests = sum(1 for t in deduplicated if t["status"] == "WARNING")
        
        # Calculate pass rate based on deduplicated scenarios
        pass_pct = int((passed_tests / total_tests) * 100) if total_tests > 0 else 0
        dash_offset = int(100 - pass_pct)

        # Build Sidebar menu list
        menu_items_html = ""
        for idx, t in enumerate(deduplicated):
            badge_color = "status-pass" if t["status"] == "PASS" else "status-fail" if t["status"] == "FAIL" else "status-warn"
            active_class = "active" if idx == 0 else ""
            menu_items_html += f"""
            <div id="test-menu-{idx}" class="test-menu-item {active_class}" onclick="showTest({idx})">
                <span class="status-badge {badge_color}">{t['status']}</span>
                <span class="test-menu-name">{t['name']}</span>
            </div>
            """

        # Build Test Details panels
        details_panels_html = ""
        for idx, t in enumerate(deduplicated):
            display_style = "block" if idx == 0 else "none"
            badge_color = "status-pass" if t["status"] == "PASS" else "status-fail" if t["status"] == "FAIL" else "status-warn"
            
            steps_rows_html = ""
            for step in t["steps"]:
                step_badge = "status-pass" if step["status"] == "PASS" else "status-fail" if step["status"] == "FAIL" else "status-warn" if step["status"] == "WARNING" else "status-info"
                screenshot_cell = ""
                if step["screenshot"]:
                    screenshot_cell = f"""
                    <img class="screenshot-thumbnail" src="{step['screenshot']}" onclick="openModal(this.src)" alt="Screenshot"/>
                    """
                steps_rows_html += f"""
                <tr>
                    <td><span class="status-badge {step_badge}">{step['status']}</span></td>
                    <td class="step-time">{step['time']}</td>
                    <td>{step['description']}</td>
                    <td style="text-align: center;">{screenshot_cell}</td>
                </tr>
                """
                
            details_panels_html += f"""
            <div id="test-detail-{idx}" class="test-detail" style="display: {display_style};">
                <div class="test-header">
                    <span class="status-badge {badge_color}" style="font-size: 14px; padding: 6px 12px;">{t['status']}</span>
                    <h2 class="test-title">{t['name']}</h2>
                </div>
                <div class="test-meta-grid">
                    <div class="meta-item"><strong>Description:</strong> {t['description']}</div>
                    <div class="meta-item"><strong>Author:</strong> {t['author']}</div>
                    <div class="meta-item"><strong>Category:</strong> {t['category']}</div>
                    <div class="meta-item"><strong>Started:</strong> {t['start_time'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                
                <h3 style="margin-top: 24px; color: #475569;">Step Details</h3>
                <table class="steps-table">
                    <thead>
                        <tr>
                            <th style="width: 10%;">Status</th>
                            <th style="width: 12%;">Time</th>
                            <th>Step Description</th>
                            <th style="width: 18%;">Screenshot</th>
                        </tr>
                    </thead>
                    <tbody>
                        {steps_rows_html}
                    </tbody>
                </table>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Momentec Extent Reports</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }}
        body {{
            background-color: #f1f5f9;
            color: #1e293b;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}
        /* Left Sidebar navigation */
        .sidebar {{
            width: 320px;
            background-color: #0f172a;
            color: #e2e8f0;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #1e293b;
            height: 100%;
        }}
        .sidebar-header {{
            padding: 20px;
            background-color: #1e293b;
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #ef4444;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .menu-list {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }}
        .test-menu-item {{
            display: flex;
            align-items: center;
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            background-color: #1e293b;
        }}
        .test-menu-item:hover {{
            background-color: #334155;
        }}
        .test-menu-item.active {{
            background-color: #3b82f6;
            color: white;
        }}
        .test-menu-name {{
            font-size: 14px;
            font-weight: 500;
            margin-left: 12px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        /* Status Badges */
        .status-badge {{
            display: inline-block;
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            text-align: center;
            color: white;
            text-transform: uppercase;
        }}
        .status-pass {{ background-color: #10b981; }}
        .status-fail {{ background-color: #ef4444; }}
        .status-warn {{ background-color: #f59e0b; }}
        .status-info {{ background-color: #3b82f6; }}
        
        /* Main Panel */
        .main-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
        }}
        .dashboard {{
            padding: 24px;
            background-color: white;
            border-bottom: 1px solid #e2e8f0;
            display: grid;
            grid-template-columns: repeat(4, 1fr) auto;
            gap: 20px;
            align-items: center;
        }}
        .dash-card {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            flex-direction: column;
        }}
        .dash-card-title {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 6px;
        }}
        .dash-card-value {{
            font-size: 24px;
            font-weight: 700;
            color: #0f172a;
        }}
        .dash-chart-container {{
            width: 100px;
            height: 100px;
            position: relative;
            margin-left: 20px;
        }}
        
        /* Details Area */
        .details-area {{
            flex: 1;
            padding: 24px;
            overflow-y: auto;
        }}
        .test-detail {{
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
        }}
        .test-header {{
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 16px;
        }}
        .test-title {{
            font-size: 20px;
            font-weight: 700;
            color: #0f172a;
            margin-left: 16px;
        }}
        .test-meta-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px 24px;
            background-color: #f8fafc;
            padding: 16px;
            border-radius: 8px;
            font-size: 13px;
            margin-bottom: 24px;
            border: 1px solid #f1f5f9;
        }}
        
        /* Steps Table */
        .steps-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            border: 1px solid #e2e8f0;
        }}
        .steps-table th, .steps-table td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }}
        .steps-table th {{
            background-color: #f8fafc;
            font-weight: 600;
            color: #475569;
        }}
        .step-time {{
            color: #64748b;
            font-size: 12px;
        }}
        .screenshot-thumbnail {{
            max-width: 120px;
            border-radius: 4px;
            cursor: pointer;
            border: 1px solid #cbd5e1;
            transition: transform 0.2s ease;
        }}
        .screenshot-thumbnail:hover {{
            transform: scale(1.05);
        }}
        
        /* Fullscreen Modal */
        .modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.85);
            align-items: center;
            justify-content: center;
        }}
        .modal-content {{
            max-width: 90%;
            max-height: 90%;
            box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
            border-radius: 8px;
        }}
        .close-modal {{
            position: absolute;
            top: 20px;
            right: 30px;
            color: white;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <span>Momentec Suite</span>
            <span style="font-size: 11px; background-color: #ef4444; padding: 2px 6px; border-radius: 4px;">PLAYWRIGHT</span>
        </div>
        <div class="menu-list">
            {menu_items_html}
        </div>
    </div>
    
    <div class="main-panel">
        <div class="dashboard">
            <div class="dash-card">
                <span class="dash-card-title">Scenarios Run</span>
                <span class="dash-card-value">{total_tests}</span>
            </div>
            <div class="dash-card" style="border-left: 4px solid #10b981;">
                <span class="dash-card-title">Passed Scenarios</span>
                <span class="dash-card-value" style="color: #10b981;">{passed_tests}</span>
            </div>
            <div class="dash-card" style="border-left: 4px solid #ef4444;">
                <span class="dash-card-title">Failed Scenarios</span>
                <span class="dash-card-value" style="color: #ef4444;">{failed_tests}</span>
            </div>
            <div class="dash-card">
                <span class="dash-card-title">Total Duration</span>
                <span class="dash-card-value">{duration}</span>
            </div>
            
            <div class="dash-chart-container">
                <svg width="100" height="100" viewBox="0 0 42 42">
                    <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#ef4444" stroke-width="6"></circle>
                    <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#10b981" stroke-width="6" 
                            stroke-dasharray="{pass_pct} {dash_offset}" stroke-dashoffset="25"></circle>
                    <g class="chart-text">
                        <text x="50%" y="50%" class="chart-number" dy="3" text-anchor="middle" font-size="8" font-weight="bold" fill="#0f172a">
                            {pass_pct}%
                        </text>
                    </g>
                </svg>
            </div>
        </div>
        
        <div class="details-area">
            {details_panels_html}
        </div>
    </div>
    
    <!-- Modal popup -->
    <div id="screenshotModal" class="modal" onclick="closeModal()">
        <span class="close-modal">&times;</span>
        <img class="modal-content" id="modalImage" />
    </div>

    <script>
        function showTest(index) {{
            document.querySelectorAll('.test-detail').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.test-menu-item').forEach(el => el.classList.remove('active'));
            
            document.getElementById('test-detail-' + index).style.display = 'block';
            document.getElementById('test-menu-' + index).classList.add('active');
        }}

        function openModal(src) {{
            const modal = document.getElementById("screenshotModal");
            const modalImg = document.getElementById("modalImage");
            modal.style.display = "flex";
            modalImg.src = src;
        }}

        function closeModal() {{
            document.getElementById("screenshotModal").style.display = "none";
        }}
    </script>
</body>
</html>
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"\n[REPORTER] Interactive Extent Report successfully generated at: {report_path}")
