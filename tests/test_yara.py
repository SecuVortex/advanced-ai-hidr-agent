"""Tests for YARA scanner"""
import pytest
from pathlib import Path
from core.yara_scanner import YaraScanner

class TestYaraScanner:
    """Test YARA scanner functionality"""
    
    def test_init(self):
        """Test YARA scanner initialization"""
        scanner = YaraScanner('yara_rules')
        assert scanner is not None
        assert scanner.rules_dir == Path('yara_rules')
    
    def test_load_rules(self):
        """Test loading YARA rules"""
        scanner = YaraScanner('yara_rules')
        info = scanner.get_rules_info()
        assert 'rules_count' in info
        assert info['rules_count'] > 0
    
    def test_scan_nonexistent_file(self):
        """Test scanning non-existent file"""
        scanner = YaraScanner('yara_rules')
        result = scanner.scan_file('nonexistent.exe')
        assert result['matches'] == []
        assert result['threat_score'] == 0
    
    def test_scan_eicar(self, tmp_path, eicar_string):
        """Test EICAR detection"""
        scanner = YaraScanner('yara_rules')
        
        # Create EICAR file
        eicar_file = tmp_path / "eicar.txt"
        eicar_file.write_text(eicar_string)
        
        result = scanner.scan_file(str(eicar_file))
        assert isinstance(result, dict)
        assert 'matches' in result
        assert 'threat_score' in result
    
    def test_threat_score_calculation(self):
        """Test threat score calculation"""
        scanner = YaraScanner('yara_rules')
        
        # Mock matches
        matches = [
            {'rule': 'test1', 'severity': 'high'},
            {'rule': 'test2', 'severity': 'medium'}
        ]
        
        score = scanner._calculate_threat_score(matches)
        assert isinstance(score, (int, float))
        assert 0 <= score <= 10
    
    def test_get_rules_info(self):
        """Test getting rules information"""
        scanner = YaraScanner('yara_rules')
        info = scanner.get_rules_info()
        
        assert 'rules_count' in info
        assert isinstance(info['rules_count'], int)
        assert info['rules_count'] > 0
    
    def test_scan_timeout(self):
        """Test scan timeout handling"""
        scanner = YaraScanner('yara_rules')
        result = scanner.scan_file('test.exe', timeout=0.001)
        assert isinstance(result, dict)
    
    def test_invalid_rules_dir(self):
        """Test handling invalid rules directory"""
        scanner = YaraScanner('nonexistent_dir')
        info = scanner.get_rules_info()
        # Should handle gracefully, not raise exception
        assert info['rules_count'] == 0
