"""Dashboard Tab - Phase 2"""
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class DashboardTab:
    def __init__(self, parent, database):
        self.frame = ttk.Frame(parent)
        self.database = database
        self._create_widgets()
        self.update_dashboard()
    
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
        
        # Top row
        top_frame = ttk.Frame(scrollable_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Threat gauge
        gauge_frame = ttk.LabelFrame(top_frame, text="Current Threat Level", padding=10)
        gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.gauge_fig = Figure(figsize=(4, 3), dpi=80)
        self.gauge_ax = self.gauge_fig.add_subplot(111, projection='polar')
        self.gauge_canvas = FigureCanvasTkAgg(self.gauge_fig, gauge_frame)
        self.gauge_canvas.get_tk_widget().pack()
        
        # Metrics cards
        metrics_frame = ttk.LabelFrame(top_frame, text="Live Metrics", padding=10)
        metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.total_scans_label = ttk.Label(metrics_frame, text="Total Scans: 0", font=('Arial', 12))
        self.total_scans_label.pack(pady=5)
        
        self.threats_blocked_label = ttk.Label(metrics_frame, text="Threats Blocked: 0", font=('Arial', 12))
        self.threats_blocked_label.pack(pady=5)
        
        self.avg_threat_label = ttk.Label(metrics_frame, text="Avg Threat: 0.0", font=('Arial', 12))
        self.avg_threat_label.pack(pady=5)
        
        # Bottom row
        bottom_frame = ttk.Frame(scrollable_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Timeline chart
        timeline_frame = ttk.LabelFrame(bottom_frame, text="24-Hour Threat Timeline", padding=10)
        timeline_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.timeline_fig = Figure(figsize=(10, 4), dpi=80)
        self.timeline_ax = self.timeline_fig.add_subplot(111)
        self.timeline_canvas = FigureCanvasTkAgg(self.timeline_fig, timeline_frame)
        self.timeline_canvas.get_tk_widget().pack()
    
    def update_dashboard(self):
        stats = self.database.get_stats()
        
        # Update metrics
        self.total_scans_label.config(text=f"Total Scans: {stats['total_scans']}")
        self.threats_blocked_label.config(text=f"Threats Blocked: {stats['total_threats']}")
        self.avg_threat_label.config(text=f"Avg Threat: {stats['avg_threat']}")
        
        # Update gauge
        self._draw_gauge(stats['avg_threat'])
        
        # Update timeline
        self._draw_timeline()
        
        # Schedule next update
        self.frame.after(5000, self.update_dashboard)
    
    def _draw_gauge(self, value):
        self.gauge_ax.clear()
        theta = (value / 10) * 180
        colors = ['green' if value < 4 else 'yellow' if value < 7 else 'red']
        self.gauge_ax.barh(0, theta, height=0.3, color=colors[0])
        self.gauge_ax.set_ylim(-0.5, 0.5)
        self.gauge_ax.set_xlim(0, 180)
        self.gauge_ax.set_theta_zero_location('W')
        self.gauge_ax.set_theta_direction(1)
        self.gauge_ax.set_xticks([])
        self.gauge_ax.set_yticks([])
        self.gauge_ax.text(90, 0, f'{value}/10', ha='center', va='center', fontsize=20, fontweight='bold')
        self.gauge_canvas.draw()
    
    def _draw_timeline(self):
        threats = self.database.get_threats_24h()
        self.timeline_ax.clear()
        
        if threats:
            times = [datetime.fromisoformat(t[0]) for t in threats]
            levels = [t[1] for t in threats]
            self.timeline_ax.plot(times, levels, marker='o', linestyle='-', color='red')
        
        self.timeline_ax.set_xlabel('Time')
        self.timeline_ax.set_ylabel('Threat Level')
        self.timeline_ax.set_ylim(0, 10)
        self.timeline_ax.grid(True, alpha=0.3)
        self.timeline_fig.autofmt_xdate()
        self.timeline_canvas.draw()
    
    def get_frame(self):
        return self.frame
