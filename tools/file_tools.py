import shutil
import time
from pathlib import Path
from typing import Optional


class FileTools:

    def quarantine_file(self, filepath: str, quarantine_dir: str) ->Optional[
        str]:
        try:
            source = Path(filepath)
            if not source.exists():
                return None
            quarantine_path = Path(quarantine_dir)
            quarantine_path.mkdir(exist_ok=True)
            dest_name = f'{source.name}_{int(time.time())}.quarantined'
            destination = quarantine_path / dest_name
            shutil.move(str(source), str(destination))
            return str(destination)
        except Exception as e:
            print(f'Error quarantining file: {e}')
            return None

    def create_backup(self, filepath: str, backup_dir: str) ->Optional[str]:
        try:
            source = Path(filepath)
            if not source.exists():
                return None
            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)
            dest_name = f'{source.name}_{int(time.time())}.bak'
            destination = backup_path / dest_name
            shutil.copy2(str(source), str(destination))
            return str(destination)
        except Exception as e:
            print(f'Error creating backup: {e}')
            return None

    def restore_from_backup(self, backup_path: str, target_path: str) ->bool:
        try:
            source = Path(backup_path)
            if not source.exists():
                return False
            shutil.copy2(str(source), str(target_path))
            return True
        except Exception as e:
            print(f'Error restoring backup: {e}')
            return False

    def get_file_info(self, filepath: str) ->Optional[dict]:
        try:
            p = Path(filepath)
            if not p.exists():
                return None
            stat = p.stat()
            return {'size': stat.st_size, 'created': stat.st_ctime,
                'modified': stat.st_mtime, 'accessed': stat.st_atime}
        except Exception as e:
            print(f'Error getting file info: {e}')
            return None
