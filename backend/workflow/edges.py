# src/workflow/edges.py
from core.state import AgentState

def route_confidence(state: AgentState):
    """Quyết định đi tiếp hay dừng lại để hỏi thêm user"""
    if state['confidence_score'] >= 0.85:
        return "tool_execution_node"
    return "ux_mitigation_node"

def route_hallucination(state: AgentState):
    """Quyết định trả kết quả hay phải soạn lại vì AI ảo tưởng"""
    if state['is_hallucinated'] and not state.get('strict_mode'):
        return "strict_synthesis_node"
    return "finalize_answer_node"