"""Settings Tab - Configuration management"""
import tkinter as tk
from tkinter import ttk, messagebox
import yaml

class SettingsTab:
    def __init__(self, parent, auto_scanner=None, config_path="config.yaml"):
        self.parent = parent
        self.auto_scanner = auto_scanner
        self.config_path = config_path
        self.config = self._load_config()
        
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            return {}
    
    def _get_env_var(self, key):
        """Get environment variable from .env file"""
        import os
        try:
            # Try from environment first
            value = os.getenv(key)
            if value:
                return value
            
            # Try from .env file
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith(key):
                            return line.split('=', 1)[1].strip()
        except:
            pass
        return ""
    
    def _toggle_visibility(self, entry):
        """Toggle password visibility"""
        if entry.cget('show') == '*':
            entry.config(show='')
        else:
            entry.config(show='*')
    
    def _test_malwarebazaar(self):
        """Test MalwareBazaar API connection"""
        api_key = self.mb_api_key.get()
        if not api_key:
            messagebox.showwarning("No API Key", "Please enter a MalwareBazaar API key")
            return
        
        try:
            import requests
            headers = {'Auth-Key': api_key}
            data = {'query': 'get_info', 'hash': '094fd325049b8a9cf6d3e5ef2a6d4cc6a567d7d49c35f8bb8dd9e3c6acf3d78d'}
            response = requests.post('https://mb-api.abuse.ch/api/v1/', headers=headers, data=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('query_status') in ['ok', 'no_results']:
                    messagebox.showinfo("✅ Success", "MalwareBazaar API key is valid!")
                else:
                    messagebox.showerror("❌ Error", f"API returned: {result.get('query_status')}")
            else:
                messagebox.showerror("❌ Error", f"HTTP {response.status_code}: Invalid API key or connection failed")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Connection failed: {str(e)}")
    
    def _test_virustotal(self):
        """Test VirusTotal API connection"""
        api_key = self.vt_api_key.get()
        if not api_key:
            messagebox.showwarning("No API Key", "Please enter a VirusTotal API key")
            return
        
        try:
            import requests
            headers = {'x-apikey': api_key}
            response = requests.get('https://www.virustotal.com/api/v3/users/current', headers=headers, timeout=5)
            
            if response.status_code == 200:
                messagebox.showinfo("✅ Success", "VirusTotal API key is valid!")
            elif response.status_code == 401:
                messagebox.showerror("❌ Error", "Invalid API key")
            else:
                messagebox.showerror("❌ Error", f"HTTP {response.status_code}: Connection failed")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Connection failed: {str(e)}")
    
    def _save_env_file(self):
        """Save API keys to .env file"""
        import os
        env_content = []
        
        # Read existing .env
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if not line.startswith('MALWAREBAZAAR_API_KEY') and not line.startswith('VIRUSTOTAL_API_KEY'):
                        env_content.append(line.rstrip())
        
        # Add new keys
        if self.mb_api_key.get():
            env_content.append(f"MALWAREBAZAAR_API_KEY={self.mb_api_key.get()}")
        if self.vt_api_key.get():
            env_content.append(f"VIRUSTOTAL_API_KEY={self.vt_api_key.get()}")
        
        # Write back
        with open('.env', 'w') as f:
            f.write('\n'.join(env_content) + '\n')
    
    def _create_widgets(self):
        # API Keys
        api_frame = ttk.LabelFrame(self.frame, text="🔑 API Keys", padding=15)
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # MalwareBazaar
        ttk.Label(api_frame, text="MalwareBazaar API Key:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mb_api_key = tk.StringVar(value=self._get_env_var('MALWAREBAZAAR_API_KEY'))
        mb_entry = ttk.Entry(api_frame, textvariable=self.mb_api_key, width=50, show="*")
        mb_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(api_frame, text="Show", command=lambda: self._toggle_visibility(mb_entry), width=8).grid(row=0, column=2, padx=2)
        ttk.Button(api_frame, text="Test", command=self._test_malwarebazaar, width=8).grid(row=0, column=3, padx=2)
        
        # VirusTotal
        ttk.Label(api_frame, text="VirusTotal API Key:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.vt_api_key = tk.StringVar(value=self._get_env_var('VIRUSTOTAL_API_KEY'))
        vt_entry = ttk.Entry(api_frame, textvariable=self.vt_api_key, width=50, show="*")
        vt_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(api_frame, text="Show", command=lambda: self._toggle_visibility(vt_entry), width=8).grid(row=1, column=2, padx=2)
        ttk.Button(api_frame, text="Test", command=self._test_virustotal, width=8).grid(row=1, column=3, padx=2)
        
        ttk.Label(api_frame, text="Note: API keys are stored in .env file", foreground="gray", font=('Arial', 8)).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # Thresholds
        thresh_frame = ttk.LabelFrame(self.frame, text="Detection Thresholds", padding=20)
        thresh_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(thresh_frame, text="Threat Threshold (0-10):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.threat_threshold = tk.IntVar(value=self.config.get('detection', {}).get('threat_threshold', 5))
        ttk.Scale(thresh_frame, from_=0, to=10, variable=self.threat_threshold, orient=tk.HORIZONTAL, length=300).grid(row=0, column=1, padx=10)
        ttk.Label(thresh_frame, textvariable=self.threat_threshold).grid(row=0, column=2)
        
        ttk.Label(thresh_frame, text="Terminate Threshold (0-10):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.terminate_threshold = tk.IntVar(value=self.config.get('detection', {}).get('terminate_threshold', 8))
        ttk.Scale(thresh_frame, from_=0, to=10, variable=self.terminate_threshold, orient=tk.HORIZONTAL, length=300).grid(row=1, column=1, padx=10)
        ttk.Label(thresh_frame, textvariable=self.terminate_threshold).grid(row=1, column=2)
        
        # Expert System Weights
        weights_frame = ttk.LabelFrame(self.frame, text="Expert System Weights", padding=20)
        weights_frame.pack(fill=tk.X, padx=10, pady=10)
        
        weights = self.config.get('expert_system', {}).get('weights', {})
        
        ttk.Label(weights_frame, text="YARA Weight:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.yara_weight = tk.DoubleVar(value=weights.get('yara', 3.0))
        ttk.Scale(weights_frame, from_=0, to=5, variable=self.yara_weight, orient=tk.HORIZONTAL, length=300).grid(row=0, column=1, padx=10)
        ttk.Label(weights_frame, textvariable=self.yara_weight).grid(row=0, column=2)
        
        ttk.Label(weights_frame, text="VirusTotal Weight:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.vt_weight = tk.DoubleVar(value=weights.get('virustotal', 2.5))
        ttk.Scale(weights_frame, from_=0, to=5, variable=self.vt_weight, orient=tk.HORIZONTAL, length=300).grid(row=1, column=1, padx=10)
        ttk.Label(weights_frame, textvariable=self.vt_weight).grid(row=1, column=2)
        
        ttk.Label(weights_frame, text="Behavioral Weight:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.behavior_weight = tk.DoubleVar(value=weights.get('behavioral', 1.5))
        ttk.Scale(weights_frame, from_=0, to=5, variable=self.behavior_weight, orient=tk.HORIZONTAL, length=300).grid(row=2, column=1, padx=10)
        ttk.Label(weights_frame, textvariable=self.behavior_weight).grid(row=2, column=2)
        
        ttk.Label(weights_frame, text="MITRE Weight:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.mitre_weight = tk.DoubleVar(value=weights.get('mitre', 2.0))
        ttk.Scale(weights_frame, from_=0, to=5, variable=self.mitre_weight, orient=tk.HORIZONTAL, length=300).grid(row=3, column=1, padx=10)
        ttk.Label(weights_frame, textvariable=self.mitre_weight).grid(row=3, column=2)
        
        # Features
        features_frame = ttk.LabelFrame(self.frame, text="Features", padding=20)
        features_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.yara_enabled = tk.BooleanVar(value=self.config.get('yara', {}).get('enabled', True))
        ttk.Checkbutton(features_frame, text="Enable YARA Scanning", variable=self.yara_enabled).pack(anchor=tk.W, pady=5)
        
        self.expert_enabled = tk.BooleanVar(value=self.config.get('expert_system', {}).get('enabled', True))
        ttk.Checkbutton(features_frame, text="Enable Expert System", variable=self.expert_enabled).pack(anchor=tk.W, pady=5)
        
        self.langgraph_enabled = tk.BooleanVar(value=self.config.get('langgraph', {}).get('enabled', False))
        ttk.Checkbutton(features_frame, text="Enable LangGraph Orchestration", variable=self.langgraph_enabled).pack(anchor=tk.W, pady=5)
        
        # Trusted Paths
        paths_frame = ttk.LabelFrame(self.frame, text="Trusted Paths", padding=20)
        paths_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(paths_frame, text="Processes in these paths are trusted (0 threat):").pack(anchor=tk.W, pady=5)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(paths_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.paths_listbox = tk.Listbox(list_frame, height=5, yscrollcommand=scrollbar.set)
        self.paths_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.paths_listbox.yview)
        
        # Load existing paths
        trusted_paths = self.config.get('paths', {}).get('trusted_paths', [])
        for path in trusted_paths:
            self.paths_listbox.insert(tk.END, path)
        
        # Buttons for path management
        path_btn_frame = ttk.Frame(paths_frame)
        path_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(path_btn_frame, text="Add Path", command=self.add_trusted_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_btn_frame, text="Remove Selected", command=self.remove_trusted_path).pack(side=tk.LEFT, padx=5)
        
        # Auto-Scan
        autoscan_frame = ttk.LabelFrame(self.frame, text="Auto-Scan", padding=20)
        autoscan_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.autoscan_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(autoscan_frame, text="Enable Auto-Scan", variable=self.autoscan_enabled, command=self.toggle_autoscan).pack(anchor=tk.W, pady=5)
        
        ttk.Label(autoscan_frame, text="Scan Interval (minutes):").pack(anchor=tk.W, pady=5)
        self.scan_interval = tk.IntVar(value=5)
        ttk.Scale(autoscan_frame, from_=1, to=30, variable=self.scan_interval, orient=tk.HORIZONTAL, length=300).pack(anchor=tk.W, padx=20)
        ttk.Label(autoscan_frame, textvariable=self.scan_interval).pack(anchor=tk.W, padx=20)
        
        # Buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
    
    def add_trusted_path(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Trusted Directory")
        if path:
            # Normalize path
            path = path.lower().replace('/', '\\')
            if not path.endswith('\\'):
                path += '\\'
            
            # Check if already exists
            existing = self.paths_listbox.get(0, tk.END)
            if path not in existing:
                self.paths_listbox.insert(tk.END, path)
                messagebox.showinfo("Success", f"Added trusted path: {path}")
            else:
                messagebox.showwarning("Duplicate", "This path is already in the trusted list.")
    
    def remove_trusted_path(self):
        selection = self.paths_listbox.curselection()
        if selection:
            path = self.paths_listbox.get(selection[0])
            if messagebox.askyesno("Confirm", f"Remove trusted path:\n{path}"):
                self.paths_listbox.delete(selection[0])
                messagebox.showinfo("Success", "Trusted path removed.")
        else:
            messagebox.showwarning("No Selection", "Please select a path to remove.")
    
    def save_settings(self):
        try:
            # Save API keys to .env
            self._save_env_file()
            
            # Update config
            if 'detection' not in self.config:
                self.config['detection'] = {}
            self.config['detection']['threat_threshold'] = self.threat_threshold.get()
            self.config['detection']['terminate_threshold'] = self.terminate_threshold.get()
            
            # Save trusted paths
            if 'paths' not in self.config:
                self.config['paths'] = {}
            self.config['paths']['trusted_paths'] = list(self.paths_listbox.get(0, tk.END))
            
            if 'expert_system' not in self.config:
                self.config['expert_system'] = {'weights': {}}
            if 'weights' not in self.config['expert_system']:
                self.config['expert_system']['weights'] = {}
            
            self.config['expert_system']['weights']['yara'] = round(self.yara_weight.get(), 1)
            self.config['expert_system']['weights']['virustotal'] = round(self.vt_weight.get(), 1)
            self.config['expert_system']['weights']['behavioral'] = round(self.behavior_weight.get(), 1)
            self.config['expert_system']['weights']['mitre'] = round(self.mitre_weight.get(), 1)
            self.config['expert_system']['enabled'] = self.expert_enabled.get()
            
            if 'yara' not in self.config:
                self.config['yara'] = {}
            self.config['yara']['enabled'] = self.yara_enabled.get()
            
            if 'langgraph' not in self.config:
                self.config['langgraph'] = {}
            self.config['langgraph']['enabled'] = self.langgraph_enabled.get()
            
            # Save to file
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            messagebox.showinfo("Success", "Settings saved successfully!\nRestart the application for changes to take effect.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_defaults(self):
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            self.threat_threshold.set(5)
            self.terminate_threshold.set(8)
            self.yara_weight.set(3.0)
            self.vt_weight.set(2.5)
            self.behavior_weight.set(1.5)
            self.mitre_weight.set(2.0)
            self.yara_enabled.set(True)
            self.expert_enabled.set(True)
            self.langgraph_enabled.set(False)
    
    def toggle_autoscan(self):
        if not self.auto_scanner:
            return
        
        if self.autoscan_enabled.get():
            self.auto_scanner.interval = self.scan_interval.get() * 60
            self.auto_scanner.start()
            messagebox.showinfo("Auto-Scan", f"Auto-scan started (every {self.scan_interval.get()} minutes)")
        else:
            self.auto_scanner.stop()
            messagebox.showinfo("Auto-Scan", "Auto-scan stopped")
    
    def get_frame(self):
        return self.frame
