from typing import Dict, Any
from agents.base_agent import BaseAgent
from tools.security_tools import SecurityTools
from tools.process_tools import ProcessTools
from agents.config import Config


class DetectionAgent(BaseAgent):

    def __init__(self):
        super().__init__(name='DetectionAgent', role=
            'Threat Detection Specialist')

    def analyze(self, data: Dict[str, Any]) ->Dict[str, Any]:
        event_type = data.get('event_type')
        if event_type == 'process':
            return self.analyze_process(data['name'], data['path'], data[
                'cmdline'], data['pid'])
        elif event_type == 'file':
            return self.analyze_file(data['filepath'], data.get('old_hash'))
        else:
            return {'error': f'Unsupported event type: {event_type}'}

    def analyze_process(self, proc_name: str, path: str, cmdline: str, pid: int
        ) ->Dict[str, Any]:
        self.log_info(f'Analyzing process: {proc_name} (PID: {pid})')
        reasons = []
        indicators = {}
        if SecurityTools.is_suspicious_name(proc_name):
            reasons.append(f"Suspicious process name: '{proc_name}'")
            indicators['suspicious_name'] = True
        if SecurityTools.is_suspicious_path(path):
            reasons.append(f"Process running from suspicious path: '{path}'")
            indicators['suspicious_path'] = True
        if SecurityTools.is_encoded_command(cmdline):
            reasons.append('Process has encoded command-line arguments')
            indicators['encoded_command'] = True
        threat_level = SecurityTools.calculate_threat_score(indicators)
        is_suspicious = threat_level >= 3
        if is_suspicious:
            self.log_warning(
                f'Suspicious process detected: {proc_name} (Threat: {threat_level}/10)'
                )
        return {'agent': self.name, 'process_name': proc_name, 'path': path,
            'pid': pid, 'is_suspicious': is_suspicious, 'threat_level':
            threat_level, 'reasons': reasons, 'recommendation': self.
            _get_recommendation(threat_level), 'file_hash': SecurityTools.
            calculate_file_hash(path)}

    def analyze_file(self, filepath: str, old_hash: str=None) ->Dict[str, Any]:
        self.log_info(f'Analyzing file: {filepath}')
        current_hash = SecurityTools.calculate_file_hash(filepath)
        is_modified = old_hash is not None and current_hash != old_hash
        if is_modified:
            self.log_warning(f'File integrity compromised: {filepath}')
        return {'agent': self.name, 'filepath': filepath, 'file_hash':
            current_hash, 'is_modified': is_modified}

    def _get_recommendation(self, threat_level: int) ->str:
        if threat_level >= 8:
            return 'terminate_permanent'
        elif threat_level >= 5:
            return 'terminate_temporary'
        elif threat_level >= 3:
            return 'monitor'
        else:
            return 'allow'
