"""
Dual LLM System - Load balancing between Gemini and OpenAI
"""
from typing import Optional, Dict, Any
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
            from agents.config import Config
            if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != "your_google_api_key_here":
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=Config.GOOGLE_API_KEY,
                    temperature=0.3
                )
                self.gemini_available = True
                print("[OK] Gemini API initialized")
        except Exception as e:
            print(f"[WARN] Gemini init failed: {e}")
    
    def _init_openai(self):
        try:
            from agents.config import Config
            if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
                from langchain_openai import ChatOpenAI
                self.openai_llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    openai_api_key=Config.OPENAI_API_KEY,
                    temperature=0.3,
                    max_tokens=800
                )
                self.openai_available = True
                print("[OK] OpenAI API initialized")
        except Exception as e:
            print(f"[WARN] OpenAI init failed: {e}")
    
    def invoke(self, prompt: str, prefer_gemini: bool = True) -> Optional[str]:
        """Invoke LLM with load balancing"""
        if prefer_gemini and self.gemini_available:
            try:
                response = self.gemini_llm.invoke(prompt)
                return response.content
            except Exception as e:
                print(f"⚠️  Gemini failed, trying OpenAI: {e}")
                if self.openai_available:
                    try:
                        response = self.openai_llm.invoke(prompt)
                        return response.content
                    except:
                        pass
        elif self.openai_available:
            try:
                response = self.openai_llm.invoke(prompt)
                return response.content
            except Exception as e:
                print(f"⚠️  OpenAI failed, trying Gemini: {e}")
                if self.gemini_available:
                    try:
                        response = self.gemini_llm.invoke(prompt)
                        return response.content
                    except:
                        pass
        return None
    
    def is_available(self) -> bool:
        return self.gemini_available or self.openai_available
