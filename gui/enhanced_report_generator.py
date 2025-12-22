"""Enhanced HTML Report Generator with Charts and Forensic Details"""
from datetime import datetime
from typing import List, Dict, Any

class EnhancedReportGenerator:
    @staticmethod
    def generate_html_report(stats: Dict, threats: List[Dict], activity: str, scan_results: List[Dict] = None) -> str:
        """Generate professional HTML report with charts and forensic details"""
        
        scan_results = scan_results or []
        
        # Calculate chart data
        threat_distribution = EnhancedReportGenerator._calculate_threat_distribution(threats)
        score_distribution = EnhancedReportGenerator._calculate_score_distribution(threats)
        timeline_data = EnhancedReportGenerator._calculate_timeline_data(threats)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIDR Security Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 36px; margin-bottom: 10px; }}
        .header p {{ font-size: 16px; opacity: 0.9; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-4px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }}
        .stat-label {{ font-size: 14px; color: #666; margin-bottom: 8px; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #2196F3; }}
        
        .charts-section {{
            padding: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }}
        .chart-card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .chart-card h3 {{ margin-bottom: 20px; color: #333; font-size: 18px; }}
        
        .threats-section {{ padding: 30px; }}
        .threat-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #f44336;
        }}
        .threat-card.medium {{ border-left-color: #ff9800; }}
        .threat-card.low {{ border-left-color: #4caf50; }}
        
        .threat-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .threat-title {{ font-size: 18px; font-weight: bold; }}
        .threat-score {{
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        .score-critical {{ background: #ffebee; color: #c62828; }}
        .score-high {{ background: #fff3e0; color: #e65100; }}
        .score-medium {{ background: #fff9c4; color: #f57f17; }}
        .score-low {{ background: #e8f5e9; color: #2e7d32; }}
        
        .forensic-details {{
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            margin-top: 16px;
        }}
        .forensic-item {{ margin: 8px 0; font-size: 14px; }}
        .forensic-label {{ font-weight: bold; color: #666; }}
        
        .why-quarantined {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 16px;
            margin-top: 16px;
            border-radius: 4px;
        }}
        .why-quarantined h4 {{ color: #856404; margin-bottom: 8px; }}
        .why-quarantined p {{ color: #856404; line-height: 1.6; }}
        
        .confidence-breakdown {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 12px;
        }}
        .confidence-item {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
        }}
        .confidence-label {{ font-size: 12px; color: #666; }}
        .confidence-value {{ font-size: 20px; font-weight: bold; color: #2196F3; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #2196F3;
            color: white;
            padding: 16px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 16px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover {{ background: #f5f5f5; }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-yara {{ background: #e3f2fd; color: #1976d2; }}
        .badge-mb {{ background: #f3e5f5; color: #7b1fa2; }}
        .badge-mitre {{ background: #fff3e0; color: #e65100; }}
        
        .activity-log {{
            background: #263238;
            color: #aed581;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: 1fr; }}
            .charts-section {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ HIDR Security Report</h1>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>Multi-Agent Endpoint Detection & Response System</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Scans</div>
                <div class="stat-value">{stats.get('total_scans', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Threats Detected</div>
                <div class="stat-value" style="color: #f44336;">{stats.get('threats_detected', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Files Quarantined</div>
                <div class="stat-value" style="color: #ff9800;">{stats.get('files_quarantined', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">YARA Detections</div>
                <div class="stat-value" style="color: #9c27b0;">{stats.get('yara_detections', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">MalwareBazaar Hits</div>
                <div class="stat-value" style="color: #ff5722;">{stats.get('mb_detections', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Actions Taken</div>
                <div class="stat-value" style="color: #4caf50;">{stats.get('actions_taken', 0)}</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-card">
                <h3>📊 Threat Distribution</h3>
                <canvas id="threatChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>📈 Threat Score Distribution</h3>
                <canvas id="scoreChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>⏱️ Detection Timeline</h3>
                <canvas id="timelineChart"></canvas>
            </div>
        </div>
"""

        # Add detailed threat cards
        if threats:
            html += """
        <div class="threats-section">
            <h2 style="margin-bottom: 20px; color: #333;">🔴 Detailed Threat Analysis</h2>
"""
            for threat in threats[:10]:  # Show top 10 threats
                severity_class = EnhancedReportGenerator._get_severity_class(threat.get('threat_level', 0))
                score_class = EnhancedReportGenerator._get_score_class(threat.get('threat_level', 0))
                
                html += f"""
            <div class="threat-card {severity_class}">
                <div class="threat-header">
                    <div class="threat-title">{threat.get('process', 'Unknown Process')}</div>
                    <div class="threat-score {score_class}">{threat.get('threat_level', 0)}/10</div>
                </div>
                
                <div style="margin: 12px 0;">
                    <strong>File Path:</strong> <code>{threat.get('path', 'N/A')}</code>
                </div>
                
                <div style="margin: 12px 0;">
                    <strong>Detection Reasons:</strong> {', '.join(threat.get('reasons', ['Unknown']))}
                </div>
                
                <div style="margin: 12px 0;">
"""
                
                # Add badges
                if threat.get('yara_matches'):
                    html += f'<span class="badge badge-yara">YARA: {len(threat["yara_matches"])} matches</span> '
                if threat.get('mb_detected'):
                    html += '<span class="badge badge-mb">MalwareBazaar</span> '
                if threat.get('mitre_techniques'):
                    html += f'<span class="badge badge-mitre">MITRE: {", ".join(threat["mitre_techniques"][:2])}</span>'
                
                html += """
                </div>
"""
                
                # Add forensic details if available
                if threat.get('forensic'):
                    forensic = threat['forensic']
                    html += """
                <div class="forensic-details">
                    <h4 style="margin-bottom: 12px;">🔍 Forensic Evidence</h4>
"""
                    if forensic.get('parent_chain'):
                        html += f'<div class="forensic-item"><span class="forensic-label">Parent Chain:</span> {" → ".join(forensic["parent_chain"])}</div>'
                    if forensic.get('command_line'):
                        html += f'<div class="forensic-item"><span class="forensic-label">Command Line:</span> <code>{forensic["command_line"][:100]}</code></div>'
                    if forensic.get('file_hashes'):
                        html += f'<div class="forensic-item"><span class="forensic-label">SHA-256:</span> <code>{forensic["file_hashes"].get("sha256", "N/A")[:16]}...</code></div>'
                    if forensic.get('network'):
                        for conn in forensic['network'][:2]:
                            html += f'<div class="forensic-item"><span class="forensic-label">Network:</span> {conn.get("ip")} ({conn.get("domain", "unknown")})</div>'
                    
                    html += """
                </div>
"""
                
                # Add "Why Quarantined" explanation
                if threat.get('action') in ['terminate_permanent', 'quarantine']:
                    explanation = EnhancedReportGenerator._generate_quarantine_explanation(threat)
                    html += f"""
                <div class="why-quarantined">
                    <h4>⚠️ Why This Was Quarantined</h4>
                    <p>{explanation}</p>
                    
                    <div class="confidence-breakdown">
"""
                    
                    # Show confidence breakdown
                    breakdown = EnhancedReportGenerator._calculate_confidence_breakdown(threat)
                    for component, score in breakdown.items():
                        html += f"""
                        <div class="confidence-item">
                            <div class="confidence-label">{component}</div>
                            <div class="confidence-value">{score}</div>
                        </div>
"""
                    
                    html += """
                    </div>
                </div>
"""
                
                html += """
            </div>
"""
            
            html += """
        </div>
"""
        
        # Add activity log
        html += f"""
        <div style="padding: 30px;">
            <h2 style="margin-bottom: 20px; color: #333;">📝 Activity Log</h2>
            <div class="activity-log">{activity}</div>
        </div>
        
        <div style="padding: 30px; text-align: center; color: #666; border-top: 1px solid #e0e0e0;">
            <p>HIDR v3.0 | SecuVortex (Lakshya Agarwal) | © 2025</p>
            <p style="margin-top: 8px; font-size: 14px;">Multi-Agent Endpoint Detection & Response System</p>
        </div>
    </div>
    
    <script>
        // Threat Distribution Chart
        new Chart(document.getElementById('threatChart'), {{
            type: 'doughnut',
            data: {{
                labels: {list(threat_distribution.keys())},
                datasets: [{{
                    data: {list(threat_distribution.values())},
                    backgroundColor: ['#f44336', '#ff9800', '#ffc107', '#4caf50', '#2196f3']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Score Distribution Chart
        new Chart(document.getElementById('scoreChart'), {{
            type: 'bar',
            data: {{
                labels: {list(score_distribution.keys())},
                datasets: [{{
                    label: 'Threats',
                    data: {list(score_distribution.values())},
                    backgroundColor: '#2196f3'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
        
        // Timeline Chart
        new Chart(document.getElementById('timelineChart'), {{
            type: 'line',
            data: {{
                labels: {list(timeline_data.keys())},
                datasets: [{{
                    label: 'Detections',
                    data: {list(timeline_data.values())},
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        return html
    
    @staticmethod
    def _calculate_threat_distribution(threats: List[Dict]) -> Dict[str, int]:
        """Calculate distribution of threat types"""
        distribution = {'Critical (9-10)': 0, 'High (7-8)': 0, 'Medium (5-6)': 0, 'Low (3-4)': 0, 'Safe (0-2)': 0}
        for threat in threats:
            level = threat.get('threat_level', 0)
            if level >= 9:
                distribution['Critical (9-10)'] += 1
            elif level >= 7:
                distribution['High (7-8)'] += 1
            elif level >= 5:
                distribution['Medium (5-6)'] += 1
            elif level >= 3:
                distribution['Low (3-4)'] += 1
            else:
                distribution['Safe (0-2)'] += 1
        return distribution
    
    @staticmethod
    def _calculate_score_distribution(threats: List[Dict]) -> Dict[str, int]:
        """Calculate score distribution"""
        distribution = {'0-2': 0, '3-4': 0, '5-6': 0, '7-8': 0, '9-10': 0}
        for threat in threats:
            level = threat.get('threat_level', 0)
            if level <= 2:
                distribution['0-2'] += 1
            elif level <= 4:
                distribution['3-4'] += 1
            elif level <= 6:
                distribution['5-6'] += 1
            elif level <= 8:
                distribution['7-8'] += 1
            else:
                distribution['9-10'] += 1
        return distribution
    
    @staticmethod
    def _calculate_timeline_data(threats: List[Dict]) -> Dict[str, int]:
        """Calculate timeline data (last 7 days)"""
        from collections import defaultdict
        timeline = defaultdict(int)
        for threat in threats:
            timestamp = threat.get('timestamp', datetime.now().strftime('%H:%M'))
            hour = timestamp.split(':')[0] if ':' in timestamp else '00'
            timeline[f"{hour}:00"] += 1
        return dict(sorted(timeline.items())[:7])
    
    @staticmethod
    def _get_severity_class(threat_level: int) -> str:
        """Get CSS class for severity"""
        if threat_level >= 8:
            return 'critical'
        elif threat_level >= 5:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _get_score_class(threat_level: int) -> str:
        """Get CSS class for score badge"""
        if threat_level >= 9:
            return 'score-critical'
        elif threat_level >= 7:
            return 'score-high'
        elif threat_level >= 5:
            return 'score-medium'
        else:
            return 'score-low'
    
    @staticmethod
    def _generate_quarantine_explanation(threat: Dict) -> str:
        """Generate plain-language explanation for quarantine"""
        process = threat.get('process', 'Unknown')
        path = threat.get('path', 'unknown location')
        reasons = threat.get('reasons', [])
        yara_count = len(threat.get('yara_matches', []))
        mitre = threat.get('mitre_techniques', [])
        score = threat.get('threat_level', 0)
        
        explanation = f"Quarantined because process `{process}` "
        
        if 'temp' in path.lower() or 'download' in path.lower():
            explanation += f"was running from suspicious location `{path}` "
        
        if yara_count > 0:
            yara_rules = [m.get('rule', 'Unknown') for m in threat.get('yara_matches', [])]
            explanation += f"and matched {yara_count} YARA rule(s): {', '.join(yara_rules[:2])} "
        
        if mitre:
            explanation += f"with MITRE ATT&CK technique(s): {', '.join(mitre[:2])} "
        
        explanation += f"— confidence: {score * 10}%. "
        
        explanation += "Recommended action: Isolate host, collect forensic data, remove malicious file, and rotate credentials if data exfiltration detected."
        
        return explanation
    
    @staticmethod
    def _calculate_confidence_breakdown(threat: Dict) -> Dict[str, int]:
        """Calculate confidence score breakdown"""
        breakdown = {}
        
        yara_count = len(threat.get('yara_matches', []))
        if yara_count > 0:
            breakdown['YARA Match'] = min(yara_count * 30, 50)
        
        if threat.get('mb_detected'):
            breakdown['MalwareBazaar'] = 35
        
        if threat.get('mitre_techniques'):
            breakdown['MITRE ATT&CK'] = 20
        
        reasons = threat.get('reasons', [])
        if any('temp' in r.lower() or 'download' in r.lower() for r in reasons):
            breakdown['Suspicious Location'] = 15
        
        if threat.get('forensic', {}).get('network'):
            breakdown['Network Activity'] = 20
        
        return breakdown
