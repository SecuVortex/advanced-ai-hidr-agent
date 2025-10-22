from typing import Optional, Dict, Any
from agents.config import Config
import random


class DualLLM:

    def __init__(self):
        self.gemini_llm = None
        self.openai_llm = None
        self.gemini_available = False
        self.openai_available = False
        self._init_gemini()
        self._init_openai()

    def _init_gemini(self):
        try:
            if (Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY !=
                'your_google_api_key_here'):
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.gemini_llm = ChatGoogleGenerativeAI(model=
                    'gemini-1.5-flash-latest', google_api_key=Config.
                    GOOGLE_API_KEY, temperature=0.3)
                self.gemini_available = True
                print('✓ Gemini API initialized')
        except Exception as e:
            print(f'⚠️  Gemini init failed: {e}')

    def _init_openai(self):
        try:
            if (Config.OPENAI_API_KEY and Config.OPENAI_API_KEY !=
                'your_openai_api_key_here'):
                from langchain_openai import ChatOpenAI
                self.openai_llm = ChatOpenAI(model='gpt-4o', openai_api_key
                    =Config.OPENAI_API_KEY, temperature=0.3, max_tokens=800)
                self.openai_available = True
                print('✓ OpenAI API initialized')
        except Exception as e:
            print(f'⚠️  OpenAI init failed: {e}')

    def is_available(self):
        return self.gemini_available or self.openai_available

    def invoke(self, prompt: str, prefer_gemini: bool=True) ->Optional[str]:
        llm = None
        if prefer_gemini and self.gemini_available:
            llm = self.gemini_llm
        elif self.openai_available:
            llm = self.openai_llm
        elif self.gemini_available:
            llm = self.gemini_llm
        if not llm:
            return None
        try:
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f'LLM invocation failed: {e}')
            return None
