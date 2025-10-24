"""Behavioral Analysis Module"""
import psutil
from typing import Dict, List

class BehaviorMonitor:
    def __init__(self):
        self.suspicious_behaviors = []
    
    def analyze_process_behavior(self, pid: int, proc_name: str, path: str, cmdline: str) -> Dict:
        behaviors = []
        threat_score = 0
        
        try:
            proc = psutil.Process(pid)
            
            connections = proc.connections()
            if connections:
                external_conns = [c for c in connections if c.status == 'ESTABLISHED']
                if external_conns:
                    behaviors.append(f"Network: {len(external_conns)} connections")
                    threat_score += 2
            
            mem_info = proc.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            if mem_mb > 500:
                behaviors.append(f"Memory: {mem_mb:.0f}MB")
                threat_score += 1
            
            cpu_percent = proc.cpu_percent(interval=0.1)
            if cpu_percent > 50:
                behaviors.append(f"CPU: {cpu_percent:.0f}%")
                threat_score += 2
            
            children = proc.children()
            if len(children) > 3:
                behaviors.append(f"Children: {len(children)}")
                threat_score += 1
            
            try:
                open_files = proc.open_files()
                if len(open_files) > 10:
                    behaviors.append(f"Files: {len(open_files)}")
                    threat_score += 2
            except:
                pass
            
            if any(flag in cmdline.lower() for flag in ['-hidden', '-windowstyle hidden', '/silent']):
                behaviors.append("Hidden execution")
                threat_score += 3
            
            if 'invoke-expression' in cmdline.lower() or 'iex' in cmdline.lower():
                behaviors.append("PowerShell execution")
                threat_score += 3
            
            try:
                parent = proc.parent()
                if parent:
                    parent_name = parent.name().lower()
                    if parent_name in ['cmd.exe', 'powershell.exe', 'wscript.exe']:
                        behaviors.append(f"Parent: {parent_name}")
                        threat_score += 2
            except:
                pass
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return {
            'behaviors': behaviors,
            'behavior_threat_score': min(threat_score, 10),
            'is_suspicious': threat_score >= 5
        }
