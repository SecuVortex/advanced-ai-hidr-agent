from typing import Dict, Any
from agents.base_agent import BaseAgent
try:
    from tools.dual_llm import DualLLM
    DUAL_LLM_AVAILABLE = True
except:
    DUAL_LLM_AVAILABLE = False
    from tools.llm_tools import LLMTools


class AnalystAgent(BaseAgent):

    def __init__(self):
        super().__init__(name='AnalystAgent', role=
            'Security Analyst (AI-Powered)')
        if DUAL_LLM_AVAILABLE:
            self.dual_llm = DualLLM()
            self.llm_tools = None
        else:
            from tools.llm_tools import LLMTools
            self.llm_tools = LLMTools()
            self.dual_llm = None

    def analyze(self, data: Dict[str, Any]) ->Dict[str, Any]:
        detection = data.get('detection', {})
        intelligence = data.get('intelligence', {})
        response = data.get('response', {})
        return self.analyze_incident(detection, intelligence, response)

    def analyze_incident(self, detection: Dict[str, Any], intelligence:
        Dict[str, Any], response: Dict[str, Any]) ->Dict[str, Any]:
        self.log_info('Generating AI-powered threat analysis...')
        if self.dual_llm and self.dual_llm.is_available():
            ai_summary = self._analyze_with_dual_llm(detection, intelligence)
        elif self.llm_tools:
            ai_summary = self.llm_tools.analyze_threat(detection, intelligence)
        else:
            ai_summary = None
        if not ai_summary:
            ai_summary = self._fallback_analysis(detection, intelligence)
            self.log_warning('Using fallback analysis (LLM unavailable)')
        threat_level = detection.get('threat_level', 0)
        severity = self.llm_tools.determine_severity(ai_summary, threat_level)
        user_explanation = self.llm_tools.explain_to_user(detection,
            intelligence, ai_summary)
        result = {'agent': self.name, 'summary': ai_summary, 'severity':
            severity, 'user_explanation': user_explanation, 'threat_level':
            detection.get('threat_level', 0), 'is_known_malware':
            intelligence.get('is_known_malware', False)}
        self.log_info(f'Analysis complete - Severity: {severity}')
        return result

    def _fallback_analysis(self, detection: Dict, intelligence: Dict) ->str:
        threat_level = detection.get('threat_level', 0)
        is_suspicious = detection.get('is_suspicious', False)
        reasons = detection.get('reasons', [])
        vt_malicious = intelligence.get('virustotal', {}).get('malicious', 0)
        is_known_malware = intelligence.get('is_known_malware', False)
        if is_known_malware:
            return (
                f'CRITICAL THREAT: This file is confirmed malware with {vt_malicious} VirusTotal detections. Immediate quarantine recommended. This is a known malicious file that poses significant risk to system security.'
                )
        elif threat_level >= 7:
            return (
                f"HIGH THREAT: Multiple suspicious indicators detected (threat level: {threat_level}/10). Reasons: {', '.join(reasons)}. Recommend immediate termination and quarantine to prevent potential system compromise."
                )
        elif is_suspicious:
            return (
                f"MEDIUM THREAT: Suspicious behavior detected (threat level: {threat_level}/10). Reasons: {', '.join(reasons)}. Recommend monitoring or temporary termination. May be false positive."
                )
        else:
            return (
                f'LOW THREAT: No significant threats detected. Process/file appears to be legitimate. Continue monitoring for any changes.'
                )

    def generate_recommendations(self, analysis: Dict[str, Any]) ->list:
        severity = analysis.get('severity', 'Medium')
        is_known_malware = analysis.get('is_known_malware', False)
        recommendations = []
        if is_known_malware:
            recommendations.extend(['Immediately quarantine the file',
                'Terminate all related processes',
                'Scan system for additional infections',
                'Review system logs for compromise indicators',
                'Consider full system scan with updated antivirus'])
        elif severity == 'Critical':
            recommendations.extend(['Terminate process immediately',
                'Quarantine executable file',
                'Investigate process origin and purpose',
                'Check for persistence mechanisms',
                'Review recent system changes'])
        elif severity == 'High':
            recommendations.extend(['Terminate process temporarily',
                'Investigate process behavior',
                'Check VirusTotal for additional information',
                'Monitor for related suspicious activity'])
        elif severity == 'Medium':
            recommendations.extend(['Continue monitoring process',
                'Verify process legitimacy',
                'Check digital signature if available',
                'Review process network activity'])
        else:
            recommendations.extend(['No immediate action required',
                'Continue routine monitoring',
                'Log event for future reference'])
        return recommendations

    def _analyze_with_dual_llm(self, detection: Dict, intelligence: Dict
        ) ->str:
        try:
            prompt = f"""Cybersecurity Analysis:

Process: {detection.get('process_name', 'Unknown')}
Path: {detection.get('path', 'Unknown')}
Threat Level: {detection.get('threat_level', 0)}/10
Indicators: {', '.join(detection.get('reasons', []))}
VirusTotal: {intelligence.get('virustotal', {}).get('malicious', 0)} detections

Provide brief analysis: threat type, risk level, recommended action."""
            response = self.dual_llm.invoke(prompt, prefer_gemini=True)
            return response if response else self._fallback_analysis(detection,
                intelligence)
        except:
            return self._fallback_analysis(detection, intelligence)
