"""
LLM Integration Tools
Provides AI-powered analysis using language models.
"""

from typing import Optional, Dict, Any
from agents.config import Config
from tools.dual_llm import DualLLM


class LLMTools:
    """LLM integration for AI-powered analysis with dual API support"""
    
    def __init__(self):
        self.dual_llm = DualLLM()
        self.llm = self.dual_llm if self.dual_llm.is_available() else None
    
    def _initialize_llm_old(self) -> None:
        """Initialize LLM based on configuration (optimized for free tier)"""
        try:
            provider = Config.LLM_PROVIDER.lower()
            
            if provider == "gemini":
                if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == "your_google_api_key_here":
                    print("⚠️  Gemini API key not configured. Using rule-based analysis.")
                    self.llm = None
                    return
                
                from langchain_google_genai import ChatGoogleGenerativeAI
                # Use gemini-pro for free tier
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=Config.GOOGLE_API_KEY,
                    temperature=Config.LLM_TEMPERATURE,
                    max_output_tokens=min(Config.LLM_MAX_TOKENS, 500)  # Limit for free tier
                )
            elif provider == "openai":
                if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "your_openai_api_key_here":
                    print("⚠️  OpenAI API key not configured. Using rule-based analysis.")
                    self.llm = None
                    return
                
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",  # Cheaper for free tier
                    openai_api_key=Config.OPENAI_API_KEY,
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=Config.LLM_MAX_TOKENS
                )
            elif provider == "mistral":
                if not Config.MISTRAL_API_KEY or Config.MISTRAL_API_KEY == "your_mistral_api_key_here":
                    print("⚠️  Mistral API key not configured. Using rule-based analysis.")
                    self.llm = None
                    return
                
                from langchain_mistralai import ChatMistralAI
                self.llm = ChatMistralAI(
                    model="mistral-small-latest",  # Cheaper option
                    mistral_api_key=Config.MISTRAL_API_KEY,
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=Config.LLM_MAX_TOKENS
                )
            else:
                print(f"⚠️  Unknown LLM provider: {provider}. Using rule-based analysis.")
                self.llm = None
        
        except Exception as e:
            print(f"⚠️  Failed to initialize LLM: {e}. Using rule-based analysis.")
            self.llm = None
    
    def analyze_threat(self, detection: Dict, intelligence: Dict) -> Optional[str]:
        """
        Analyze threat using LLM with fallback to rule-based analysis
        
        Args:
            detection: Detection results
            intelligence: Intelligence results
            
        Returns:
            Analysis summary
        """
        # Try LLM analysis first
        if self.llm:
            try:
                prompt = f"""You are a cybersecurity expert. Analyze this threat:

Process: {detection.get('process_name', 'Unknown')}
Path: {detection.get('path', 'Unknown')}
Threat Level: {detection.get('threat_level', 0)}/10
Suspicious Indicators: {', '.join(detection.get('reasons', []))}
VirusTotal Detections: {intelligence.get('virustotal', {}).get('malicious', 0)}

Provide:
1. Threat type (ransomware/keylogger/trojan/legitimate)
2. Risk assessment (critical/high/medium/low)
3. Recommended action (terminate/quarantine/monitor/allow)

Be concise and actionable."""

                response = self.dual_llm.invoke(prompt, prefer_gemini=True)
                if response:
                    return response
            
            except Exception as e:
                print(f"⚠️  LLM analysis failed: {e}")
        
        # Rule-based fallback analysis
        return self._rule_based_analysis(detection, intelligence)
    
    def _rule_based_analysis(self, detection: Dict, intelligence: Dict) -> str:
        """Fallback rule-based analysis when LLM unavailable"""
        threat_level = detection.get('threat_level', 0)
        reasons = detection.get('reasons', [])
        vt_detections = intelligence.get('virustotal', {}).get('malicious', 0)
        
        if threat_level >= 7 or vt_detections >= 5:
            return f"Critical threat detected. This appears to be malware with threat level {threat_level}/10 and {vt_detections} VirusTotal detections. Immediate termination recommended to prevent system compromise."
        elif threat_level >= 4 or vt_detections >= 2:
            return f"Suspicious activity detected. Threat level {threat_level}/10 with concerning patterns: {', '.join(reasons[:2])}. Recommend temporary termination and further investigation."
        elif threat_level >= 2:
            return f"Low-level suspicious behavior detected. Threat level {threat_level}/10. Recommend monitoring for escalation. May be legitimate software with unusual behavior."
        else:
            return f"Minimal threat detected. Threat level {threat_level}/10. Process appears safe but flagged for: {', '.join(reasons[:1]) if reasons else 'precautionary monitoring'}. Safe to allow."
    
    def determine_severity(self, analysis: str, threat_level: int = 0) -> str:
        """
        Extract severity from analysis with threat level fallback
        
        Args:
            analysis: LLM analysis text
            threat_level: Numeric threat level (0-10)
            
        Returns:
            Severity level (Critical/High/Medium/Low)
        """
        if not analysis:
            # Fallback to threat level
            if threat_level >= 7:
                return "Critical"
            elif threat_level >= 4:
                return "High"
            elif threat_level >= 2:
                return "Medium"
            else:
                return "Low"
        
        analysis_lower = analysis.lower()
        
        if any(word in analysis_lower for word in ["critical", "severe", "immediate", "urgent", "malware"]):
            return "Critical"
        elif any(word in analysis_lower for word in ["high", "dangerous", "serious", "suspicious"]):
            return "High"
        elif any(word in analysis_lower for word in ["low", "minimal", "unlikely", "safe"]):
            return "Low"
        else:
            return "Medium"
    
    def generate_recommendation(self, severity: str, threat_type: str) -> str:
        """
        Generate action recommendation
        
        Args:
            severity: Threat severity
            threat_type: Type of threat
            
        Returns:
            Recommended action
        """
        if severity in ["Critical", "High"]:
            return "terminate_permanent"
        elif severity == "Medium":
            return "terminate_temporary"
        else:
            return "monitor"
    
    def explain_to_user(self, detection: Dict, intelligence: Dict, analysis: str) -> str:
        """
        Generate user-friendly explanation
        
        Args:
            detection: Detection results
            intelligence: Intelligence results
            analysis: LLM analysis
            
        Returns:
            User-friendly explanation
        """
        threat_level = detection.get('threat_level', 0)
        vt_detections = intelligence.get('virustotal', {}).get('malicious', 0)
        
        explanation = f"""
🔍 THREAT ANALYSIS

{analysis}

📊 TECHNICAL DETAILS:
• Threat Score: {threat_level}/10
• VirusTotal Detections: {vt_detections}
• Detection Reasons: {', '.join(detection.get('reasons', ['None']))}

⚠️  This analysis is based on behavioral patterns and threat intelligence.
"""
        return explanation.strip()
