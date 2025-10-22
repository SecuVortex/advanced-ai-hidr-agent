import os
import time
import shutil
import subprocess
import threading
import random
import string
from pathlib import Path

class AdvancedAttackSimulator:
    def __init__(self):
        self.watched_dir = Path.cwd() / "watched"
        self.temp_dir = Path.cwd() / "temp_attack"
        self.temp_dir.mkdir(exist_ok=True)
        
    def simulate_ransomware_attack(self):
        print("Executing ransomware simulation...")
        
        if not self.watched_dir.exists():
            print("Watched directory not found. Run monitor.py first.")
            return
        
        decoys_dir = self.watched_dir / "decoys"
        
        for decoy_file in decoys_dir.glob("*"):
            if decoy_file.is_file():
                print(f"Encrypting {decoy_file.name}...")
                content = decoy_file.read_bytes()
                
                encrypted = bytearray()
                for byte in content:
                    encrypted.append(byte ^ 0xAA)
                
                decoy_file.write_bytes(encrypted)
                time.sleep(0.5)
        
        ransom_note = self.watched_dir / "README_RANSOM.txt"
        ransom_note.write_text("""
YOUR FILES HAVE BEEN ENCRYPTED!
All your important files have been encrypted with military-grade encryption.
To recover your files, you must pay 0.5 BTC to the following address:
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
Contact: darkweb@encrypted.onion
        """)
        
        for i in range(5):
            fake_encrypted = self.watched_dir / f"important_file_{i}.encrypted"
            fake_encrypted.write_text(f"ENCRYPTED_DATA_{random.randint(1000, 9999)}")
            time.sleep(0.2)
    
    def simulate_process_injection(self):
        print("Simulating process injection attack...")
        
        suspicious_names = [
            "encryptor.exe", "locker.exe", "crypt.exe", "ransomware.exe",
            "keylogger.exe", "stealer.exe", "backdoor.exe", "trojan.exe"
        ]
        
        for name in suspicious_names[:3]:
            try:
                suspicious_exe = self.temp_dir / name
                shutil.copy("C:\\Windows\\System32\\notepad.exe", suspicious_exe)
                
                print(f"Launching suspicious process: {name}")
                subprocess.Popen([str(suspicious_exe)], cwd=self.temp_dir)
                time.sleep(1)
            except Exception as e:
                print(f"Failed to create {name}: {e}")
    
    def simulate_powershell_attack(self):
        print("Simulating PowerShell encoded command attack...")
        
        encoded_commands = [
            "SQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0AA==",
            "RwBlAHQALQBQAHIAbwBjAGUAcwBzAA==",
            "UwB0AGEAcgB0AC0AUAByAG8AYwBlAHMAcwA="
        ]
        
        for cmd in encoded_commands:
            try:
                print(f"Executing encoded PowerShell command...")
                subprocess.Popen([
                    "powershell.exe", "-EncodedCommand", cmd, "-WindowStyle", "Hidden"
                ], cwd=self.temp_dir)
                time.sleep(2)
            except Exception as e:
                print(f"PowerShell attack failed: {e}")
    
    def simulate_file_deletion_spree(self):
        print("Simulating mass file deletion...")
        
        for i in range(10):
            temp_file = self.watched_dir / f"temp_file_{i}.txt"
            temp_file.write_text(f"Temporary file {i}")
            time.sleep(0.1)
        
        time.sleep(1)
        
        for i in range(10):
            temp_file = self.watched_dir / f"temp_file_{i}.txt"
            if temp_file.exists():
                temp_file.unlink()
                time.sleep(0.1)
    
    def simulate_registry_modification(self):
        print("Simulating registry modification attack...")
        
        try:
            reg_commands = [
                'reg add "HKCU\\Software\\TestMalware" /v "Persistence" /t REG_SZ /d "C:\\temp\\malware.exe" /f',
                'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "TestPersistence" /t REG_SZ /d "C:\\temp\\backdoor.exe" /f'
            ]
            
            for cmd in reg_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True)
                    print(f"Registry modification attempted")
                    time.sleep(1)
                except Exception:
                    pass
        except Exception as e:
            print(f"Registry attack failed: {e}")
    
    def simulate_network_scanning(self):
        print("Simulating network reconnaissance...")
        
        try:
            scan_commands = [
                "netstat -an",
                "arp -a",
                "ipconfig /all",
                "net user",
                "net localgroup administrators"
            ]
            
            for cmd in scan_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                    print(f"Network scan: {cmd}")
                    time.sleep(1)
                except Exception:
                    pass
        except Exception as e:
            print(f"Network scanning failed: {e}")
    
    def simulate_credential_harvesting(self):
        print("Simulating credential harvesting...")
        
        fake_creds_file = self.temp_dir / "harvested_creds.txt"
        fake_creds = """
Harvested Credentials:
Username: admin
Password: password123
Domain: WORKGROUP
Browser Cookies: 247 entries
Saved Passwords: 15 entries
        """
        fake_creds_file.write_text(fake_creds)
        
        keylog_file = self.temp_dir / "keylog.txt"
        keylog_data = "".join(random.choices(string.ascii_letters + string.digits, k=500))
        keylog_file.write_text(keylog_data)
    
    def simulate_lateral_movement(self):
        print("Simulating lateral movement...")
        
        try:
            movement_commands = [
                "net view",
                "ping 192.168.1.1",
                "nslookup google.com",
                "telnet 127.0.0.1 80"
            ]
            
            for cmd in movement_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=3)
                    print(f"Lateral movement: {cmd}")
                    time.sleep(1)
                except Exception:
                    pass
        except Exception as e:
            print(f"Lateral movement failed: {e}")
    
    def simulate_data_exfiltration(self):
        print("Simulating data exfiltration...")
        
        exfil_dir = self.temp_dir / "exfiltrated_data"
        exfil_dir.mkdir(exist_ok=True)
        
        fake_data_files = [
            "customer_database.sql", "financial_records.xlsx", 
            "employee_data.csv", "trade_secrets.docx", "passwords.txt"
        ]
        
        for filename in fake_data_files:
            fake_file = exfil_dir / filename
            fake_content = f"SENSITIVE DATA - {filename}\n" + "X" * 1000
            fake_file.write_text(fake_content)
            print(f"Exfiltrated: {filename}")
            time.sleep(0.5)
    
    def simulate_persistence_mechanism(self):
        print("Simulating persistence mechanisms...")
        
        try:
            persistence_file = Path.cwd() / "startup_malware.bat"
            persistence_content = """
@echo off
echo Malware persistence activated
start /min notepad.exe
            """
            persistence_file.write_text(persistence_content)
            
            scheduled_task_cmd = f'schtasks /create /tn "SystemUpdate" /tr "{persistence_file}" /sc onlogon /f'
            try:
                subprocess.run(scheduled_task_cmd, shell=True, capture_output=True)
                print("Scheduled task persistence created")
            except Exception:
                pass
                
        except Exception as e:
            print(f"Persistence mechanism failed: {e}")
    
    def run_full_attack_chain(self):
        print("=== ADVANCED ATTACK SIMULATION STARTED ===")
        print("Simulating multi-stage cyber attack...")
        
        attack_stages = [
            ("Initial Reconnaissance", self.simulate_network_scanning),
            ("Process Injection", self.simulate_process_injection),
            ("PowerShell Attack", self.simulate_powershell_attack),
            ("Credential Harvesting", self.simulate_credential_harvesting),
            ("Lateral Movement", self.simulate_lateral_movement),
            ("File System Attack", self.simulate_ransomware_attack),
            ("Mass File Deletion", self.simulate_file_deletion_spree),
            ("Data Exfiltration", self.simulate_data_exfiltration),
            ("Persistence", self.simulate_persistence_mechanism),
            ("Registry Modification", self.simulate_registry_modification)
        ]
        
        for stage_name, stage_func in attack_stages:
            print(f"\n--- {stage_name} ---")
            try:
                stage_func()
            except Exception as e:
                print(f"Stage failed: {e}")
            time.sleep(2)
        
        print("\n=== ATTACK SIMULATION COMPLETE ===")
        print("Check HIDR Agent for detection results")
    
    def cleanup(self):
        print("Cleaning up attack artifacts...")
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            
            cleanup_files = [
                "startup_malware.bat", "encryptor.exe", "locker.exe", 
                "crypt.exe", "ransomware.exe"
            ]
            
            for filename in cleanup_files:
                file_path = Path.cwd() / filename
                if file_path.exists():
                    file_path.unlink()
            
            try:
                subprocess.run('schtasks /delete /tn "SystemUpdate" /f', shell=True, capture_output=True)
                subprocess.run('reg delete "HKCU\\Software\\TestMalware" /f', shell=True, capture_output=True)
                subprocess.run('reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "TestPersistence" /f', shell=True, capture_output=True)
            except Exception:
                pass
                
        except Exception as e:
            print(f"Cleanup failed: {e}")

def run_quick_test():
    simulator = AdvancedAttackSimulator()
    
    print("=== QUICK ATTACK TEST ===")
    simulator.simulate_ransomware_attack()
    time.sleep(1)
    simulator.simulate_process_injection()
    time.sleep(1)
    simulator.simulate_powershell_attack()
    
    print("\nQuick test complete")

def run_full_test():
    simulator = AdvancedAttackSimulator()
    
    try:
        simulator.run_full_attack_chain()
    finally:
        time.sleep(5)
        simulator.cleanup()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        run_full_test()
    else:
        run_quick_test()