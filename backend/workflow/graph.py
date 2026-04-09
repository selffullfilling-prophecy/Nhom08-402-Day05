from langgraph.graph import StateGraph, END
from core.state import AgentState
from workflow import nodes

# Hàm bẻ lái (Router): Trả về tên của Node tiếp theo dựa trên State
def route_after_parse(state: AgentState):
    if state.get("confidence_score", 0.0) < 0.6:
        # Nếu điểm thấp -> Chuyển sang Node hỏi lại
        return "ask_clarification_node"
    # Nếu điểm cao -> Đi bình thường tới Node tìm kiếm
    return "retrieval_node"

def build_graph():
    workflow = StateGraph(AgentState)

    # 1. Khai báo các Nodes
    workflow.add_node("parse_mood_node", nodes.parse_mood_node)
    workflow.add_node("ask_clarification_node", nodes.ask_clarification_node) # Node mới
    workflow.add_node("retrieval_node", nodes.retrieval_node)
    workflow.add_node("llm_ranking_node", nodes.llm_ranking_node)
    workflow.add_node("synthesize_response_node", nodes.synthesize_response_node)

    # 2. Định nghĩa luồng chạy (Edges)
    workflow.set_entry_point("parse_mood_node")
    
    # Rẽ nhánh sau khi parse mood
    workflow.add_conditional_edges(
        "parse_mood_node",
        route_after_parse,
        {
            "ask_clarification_node": "ask_clarification_node",
            "retrieval_node": "retrieval_node"
        }
    )

    # Nhánh 1: Nếu bị yêu cầu làm rõ -> Kết thúc Graph và trả về Front-end luôn
    workflow.add_edge("ask_clarification_node", END)

    # Nhánh 2: Nếu đủ tự tin -> Chạy luồng tìm phim bình thường
    workflow.add_edge("retrieval_node", "llm_ranking_node")
    workflow.add_edge("llm_ranking_node", "synthesize_response_node")
    workflow.add_edge("synthesize_response_node", END)

    return workflow.compile()