import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
from gui_monitor import HIDRGui


class TestHIDRGui(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = HIDRGui()
        self.app.root = self.root

    def test_gui_initialization(self):
        self.assertEqual(self.app.root.title(),
            'HIDR Agent - Host Intrusion Detection & Response')
        self.assertTrue(self.app.notebook.index('end') > 0)

    @patch('tkinter.messagebox')
    def test_start_monitoring_button(self, mock_messagebox):
        self.app.start_monitoring()
        self.assertTrue(self.app.monitoring_active)
        self.assertEqual(self.app.start_btn['state'], 'disabled')

    def tearDown(self):
        self.root.destroy()


if __name__ == '__main__':
    unittest.main()
