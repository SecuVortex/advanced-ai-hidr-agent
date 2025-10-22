import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
from gui_multiagent import MultiAgentGUI


class TestMultiAgentGUI(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = MultiAgentGUI()
        self.app.root = self.root

    def test_gui_initialization(self):
        self.assertEqual(self.app.root.title(), 'Multi-Agent HIDR System v2.0')

    @patch('tkinter.messagebox')
    def test_start_system_button(self, mock_messagebox):
        self.app.start_system()
        self.assertTrue(self.app.monitoring_active)
        self.assertEqual(self.app.start_btn['state'], 'disabled')

    def tearDown(self):
        self.root.destroy()


if __name__ == '__main__':
    unittest.main()
