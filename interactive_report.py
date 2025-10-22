import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import webbrowser
import base64
from io import BytesIO
try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.offline import plot
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


class InteractiveReportGenerator:

    def __init__(self, incident_log_path):
        self.incident_log = Path(incident_log_path)
        self.output_dir = Path.cwd() / 'reports'
        self.output_dir.mkdir(exist_ok=True)

    def generate_full_report(self):
        if not PLOTTING_AVAILABLE:
            print('Plotting libraries not available. Generating simple report.'
                )
            return None
        try:
            df = pd.read_csv(self.incident_log)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        except (FileNotFoundError, pd.errors.EmptyDataError):
            df = pd.DataFrame(columns=['timestamp', 'type', 'process_name',
                'action', 'details'])
        timeline_chart = self.generate_charts(df)
        threat_pie_chart = self.create_threat_pie_chart(df)
        activity_heatmap = self.create_activity_heatmap(df)
        incident_table = self.create_incident_table(df)
        recommendations = self.generate_recommendations(df)
        stats_cards = self.generate_stats_cards(df)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Interactive Security Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>{self.get_css_styles()}</style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Interactive Security Report</h1>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Period: {self.get_report_period(df)}</p>
                </div>
                
                <div class="grid-container">
                    {stats_cards}
                    <div class="chart-card large">{timeline_chart}</div>
                    <div class="chart-card">{threat_pie_chart}</div>
                    <div class="chart-card">{activity_heatmap}</div>
                    <div class="chart-card full-width">{incident_table}</div>
                    <div class="chart-card full-width">
                        <h2>Recommendations</h2>
                        {recommendations}
                    </div>
                </div>
            </div>
            <script>{self.get_javascript_functions(df)}</script>
        </body>
        </html>
        """
        report_path = (self.output_dir /
            f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f'Interactive report generated: {report_path}')
        return report_path

    def generate_charts(self, df):
        daily_counts = df.groupby(df['timestamp'].dt.date).size().reset_index()
        daily_counts.columns = ['date', 'incidents']
        fig = px.line(daily_counts, x='date', y='incidents', title=
            'Security Incidents Over Time', markers=True)
        fig.update_layout(xaxis_title='Date', yaxis_title=
            'Number of Incidents', hovermode='x unified')
        return plot(fig, output_type='div', include_plotlyjs=False)

    def create_threat_pie_chart(self, df):
        if df.empty:
            return ''
        fig = px.pie(df, names='type', title='Incident Type Distribution')
        return plot(fig, output_type='div', include_plotlyjs=False)

    def create_activity_heatmap(self, df):
        if df.empty:
            return ''
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day_name()
        heatmap_data = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
        fig = px.imshow(heatmap_data.values, x=heatmap_data.columns, y=
            heatmap_data.index, title='Activity Heatmap (Day vs Hour)',
            color_continuous_scale='Reds')
        return plot(fig, output_type='div', include_plotlyjs=False)

    def create_process_chart(self, df):
        if df.empty:
            return ''
        top_processes = df['process_name'].value_counts().nlargest(10)
        fig = px.bar(top_processes, x=top_processes.index, y=top_processes.
            values, title='Top 10 Flagged Processes')
        return plot(fig, output_type='div', include_plotlyjs=False)

    def generate_stats_cards(self, df):
        if df.empty:
            return "<div class='stat-card alert'>No incidents recorded</div>"
        total_incidents = len(df)
        process_alerts = len(df[df['type'] == 'suspicious_process'])
        file_alerts = len(df[df['type'].isin(['file_modified',
            'file_deleted'])])
        if len(df) > 1:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            recent_24h = df[df['timestamp'] > datetime.now() - timedelta(
                hours=24)]
            trend_24h = len(recent_24h)
        else:
            trend_24h = 0
        stats_html = f"""
        <div class="stat-card"><h2>Total Incidents</h2><p>{total_incidents}</p></div>
        <div class="stat-card"><h2>Process Alerts</h2><p>{process_alerts}</p></div>
        <div class="stat-card"><h2>File Alerts</h2><p>{file_alerts}</p></div>
        <div class="stat-card"><h2>24h Trend</h2><p>{trend_24h}</p></div>
        """
        return stats_html

    def create_incident_table(self, df):
        if df.empty:
            return ''
        table_html = """
        <div class="table-controls">
            <input type="text" id="search-input" placeholder="Search incidents..." onkeyup="filterTable()">
            <select id="type-filter" onchange="filterTable()">
                <option value="">All Types</option>
                <option value="suspicious_process">Process Alerts</option>
                <option value="file_modified">File Modified</option>
                <option value="file_deleted">File Deleted</option>
            </select>
        </div>
        
        <div class="table-wrapper">
            <table id="incidents-table" class="incidents-table">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Timestamp ↕</th>
                        <th onclick="sortTable(1)">Type ↕</th>
                        <th onclick="sortTable(2)">Process/File ↕</th>
                        <th onclick="sortTable(3)">Action ↕</th>
                        <th onclick="sortTable(4)">Details ↕</th>
                    </tr>
                </thead>
                <tbody>
        """
        for _, row in df.iterrows():
            severity_class = self.get_severity_class(row['type'])
            table_html += f"""
            <tr class='{severity_class}'>
                <td>{row['timestamp']}</td>
                <td>{row['type']}</td>
                <td>{row['process_name']}</td>
                <td>{row['action']}</td>
                <td>{row['details']}</td>
            </tr>
            """
        table_html += """
                </tbody>
            </table>
        </div>
        """
        return table_html

    def generate_recommendations(self, df):
        recommendations = []
        if df.empty:
            recommendations.append(
                '✅ No security incidents detected. System appears secure.')
        else:
            process_alerts = len(df[df['type'] == 'suspicious_process'])
            file_alerts = len(df[df['type'].isin(['file_modified',
                'file_deleted'])])
            if process_alerts > 5:
                recommendations.append(
                    '⚠️ High number of process alerts detected. Review allowlist configuration.'
                    )
            if file_alerts > 10:
                recommendations.append(
                    '🔒 Multiple file modifications detected. Consider implementing stricter file protection.'
                    )
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                recent_activity = df[df['timestamp'] > datetime.now() -
                    timedelta(hours=1)]
                if len(recent_activity) > 5:
                    recommendations.append(
                        '🚨 High recent activity detected. Investigate potential ongoing attack.'
                        )
        recommendations.extend([
            '🔄 Regularly update the HIDR agent and threat signatures',
            '📊 Review incident reports weekly for trend analysis',
            '🛡️ Ensure all critical files are backed up regularly',
            '👥 Train users on security best practices',
            '🔍 Consider integrating with SIEM for centralized monitoring'])
        rec_html = "<ul class='recommendations-list'>"
        for rec in recommendations:
            rec_html += f'<li>{rec}</li>'
        rec_html += '</ul>'
        return rec_html

    def get_severity_class(self, incident_type):
        if 'process' in incident_type:
            return 'severity-high'
        elif 'modified' in incident_type:
            return 'severity-medium'
        else:
            return 'severity-low'

    def get_report_period(self, df):
        if df.empty:
            return 'No data'
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            start_date = df['timestamp'].min().strftime('%Y-%m-%d')
            end_date = df['timestamp'].max().strftime('%Y-%m-%d')
            return f'{start_date} to {end_date}'
        except Exception:
            return 'Unknown period'

    def get_css_styles(self):
        return """
        body { font-family: 'Segoe UI', sans-serif; background-color: #f4f7fc; color: #333; }
        .container { max-width: 1200px; margin: auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 20px; }
        .grid-container { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
        .chart-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .large { grid-column: span 4; }
        .full-width { grid-column: span 4; }
        .stat-card { background: #fff; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h2 { margin: 0; font-size: 1em; color: #666; }
        .stat-card p { font-size: 2em; font-weight: bold; color: #333; }
        .incidents-table { width: 100%; border-collapse: collapse; }
        .incidents-table th, .incidents-table td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }
        .incidents-table th { background-color: #f8f9fa; cursor: pointer; }
        .recommendations-list { list-style-type: none; padding: 0; }
        .recommendations-list li { margin-bottom: 10px; }
        """

    def get_javascript_functions(self, df):
        return """
        function filterTable() {
            // JS for filtering table
        }
        function sortTable(n) {
            // JS for sorting table
        }
        """


def main():
    if not PLOTTING_AVAILABLE:
        print(
            'Please install required libraries: pip install pandas matplotlib seaborn plotly'
            )
        return
    log_file = Path.cwd() / 'hidr_incidents.csv'
    if not log_file.exists():
        print(f'Incident log not found at {log_file}. Creating dummy data.')
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'type', 'process_name', 'pid',
                'path', 'cmdline', 'action', 'details'])
            writer.writerow([(datetime.now() - timedelta(days=1)).isoformat
                (), 'suspicious_process', 'powershell.exe', 1234, '', '',
                'TERMINATED', 'Encoded command'])
    generator = InteractiveReportGenerator(log_file)
    report = generator.generate_full_report()
    if report:
        webbrowser.open(f'file://{report.absolute()}')


if __name__ == '__main__':
    main()
