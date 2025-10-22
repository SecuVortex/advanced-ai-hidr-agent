"""
File System Tools
Provides file operations including quarantine and backup.
"""

import shutil
import time
from pathlib import Path
from typing import Optional


class FileTools:
    """File system operations"""
    
    @staticmethod
    def quarantine_file(filepath: str, quarantine_dir: str) -> Optional[str]:
        """
        Move file to quarantine
        
        Args:
            filepath: Path to file to quarantine
            quarantine_dir: Quarantine directory path
            
        Returns:
            Path to quarantined file or None on error
        """
        try:
            Path(quarantine_dir).mkdir(exist_ok=True, parents=True)
            
            source = Path(filepath)
            if not source.exists():
                return None
            
            # Create unique quarantine filename
            timestamp = int(time.time())
            quar_name = f"{source.name}.{timestamp}.quar"
            quar_path = Path(quarantine_dir) / quar_name
            
            # Move file to quarantine
            shutil.move(str(source), str(quar_path))
            
            return str(quar_path)
        except Exception as e:
            return None
    
    @staticmethod
    def backup_file(filepath: str, backup_dir: str) -> Optional[str]:
        """
        Create backup of file
        
        Args:
            filepath: Path to file to backup
            backup_dir: Backup directory path
            
        Returns:
            Path to backup file or None on error
        """
        try:
            Path(backup_dir).mkdir(exist_ok=True, parents=True)
            
            source = Path(filepath)
            if not source.exists():
                return None
            
            # Preserve directory structure in backup
            backup_path = Path(backup_dir) / source.name
            backup_path.parent.mkdir(exist_ok=True, parents=True)
            
            shutil.copy2(str(source), str(backup_path))
            
            return str(backup_path)
        except Exception as e:
            return None
    
    @staticmethod
    def restore_file(backup_path: str, target_path: str) -> bool:
        """
        Restore file from backup
        
        Args:
            backup_path: Path to backup file
            target_path: Target restore path
            
        Returns:
            True if successful
        """
        try:
            backup = Path(backup_path)
            target = Path(target_path)
            
            if not backup.exists():
                return False
            
            target.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy2(str(backup), str(target))
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_info(filepath: str) -> Optional[dict]:
        """
        Get file information
        
        Args:
            filepath: Path to file
            
        Returns:
            Dictionary with file info or None
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": path.suffix,
                "is_executable": path.suffix.lower() in ['.exe', '.dll', '.sys', '.bat', '.cmd', '.ps1']
            }
        except Exception:
            return None
