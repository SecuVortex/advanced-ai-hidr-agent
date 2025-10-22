import unittest
from unittest.mock import patch
import os
from agents.config import Config


class TestGeminiAPI(unittest.TestCase):

    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'your_test_api_key'})
    def test_api_key_loading(self):
        self.assertEqual(Config.GOOGLE_API_KEY, 'your_test_api_key')

    @patch('langchain_google_genai.ChatGoogleGenerativeAI')
    def test_llm_initialization(self, mock_chat_google):
        from tools.llm_tools import LLMTools
        tools = LLMTools()
        mock_chat_google.assert_called_once()


if __name__ == '__main__':
    unittest.main()
