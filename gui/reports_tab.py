"""Reports Tab - Statistics and export"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import csv
from datetime import datetime
import time

class ReportsTab:
    def __init__(self, parent):
        self.parent = parent
        self.start_time = time.time()
        self.stats = {
            'total_scans': 0,
            'threats_detected': 0,
            'files_quarantined': 0,
            'yara_detections': 0,
            'mb_detections': 0,
            'actions_taken': 0
        }
        self.scan_results = []
        
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        # Canvas with scrollbar
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Control frame
        control_frame = ttk.Frame(scrollable_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Refresh Stats", command=self._refresh_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Data", command=self._clear_data).pack(side=tk.LEFT, padx=5)
        
        # Statistics display
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📈 Summary Statistics", padding=15)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create grid of stats (2 columns)
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        row = 0
        col = 0
        for key, value in self.stats.items():
            label_text = key.replace('_', ' ').title()
            frame = ttk.Frame(stats_grid)
            frame.grid(row=row, column=col, padx=15, pady=5, sticky=tk.W)
            
            ttk.Label(frame, text=label_text, font=('Arial', 9)).pack(anchor=tk.W)
            label = ttk.Label(frame, text=str(value), font=('Arial', 14, 'bold'))
            label.pack(anchor=tk.W)
            setattr(self, f"{key}_label", label)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Uptime
        uptime_frame = ttk.Frame(stats_grid)
        uptime_frame.grid(row=row, column=col, padx=15, pady=5, sticky=tk.W)
        ttk.Label(uptime_frame, text="Uptime", font=('Arial', 9)).pack(anchor=tk.W)
        self.uptime_label = ttk.Label(uptime_frame, text="00:00:00", font=('Arial', 14, 'bold'))
        self.uptime_label.pack(anchor=tk.W)
        self._update_uptime()
        
        # Threats table
        threats_frame = ttk.LabelFrame(scrollable_frame, text="🔴 Recent Threats", padding=10)
        threats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Time", "Process", "Threat", "YARA", "Action")
        self.threats_tree = ttk.Treeview(threats_frame, columns=columns, show="headings", height=8)
        
        widths = {"Time": 80, "Process": 150, "Threat": 60, "YARA": 60, "Action": 120}
        for col in columns:
            self.threats_tree.heading(col, text=col)
            self.threats_tree.column(col, width=widths.get(col, 100))
        
        scroll = ttk.Scrollbar(threats_frame, orient=tk.VERTICAL, command=self.threats_tree.yview)
        self.threats_tree.configure(yscrollcommand=scroll.set)
        
        self.threats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Export buttons
        export_frame = ttk.LabelFrame(scrollable_frame, text="Export Reports", padding=20)
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(export_frame, text="Export as JSON", command=self.export_json, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export as CSV", command=self.export_csv, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export as HTML", command=self.export_html, width=20).pack(side=tk.LEFT, padx=5)
        
        # Recent activity
        activity_frame = ttk.LabelFrame(scrollable_frame, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.activity_text = tk.Text(activity_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(activity_frame, command=self.activity_text.yview)
        self.activity_text.configure(yscrollcommand=scrollbar.set)
        
        self.activity_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.activity_text.insert('1.0', "No activity yet. Start scanning to see results.")
        self.activity_text.config(state=tk.DISABLED)
    
    def _update_uptime(self):
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.frame.after(1000, self._update_uptime)
    
    def _refresh_stats(self):
        for key, value in self.stats.items():
            label = getattr(self, f"{key}_label", None)
            if label:
                label.config(text=str(value))
        messagebox.showinfo("Refreshed", "Statistics refreshed successfully")
    
    def _clear_data(self):
        if messagebox.askyesno("Clear Data", "Clear all statistics and threat data?"):
            self.stats = {key: 0 for key in self.stats}
            self.scan_results = []
            self.threats_tree.delete(*self.threats_tree.get_children())
            self.activity_text.config(state=tk.NORMAL)
            self.activity_text.delete('1.0', tk.END)
            self.activity_text.insert('1.0', "Data cleared. Start scanning to see new results.")
            self.activity_text.config(state=tk.DISABLED)
            self._refresh_stats()
    
    def update_stats(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] = value
                label = getattr(self, f"{key}_label", None)
                if label:
                    label.config(text=str(value))
    
    def log_threat(self, process_name, threat_level, yara_count, action):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.threats_tree.insert('', 0, values=(
            timestamp, process_name[:25], f"{threat_level}/10", yara_count, action
        ))
        # Keep only last 100 entries
        children = self.threats_tree.get_children()
        if len(children) > 100:
            self.threats_tree.delete(children[-1])
    
    def add_activity(self, message):
        self.activity_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.activity_text.insert('1.0', f"[{timestamp}] {message}\n")
        self.activity_text.config(state=tk.DISABLED)
    
    def export_json(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'statistics': self.stats,
                    'activity': self.activity_text.get('1.0', tk.END).strip()
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Metric', 'Value'])
                    for key, value in self.stats.items():
                        writer.writerow([key.replace('_', ' ').title(), value])
                
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def export_html(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                html = f"""<!DOCTYPE html>
<html>
<head>
    <title>HIDR System Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .activity {{ background: #f9f9f9; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>HIDR Multi-Agent System Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Statistics</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
"""
                for key, value in self.stats.items():
                    html += f"        <tr><td>{key.replace('_', ' ').title()}</td><td>{value}</td></tr>\n"
                
                html += "    </table>\n\n"
                
                # Add threats table
                html += "    <h2>Recent Threats</h2>\n"
                html += "    <table>\n"
                html += "        <tr><th>Time</th><th>Process</th><th>Threat Level</th><th>YARA Matches</th><th>Action</th></tr>\n"
                
                for item in self.threats_tree.get_children():
                    values = self.threats_tree.item(item)['values']
                    html += f"        <tr><td>{values[0]}</td><td>{values[1]}</td><td>{values[2]}</td><td>{values[3]}</td><td>{values[4]}</td></tr>\n"
                
                html += "    </table>\n\n"
                
                html += f"""    <h2>Recent Activity</h2>
    <div class="activity">
        <pre>{self.activity_text.get('1.0', tk.END).strip()}</pre>
    </div>
</body>
</html>"""
                
                with open(filename, 'w') as f:
                    f.write(html)
                
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def get_frame(self):
        return self.frame
