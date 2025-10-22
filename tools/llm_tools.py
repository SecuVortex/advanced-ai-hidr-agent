from typing import Optional, Dict, Any
from agents.config import Config
from tools.dual_llm import DualLLM


class LLMTools:

    def __init__(self):
        self.dual_llm = DualLLM()
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        try:
            provider = Config.LLM_PROVIDER.lower()
            if provider == 'gemini':
                if (not Config.GOOGLE_API_KEY or Config.GOOGLE_API_key ==
                    'your_gemini_api_key_here'):
                    print(
                        ' Gemini API key not configured. Using rule-based analysis.'
                        )
                    return None
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(model='gemini-pro',
                    google_api_key=Config.GOOGLE_API_KEY, temperature=0.4,
                    max_output_tokens=500)
            elif provider == 'openai':
                if (not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY ==
                    'your_openai_api_key_here'):
                    print(
                        ' OpenAI API key not configured. Using rule-based analysis.'
                        )
                    return None
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(model='gpt-4o', openai_api_key=Config.
                    OPENAI_API_KEY, temperature=0.4, max_tokens=800)
            else:
                print(
                    f' Unknown LLM provider: {provider}. Using rule-based analysis.'
                    )
                return None
        except Exception as e:
            print(f' Failed to initialize LLM: {e}. Using rule-based analysis.'
                )
            return None

    def analyze_threat(self, detection: Dict, intelligence: Dict) ->Optional[
        str]:
        if self.llm:
            try:
                prompt = f"""Analyze the following security event and provide a brief, one-paragraph summary.
                Detection details: {detection}
                Threat intelligence: {intelligence}"""
                response = self.dual_llm.invoke(prompt, prefer_gemini=True)
                if response:
                    return response
            except Exception as e:
                print(f' LLM analysis failed: {e}')
        return self._rule_based_analysis(detection, intelligence)

    def _rule_based_analysis(self, detection: Dict, intelligence: Dict) ->str:
        if intelligence.get('is_known_malware'):
            return 'Confirmed malware detected. Immediate action required.'
        if detection.get('threat_level', 0) >= 8:
            return 'High threat level detected. Potentially malicious.'
        return (
            'Suspicious activity detected. Further investigation recommended.')

    def determine_severity(self, analysis: str, threat_level: int=0) ->str:
        analysis_lower = analysis.lower()
        if ('critical' in analysis_lower or 'confirmed malware' in
            analysis_lower):
            return 'Critical'
        if 'high' in analysis_lower or threat_level >= 8:
            return 'High'
        if ('medium' in analysis_lower or 'suspicious' in analysis_lower or
            threat_level >= 5):
            return 'Medium'
        return 'Low'

    def generate_recommendation(self, severity: str, threat_type: str) ->str:
        if severity == 'Critical':
            return 'Terminate process and quarantine file immediately.'
        if severity == 'High':
            return 'Terminate process and investigate.'
        return 'Monitor process for further activity.'

    def explain_to_user(self, detection: Dict, intelligence: Dict, analysis:
        str) ->str:
        explanation = f'AI Analysis Summary: {analysis}\n'
        explanation += f"Threat Level: {detection.get('threat_level', 0)}/10\n"
        if intelligence.get('is_known_malware'):
            explanation += (
                'This appears to be known malware based on threat intelligence.\n'
                )
        return explanation.strip()
