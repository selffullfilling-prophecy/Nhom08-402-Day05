from langgraph.graph import StateGraph, END
from core.state import AgentState
from workflow import nodes

def build_graph():
    workflow = StateGraph(AgentState)

    # Khai báo các Nodes
    workflow.add_node("parse_mood_node", nodes.parse_mood_node)
    workflow.add_node("retrieval_node", nodes.retrieval_node)
    workflow.add_node("llm_ranking_node", nodes.llm_ranking_node)
    workflow.add_node("synthesize_response_node", nodes.synthesize_response_node)

    # Kết nối luồng (Edges)
    workflow.set_entry_point("parse_mood_node")
    workflow.add_edge("parse_mood_node", "retrieval_node")
    workflow.add_edge("retrieval_node", "llm_ranking_node")
    workflow.add_edge("llm_ranking_node", "synthesize_response_node")
    workflow.add_edge("synthesize_response_node", END)

    return workflow.compile()