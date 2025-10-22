import time
from typing import Dict, Any, Optional

class SimpleMultiAgent:
    def __init__(self):
        self.messages = []
        self.gemini_llm = None
        self.openai_llm = None
        self._init_llms()

    def _init_llms(self):
        try:
            from agents.config import Config
            if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != "your_google_api_key_here":
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro")
        except ImportError:
            pass

    def _send_message(self, from_agent: str, to_agent: str, message: str):
        msg = {
            'from_agent': from_agent,
            'to_agent': to_agent,
            'message': message,
            'timestamp': time.time()
        }
        self.messages.append(msg)
        print(f"[MSG] [{from_agent}] -> [{to_agent}]: {message}")

    def analyze_process(self, proc_name: str, path: str, cmdline: str, pid: int) -> Dict[str, Any]:
        detection_result = self._detection_agent(proc_name, path, cmdline, pid)
        self._send_message("DetectionAgent", "IntelligenceAgent", f"Suspicious process found: {proc_name} (Threat: {detection_result['threat_level']}/10)")

        intelligence_result = self._intelligence_agent(path)
        self._send_message("IntelligenceAgent", "AnalystAgent", f"Threat score: {intelligence_result['threat_score']}/10. Known malware: {intelligence_result['is_known_malware']}")

        analysis_result = self._ai_analysis(detection_result, intelligence_result)
        self._send_message("AnalystAgent", "CoordinatorAgent", f"AI analysis complete. Severity: {analysis_result['severity']}")

        final_action = self._coordinator_agent(detection_result, intelligence_result, analysis_result)
        self._send_message("CoordinatorAgent", "System", f"Final action decided: {final_action}")

        return {
            'final_action': final_action,
            'detection': detection_result,
            'intelligence': intelligence_result,
            'analysis': analysis_result
        }

    def _detection_agent(self, proc_name: str, path: str, cmdline: str, pid: int) -> Dict[str, Any]:
        threat_level = self._calculate_threat_level(proc_name, path, cmdline)
        reasons = self._get_threat_reasons(proc_name, path, cmdline)
        return {'threat_level': threat_level, 'reasons': reasons, 'is_suspicious': threat_level >= 3}

    def _calculate_threat_level(self, proc_name: str, path: str, cmdline: str) -> int:
        score = 0

        if "temp" in path.lower(): score += 3
        if "downloads" in path.lower(): score += 2
        if proc_name.lower() in ["encryptor.exe", "locker.exe", "crypt.exe", "ransomware.exe"]: score += 8
        if proc_name.lower() in ["keylogger.exe", "stealer.exe"]: score += 7
        if "suspicious" in proc_name.lower(): score += 5
        if "powershell" in proc_name.lower() and "-enc" in cmdline.lower(): score += 6

        return min(score, 10)

    def _get_threat_reasons(self, proc_name: str, path: str, cmdline: str) -> list:
        reasons = []
        if "temp" in path.lower(): reasons.append("Runs from Temp folder")
        if "downloads" in path.lower(): reasons.append("Runs from Downloads folder")
        if proc_name.lower() in ["ransomware.exe"]: reasons.append("Name suggests ransomware")
        if "powershell" in proc_name.lower() and "-enc" in cmdline.lower(): reasons.append("Uses encoded PowerShell")
        return reasons

    def _intelligence_agent(self, path: str) -> Dict[str, Any]:
        try:
            from tools.virustotal_tool import VirusTotalTool
            from tools.security_tools import SecurityTools

            if not path or not path.endswith('.exe'):
                return {'threat_score': 0, 'is_known_malware': False}

            vt = VirusTotalTool()
            file_hash = SecurityTools.calculate_file_hash(path)

            if file_hash:
                result = vt.query_file_hash(file_hash)
                malicious = result.get('malicious', 0)
                score = min((malicious / 5) * 10, 10) if malicious > 0 else 0

                return {
                    'threat_score': score,
                    'is_known_malware': malicious >= 5,
                    'detections': malicious
                }
        except:
            pass

        return {'threat_score': 0, 'is_known_malware': False}

    def _ai_analysis(self, detection: Dict, intelligence: Dict) -> Dict:
        threat_level = detection.get('threat_level', 0)
        reasons = detection.get('reasons', [])

        if self.gemini_llm:
            try:
                prompt = f"Analyze security threat. Threat level: {threat_level}/10. Reasons: {', '.join(reasons)}. Provide brief analysis and severity (Low, Medium, High, Critical)."
                response = self.gemini_llm.invoke(prompt)
                summary = response.content
                severity = self._extract_severity(summary, threat_level)
                return {'summary': summary, 'severity': severity}
            except Exception as e:
                print(f"LLM failed: {e}")

        return self._fallback_analysis(detection, intelligence)

    def _fallback_analysis(self, detection: Dict, intelligence: Dict) -> Dict:
        threat_level = detection.get('threat_level', 0)
        reasons = detection.get('reasons', [])

        if threat_level >= 8:
            return {
                'summary': f"Critical threat detected. {', '.join(reasons[:2])}. Immediate termination recommended.",
                'severity': 'Critical'
            }
        elif threat_level >= 5:
            return {
                'summary': f"Suspicious activity. {', '.join(reasons[:2])}. Recommend termination.",
                'severity': 'High'
            }
        elif threat_level >= 3:
            return {
                'summary': f"Low-level suspicious behavior. {', '.join(reasons[:1])}. Monitor recommended.",
                'severity': 'Medium'
            }
        else:
            return {
                'summary': "Minimal threat. Process appears safe.",
                'severity': 'Low'
            }

    def _extract_severity(self, summary: str, threat_level: int) -> str:
        summary = summary.lower()
        if 'critical' in summary: return 'Critical'
        if 'high' in summary: return 'High'
        if 'medium' in summary: return 'Medium'
        return 'Low'

    def _coordinator_agent(self, detection: Dict, intelligence: Dict, analysis: Dict) -> str:
        threat_level = detection.get('threat_level', 0)
        severity = analysis.get('severity', 'Low')
        is_known_malware = intelligence.get('is_known_malware', False)

        if is_known_malware or threat_level >= 8:
            return 'terminate_permanent'
        elif threat_level >= 5 or severity == 'High':
            return 'terminate_temporary'
        elif threat_level >= 3:
            return 'monitor'
        else:
            return 'allow'

if __name__ == "__main__":
    agent = SimpleMultiAgent()
    result = agent.analyze_process("ransomware.exe", "C:\\Users\\test\\AppData\\Local\\Temp\\ransomware.exe", "", 1234)
    print("\n--- FINAL RESULT ---")
    print(f"Action: {result['final_action']}")
    print(f"Detection: {result['detection']}")
    print(f"Intelligence: {result['intelligence']}")
    print(f"Analysis: {result['analysis']}")
