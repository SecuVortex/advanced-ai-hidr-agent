import os
import time
import shutil
import subprocess
import threading
import random
import string
from pathlib import Path
import argparse


class AdvancedAttackSimulator:

    def __init__(self):
        self.watched_dir = Path.cwd() / 'watched'
        self.temp_dir = Path.cwd() / 'temp_attack'
        self.temp_dir.mkdir(exist_ok=True)

    def simulate_ransomware_attack(self):
        print('Executing ransomware simulation...')
        if not self.watched_dir.exists():
            print('Watched directory not found. Run monitor.py first.')
            return
        decoys_dir = self.watched_dir / 'decoys'
        for decoy_file in decoys_dir.glob('*'):
            if decoy_file.is_file():
                print(f'Encrypting {decoy_file.name}...')
                content = decoy_file.read_bytes()
                encrypted = bytearray()
                for byte in content:
                    encrypted.append(byte ^ 170)
                decoy_file.write_bytes(encrypted)
                time.sleep(0.5)
        ransom_note = self.watched_dir / 'README_RANSOM.txt'
        ransom_note.write_text(
            'Your files have been encrypted! To get them back, send 0.1 BTC to address XYZ.'
            )
        print('Ransom note created.')

    def simulate_suspicious_process(self):
        print('Simulating suspicious process execution...')
        suspicious_script = self.temp_dir / 'suspicious_script.bat'
        suspicious_content = """
@echo off
echo Running suspicious commands...
whoami
net user
ping -n 5 8.8.8.8
tasklist
"""
        suspicious_script.write_text(suspicious_content)
        try:
            subprocess.Popen(str(suspicious_script), shell=True)
            print('Suspicious script launched in temp directory.')
        except Exception as e:
            print(f'Failed to launch suspicious script: {e}')

    def simulate_powershell_attack(self):
        print('Simulating PowerShell attack...')
        encoded_command = (
            'powershell.exe -EncodedCommand VwByAGkAdABlAC0ASABvAHMAdAAgACcASABlAGwAbABvACwAIABXAG8AcgBsAGQAIQAJw=='
            )
        try:
            subprocess.Popen(encoded_command, shell=True)
            print('Encoded PowerShell command executed.')
        except Exception as e:
            print(f'PowerShell attack failed: {e}')

    def simulate_file_deletion(self):
        print('Simulating critical file deletion...')
        critical_file = self.watched_dir / 'important_document.txt'
        if critical_file.exists():
            critical_file.unlink()
            print(f'Deleted: {critical_file.name}')
        else:
            print('Critical file not found for deletion test.')

    def simulate_multi_stage_attack(self):
        print('Executing multi-stage attack...')
        self.simulate_suspicious_process()
        time.sleep(5)
        self.simulate_powershell_attack()
        time.sleep(5)
        self.simulate_file_deletion()
        time.sleep(5)
        self.simulate_ransomware_attack()

    def cleanup(self):
        print('Cleaning up attack simulation files...')
        shutil.rmtree(self.temp_dir)
        ransom_note = self.watched_dir / 'README_RANSOM.txt'
        if ransom_note.exists():
            ransom_note.unlink()
        print('Cleanup complete.')


def main():
    parser = argparse.ArgumentParser(description=
        'Advanced Attack Simulator for HIDR Agent')
    parser.add_argument('--full', action='store_true', help=
        'Run a full, multi-stage attack')
    args = parser.parse_args()
    simulator = AdvancedAttackSimulator()
    if args.full:
        simulator.simulate_multi_stage_attack()
    else:
        simulator.simulate_ransomware_attack()
        time.sleep(2)
        simulator.simulate_suspicious_process()
    time.sleep(5)
    simulator.cleanup()


if __name__ == '__main__':
    main()
