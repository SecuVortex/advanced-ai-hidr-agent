"""
Behavioral Analysis - Monitor Process Actions
Detects suspicious behavior patterns in real-time
"""
import psutil
from typing import Dict, List

class BehaviorMonitor:
    """Monitor and analyze process behavior"""
    
    def __init__(self):
        self.suspicious_behaviors = []
    
    def analyze_process_behavior(self, pid: int, proc_name: str, path: str, cmdline: str) -> Dict:
        """Analyze process behavior for suspicious patterns"""
        behaviors = []
        threat_score = 0
        
        try:
            proc = psutil.Process(pid)
            
            # 1. Network connections (RAT indicator)
            connections = proc.connections()
            if connections:
                external_conns = [c for c in connections if c.status == 'ESTABLISHED']
                if external_conns:
                    behaviors.append(f"Active network connections: {len(external_conns)}")
                    threat_score += 2
            
            # 2. Memory usage (crypto-miner indicator)
            mem_info = proc.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            if mem_mb > 500:  # High memory usage
                behaviors.append(f"High memory usage: {mem_mb:.0f}MB")
                threat_score += 1
            
            # 3. CPU usage (crypto-miner indicator)
            cpu_percent = proc.cpu_percent(interval=0.1)
            if cpu_percent > 50:
                behaviors.append(f"High CPU usage: {cpu_percent:.0f}%")
                threat_score += 2
            
            # 4. Child processes (process injection)
            children = proc.children()
            if len(children) > 3:
                behaviors.append(f"Multiple child processes: {len(children)}")
                threat_score += 1
            
            # 5. Open files (ransomware indicator)
            try:
                open_files = proc.open_files()
                if len(open_files) > 10:
                    behaviors.append(f"Many open files: {len(open_files)}")
                    threat_score += 2
            except:
                pass
            
            # 6. Command line analysis
            if any(flag in cmdline.lower() for flag in ['-hidden', '-windowstyle hidden', '/silent']):
                behaviors.append("Hidden execution flags")
                threat_score += 3
            
            if 'invoke-expression' in cmdline.lower() or 'iex' in cmdline.lower():
                behaviors.append("PowerShell code execution")
                threat_score += 3
            
            # 7. Parent process check (suspicious parent)
            try:
                parent = proc.parent()
                if parent:
                    parent_name = parent.name().lower()
                    if parent_name in ['cmd.exe', 'powershell.exe', 'wscript.exe']:
                        behaviors.append(f"Suspicious parent: {parent_name}")
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
    
    def get_network_indicators(self, pid: int) -> List[str]:
        """Get network connection details"""
        indicators = []
        try:
            proc = psutil.Process(pid)
            for conn in proc.connections():
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    indicators.append(f"{conn.raddr.ip}:{conn.raddr.port}")
        except:
            pass
        return indicators
