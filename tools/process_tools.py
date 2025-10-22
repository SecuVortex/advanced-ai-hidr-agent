import psutil
from typing import Optional, Dict, Any


class ProcessTools:

    @staticmethod
    def get_process_info(pid: int) ->Optional[Dict[str, Any]]:
        try:
            proc = psutil.Process(pid)
            return {'pid': pid, 'name': proc.name(), 'exe': proc.exe(),
                'cmdline': ' '.join(proc.cmdline()), 'status': proc.status(
                ), 'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_mb': round(proc.memory_info().rss / 1024 / 1024, 2),
                'num_threads': proc.num_threads(), 'create_time': proc.
                create_time(), 'username': proc.username() if hasattr(proc,
                'username') else None}
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            return None

    @staticmethod
    def terminate_process(pid: int, timeout: int=3) ->bool:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=timeout)
            return True
        except (psutil.NoSuchProcess, psutil.TimeoutExpired, psutil.
            AccessDenied):
            return False

    @staticmethod
    def kill_process(pid: int) ->bool:
        try:
            proc = psutil.Process(pid)
            proc.kill()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    @staticmethod
    def is_process_running(pid: int) ->bool:
        try:
            proc = psutil.Process(pid)
            return proc.is_running()
        except psutil.NoSuchProcess:
            return False

    @staticmethod
    def get_process_children(pid: int) ->list:
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)
            return [child.pid for child in children]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return []

    @staticmethod
    def suspend_process(pid: int) ->bool:
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    @staticmethod
    def resume_process(pid: int) ->bool:
        try:
            proc = psutil.Process(pid)
            proc.resume()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
