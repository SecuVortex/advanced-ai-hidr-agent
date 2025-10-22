from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class CoordinatorAgent(BaseAgent):

    def __init__(self):
        super().__init__(name='CoordinatorAgent', role=
            'Multi-Agent Coordinator')
        self.workflow_history: List[Dict[str, Any]] = []

    def analyze(self, data: Dict[str, Any]) ->Dict[str, Any]:
        return self.coordinate_workflow(data)

    def coordinate_workflow(self, workflow_state: Dict[str, Any]) ->Dict[
        str, Any]:
        self.log_info('Coordinating workflow...')
        detection = workflow_state.get('detection_result', {})
        intelligence = workflow_state.get('intelligence_result', {})
        analysis = workflow_state.get('analysis_result', {})
        priority = self._calculate_priority(detection, intelligence, analysis)
        action = self._resolve_action_conflicts(detection, intelligence,
            analysis)
        requires_human_approval = self._requires_human_approval(priority,
            action)
        result = {'agent': self.name, 'priority': priority,
            'recommended_action': action, 'requires_human_approval':
            requires_human_approval, 'notes': self._generate_notes(
            workflow_state)}
        self.workflow_history.append(result)
        self.log_info(
            f'Coordination complete - Priority: {priority}, Action: {action}')
        return result

    def _calculate_priority(self, detection: Dict, intelligence: Dict,
        analysis: Dict) ->str:
        if intelligence.get('is_known_malware'):
            return 'Critical'
        if analysis.get('severity') == 'Critical':
            return 'Critical'
        if detection.get('threat_level', 0) >= 8:
            return 'High'
        if analysis.get('severity') == 'High':
            return 'High'
        if detection.get('threat_level', 0) >= 5:
            return 'Medium'
        return 'Low'

    def _resolve_action_conflicts(self, detection: Dict, intelligence: Dict,
        analysis: Dict) ->str:
        actions = [detection.get('recommendation'), intelligence.get(
            'recommendation')]
        if intelligence.get('is_known_malware'):
            return 'terminate_permanent'
        if 'terminate_permanent' in actions:
            return 'terminate_permanent'
        if 'terminate_temporary' in actions:
            return 'terminate_temporary'
        if 'quarantine' in actions:
            return 'quarantine'
        if 'monitor' in actions:
            return 'monitor'
        return 'allow'

    def _requires_human_approval(self, priority: str, action: str) ->bool:
        if priority in ['Critical', 'High']:
            return True
        if 'terminate' in action:
            return True
        return False

    def _generate_notes(self, workflow_state: Dict) ->str:
        return (
            f"Coordination based on threat level {workflow_state['detection_result'].get('threat_level', 0)} and severity {workflow_state['analysis_result'].get('severity', 'Unknown')}."
            )

    def get_workflow_summary(self) ->Dict[str, Any]:
        total = len(self.workflow_history)
        priorities = [h['priority'] for h in self.workflow_history]
        actions = [h['recommended_action'] for h in self.workflow_history]
        return {'total_events': total, 'critical_priority': priorities.
            count('Critical'), 'high_priority': priorities.count('High'),
            'medium_priority': priorities.count('Medium'), 'low_priority':
            priorities.count('Low'), 'terminate_actions': actions.count(
            'terminate_permanent') + actions.count('terminate_temporary')}
