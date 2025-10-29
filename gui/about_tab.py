"""About Tab - System information"""
import tkinter as tk
from tkinter import ttk
import platform
import psutil

class AboutTab:
    def __init__(self, parent, multiagent):
        self.parent = parent
        self.multiagent = multiagent
        
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        # Canvas with scrollbar
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)
        
        # Title
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(pady=20)
        
        ttk.Label(title_frame, text="HIDR Multi-Agent System", font=('Arial', 18, 'bold')).pack()
        ttk.Label(title_frame, text="Hybrid Intelligent Detection & Response", font=('Arial', 10)).pack()
        ttk.Label(title_frame, text="Version 3.0 - October 2025", font=('Arial', 9)).pack(pady=5)
        
        # System Info
        sys_frame = ttk.LabelFrame(scrollable_frame, text="System Information", padding=20)
        sys_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
        
        # Get disk space safely for Windows
        try:
            import os
            if platform.system() == 'Windows':
                disk_path = os.path.abspath(os.sep)
            else:
                disk_path = '/'
            disk_free = psutil.disk_usage(disk_path).free // (1024**3)
        except:
            disk_free = "N/A"
        
        info = [
            ("Operating System", f"{platform.system()} {platform.release()}"),
            ("Python Version", platform.python_version()),
            ("CPU Cores", psutil.cpu_count()),
            ("RAM", f"{psutil.virtual_memory().total // (1024**3)} GB"),
            ("Disk Space", f"{disk_free} GB free" if disk_free != "N/A" else "N/A")
        ]
        
        for i, (label, value) in enumerate(info):
            ttk.Label(sys_frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Label(sys_frame, text=str(value)).grid(row=i, column=1, sticky=tk.W, padx=20, pady=5)
            
        
        # Agent Status
        agent_frame = ttk.LabelFrame(scrollable_frame, text="Agent Status", padding=20)
        agent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        agents = [
            ("YARA Scanner", "Active" if self.multiagent.yara_scanner else "Disabled"),
            ("Expert System", "Active" if self.multiagent.expert_system else "Disabled"),
            ("LangGraph", "Active" if self.multiagent.langgraph_orchestrator else "Disabled"),
            ("Detection Agent", "Active"),
            ("Intelligence Agent", "Active"),
            ("Analysis Agent", "Active"),
            ("Coordinator Agent", "Active"),
            ("Response Agent", "Active")
        ]
        
        for i, (agent, status) in enumerate(agents):
            ttk.Label(agent_frame, text=f"{agent}:", font=('Arial', 10)).grid(row=i, column=0, sticky=tk.W, pady=3)
            color = "green" if status == "Active" else "gray"
            ttk.Label(agent_frame, text=status, foreground=color, font=('Arial', 10, 'bold')).grid(row=i, column=1, sticky=tk.W, padx=20, pady=3)
        
        # Creator Info
        credits_frame = ttk.Frame(scrollable_frame)
        credits_frame.pack(pady=20)
        
        ttk.Label(credits_frame, text="Developed by SecuVortex", font=('Arial', 11, 'bold')).pack()
        ttk.Label(credits_frame, text="Lakshya Agarwal", font=('Arial', 10)).pack()
        ttk.Label(credits_frame, text="secuvortex@gmail.com", font=('Arial', 9), foreground='blue').pack(pady=3)
        ttk.Label(credits_frame, text="Built for Defensive Cybersecurity", font=('Arial', 9, 'italic')).pack(pady=5)
        ttk.Label(credits_frame, text="© October 2025 SecuVortex", font=('Arial', 8)).pack()
    
    def get_frame(self):
        return self.frame

    