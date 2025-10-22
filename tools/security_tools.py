"""
Core Security Tools
Provides fundamental security operations for the HIDR system.
"""

import hashlib
from pathlib import Path
from typing import Optional


class SecurityTools:
    """Core security operations"""
    
    @staticmethod
    def calculate_file_hash(filepath: str, algorithm: str = "sha256") -> Optional[str]:
        """
        Calculate file hash
        
        Args:
            filepath: Path to file
            algorithm: Hash algorithm (sha256, md5, sha1)
            
        Returns:
            File hash or None on error
        """
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            return None
    
    @staticmethod
    def is_suspicious_path(path: str) -> bool:
        """
        Check if file path is suspicious
        
        Args:
            path: File path to check
            
        Returns:
            True if path is suspicious
        """
        path_lower = path.lower()
        suspicious_locations = [
            "temp",
            "tmp",
            "downloads",
            "appdata\\local\\temp",
            "recycler",
            "$recycle.bin"
        ]
        return any(loc in path_lower for loc in suspicious_locations)
    
    @staticmethod
    def is_suspicious_name(name: str) -> bool:
        """
        Check if process/file name is suspicious
        
        Args:
            name: Process or file name
            
        Returns:
            True if name is suspicious
        """
        name_lower = name.lower()
        suspicious_names = [
            "encryptor", "locker", "crypt", "ransomware",
            "keylogger", "stealer", "backdoor", "trojan",
            "malware", "virus", "worm", "rootkit"
        ]
        return any(sus in name_lower for sus in suspicious_names)

    @staticmethod
    def is_encoded_command(cmdline: str) -> bool:
        """
        Check for encoded PowerShell commands

        Args:
            cmdline: Command line string

        Returns:
            True if encoded command is detected
        """
        return "powershell" in cmdline.lower() and "-enc" in cmdline.lower()
    
    @staticmethod
    def calculate_threat_score(indicators: dict) -> int:
        """
        Calculate threat score based on indicators
        
        Args:
            indicators: Dictionary of threat indicators
            
        Returns:
            Threat score (0-10)
        """
        score = 0
        
        # Path-based scoring
        if indicators.get("suspicious_path"):
            score += 2
        
        # Name-based scoring
        if indicators.get("suspicious_name"):
            score += 5
        
        # Behavior-based scoring
        if indicators.get("encoded_command"):
            score += 2
        
        if indicators.get("mass_file_operations"):
            score += 3
        
        if indicators.get("registry_modification"):
            score += 1
        
        if indicators.get("network_activity"):
            score += 1
        
        return min(score, 10)  # Cap at 10
