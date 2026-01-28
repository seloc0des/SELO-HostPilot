from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class ConfirmationPlan:
    def __init__(self, plan_id: str, session_id: str, tool_name: str, args: Dict[str, Any], summary: str):
        self.plan_id = plan_id
        self.session_id = session_id
        self.tool_name = tool_name
        self.args = args
        self.summary = summary
        self.created_at = datetime.utcnow()
        self.executed = False


class PlanStore:
    def __init__(self):
        self._plans: Dict[str, ConfirmationPlan] = {}
    
    def create_plan(self, session_id: str, tool_name: str, args: Dict[str, Any], summary: str) -> str:
        plan_id = f"pln_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        plan = ConfirmationPlan(plan_id, session_id, tool_name, args, summary)
        self._plans[plan_id] = plan
        return plan_id
    
    def get_plan(self, plan_id: str) -> Optional[ConfirmationPlan]:
        return self._plans.get(plan_id)
    
    def mark_executed(self, plan_id: str) -> None:
        if plan_id in self._plans:
            self._plans[plan_id].executed = True
    
    def delete_plan(self, plan_id: str) -> None:
        if plan_id in self._plans:
            del self._plans[plan_id]


plan_store = PlanStore()
