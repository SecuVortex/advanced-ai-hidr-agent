import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.detection_agent import DetectionAgent
from agents.intelligence_agent import IntelligenceAgent
from agents.response_agent import ResponseAgent
from agents.analyst_agent import AnalystAgent
from agents.coordinator_agent import CoordinatorAgent
from tools.security_tools import SecurityTools
from tools.process_tools import ProcessTools


class TestDetectionAgent(unittest.TestCase):

    def setUp(self):
        self.agent = DetectionAgent()

    def test_suspicious_process_detection(self):
        result = self.agent.analyze_process('ransomware.exe',
            'C:\\temp\\ransomware.exe', 'ransomware.exe --encrypt', 1234)
        self.assertTrue(result['is_suspicious'])
        self.assertGreater(result['threat_level'], 5)
        self.assertIn('recommendation', result)

    def test_normal_process_detection(self):
        result = self.agent.analyze_process('notepad.exe',
            'C:\\Windows\\System32\\notepad.exe', 'notepad.exe', 5678)
        self.assertFalse(result['is_suspicious'])
        self.assertLess(result['threat_level'], 3)

    def test_file_analysis(self):
        test_file = Path(__file__).parent / 'test_file.txt'
        test_file.write_text('test content')
        try:
            result = self.agent.analyze_file(str(test_file))
            self.assertIn('file_hash', result)
            self.assertIn('is_modified', result)
            self.assertIsNotNone(result['file_hash'])
        finally:
            if test_file.exists():
                test_file.unlink()


class TestIntelligenceAgent(unittest.TestCase):

    def setUp(self):
        self.agent = IntelligenceAgent()

    @patch('tools.virustotal_tool.requests.get')
    def test_virustotal_query(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'attributes': {
            'last_analysis_stats': {'malicious': 45, 'suspicious': 10,
            'harmless': 5, 'undetected': 0}}}}
        mock_get.return_value = mock_response
        result = self.agent.enrich_file_analysis('abc123')
        self.assertIn('virustotal', result)
        self.assertIn('threat_score', result)
        self.assertTrue(result['is_known_malware'])

    def test_threat_context(self):
        context = self.agent.get_threat_context('ransomware')
        self.assertIsInstance(context, str)
        self.assertIn('encryption', context.lower())


class TestResponseAgent(unittest.TestCase):

    def setUp(self):
        self.agent = ResponseAgent(quarantine_dir='./test_quarantine')

    def test_allow_action(self):
        result = self.agent.execute_action('allow', {})
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'allow')

    def test_monitor_action(self):
        result = self.agent.execute_action('monitor', {})
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'monitor')

    @patch('tools.process_tools.ProcessTools.terminate_process')
    def test_terminate_temporary(self, mock_terminate):
        mock_terminate.return_value = True
        result = self.agent.execute_action('terminate_temporary', {'pid': 1234}
            )
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'terminate_temporary')
        mock_terminate.assert_called_once()


class TestAnalystAgent(unittest.TestCase):

    def setUp(self):
        self.agent = AnalystAgent()

    def test_fallback_analysis(self):
        detection = {'threat_level': 8, 'is_suspicious': True, 'reasons': [
            'Malicious name', 'Temp directory']}
        intelligence = {'is_known_malware': True, 'virustotal': {
            'malicious': 45}}
        result = self.agent._fallback_analysis(detection, intelligence)
        self.assertIsInstance(result, str)
        self.assertIn('CRITICAL', result)

    def test_severity_determination(self):
        critical_analysis = (
            'This is a CRITICAL threat that requires immediate action')
        severity = self.agent.llm_tools.determine_severity(critical_analysis)
        self.assertEqual(severity, 'Critical')


class TestCoordinatorAgent(unittest.TestCase):

    def setUp(self):
        self.agent = CoordinatorAgent()

    def test_priority_calculation(self):
        detection = {'threat_level': 8}
        intelligence = {'is_known_malware': True}
        analysis = {'severity': 'Critical'}
        priority = self.agent._calculate_priority(detection, intelligence,
            analysis)
        self.assertEqual(priority, 'Critical')

    def test_action_conflict_resolution(self):
        detection = {'recommendation': 'terminate_temporary'}
        intelligence = {'recommendation': 'quarantine', 'is_known_malware':
            True}
        analysis = {}
        action = self.agent._resolve_action_conflicts(detection,
            intelligence, analysis)
        self.assertEqual(action, 'terminate_permanent')

    def test_human_approval_requirement(self):
        requires = self.agent._requires_human_approval('Critical',
            'terminate_permanent')
        self.assertTrue(requires)


class TestSecurityTools(unittest.TestCase):

    def test_file_hash_calculation(self):
        test_file = Path(__file__).parent / 'test_hash.txt'
        test_file.write_text('test content for hashing')
        try:
            hash_result = SecurityTools.calculate_file_hash(str(test_file))
            self.assertIsNotNone(hash_result)
            self.assertEqual(len(hash_result), 64)
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_suspicious_path_detection(self):
        self.assertTrue(SecurityTools.is_suspicious_path(
            'C:\\temp\\malware.exe'))
        self.assertTrue(SecurityTools.is_suspicious_path(
            'C:\\Users\\test\\Downloads\\file.exe'))
        self.assertFalse(SecurityTools.is_suspicious_path(
            'C:\\Windows\\System32\\notepad.exe'))

    def test_suspicious_name_detection(self):
        self.assertTrue(SecurityTools.is_suspicious_name('ransomware.exe'))
        self.assertTrue(SecurityTools.is_suspicious_name('keylogger.exe'))
        self.assertFalse(SecurityTools.is_suspicious_name('notepad.exe'))

    def test_threat_score_calculation(self):
        indicators = {'suspicious_path': True, 'suspicious_name': True,
            'encoded_command': True}
        score = SecurityTools.calculate_threat_score(indicators)
        self.assertGreater(score, 5)
        self.assertLessEqual(score, 10)


class TestProcessTools(unittest.TestCase):

    @patch('psutil.Process')
    def test_get_process_info(self, mock_process):
        mock_proc = Mock()
        mock_proc.name.return_value = 'test.exe'
        mock_proc.exe.return_value = 'C:\\test\\test.exe'
        mock_proc.cmdline.return_value = ['test.exe', '--arg']
        mock_proc.status.return_value = 'running'
        mock_proc.cpu_percent.return_value = 5.0
        mock_proc.memory_info.return_value = Mock(rss=1024 * 1024 * 100)
        mock_proc.num_threads.return_value = 4
        mock_proc.create_time.return_value = 1234567890.0
        mock_process.return_value = mock_proc
        result = ProcessTools.get_process_info(1234)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'test.exe')
        self.assertEqual(result['pid'], 1234)


def run_tests():
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
