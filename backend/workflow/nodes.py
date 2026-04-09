from langchain_core.messages import HumanMessage, SystemMessage
from core.state import AgentState, MoodParsing, MovieSelection
from core.config import CONFIG
from tools.tools import retrieve_candidates

llm = CONFIG["LLM"]

def parse_mood_node(state: AgentState):
    print("--- [NODE] Trích xuất cảm xúc ---")
    
    # SYSTEM PROMPT cho Node 1 (Có luật chấm điểm confidence_score)
    system_prompt = """Bạn là một hệ thống phân tích tâm lý. 
    Nhiệm vụ: 
    1. Trích xuất cảm xúc từ câu chuyện của người dùng, ánh xạ sang tối đa 3 thể loại phim (genres) và tạo một cụm từ tìm kiếm (semantic_query) bằng tiếng Anh.
    2. QUAN TRỌNG: Đánh giá độ tin cậy (confidence_score) từ 0.0 đến 1.0. Nếu người dùng nhập quá ngắn, không có cảm xúc rõ ràng, hoặc chỉ là câu chào hỏi (VD: 'chào', 'tôi muốn xem phim', 'buồn'), hãy cho điểm < 0.6. Nếu câu chuyện rõ ràng, cho điểm >= 0.6."""
    
    parser = llm.with_structured_output(MoodParsing)
    result = parser.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Tâm sự: {state['user_story']}")
    ])
    
    print(f"[DEBUG] Confidence Score: {result.confidence_score}")
    
    return {
        "target_genres": result.target_genres, 
        "semantic_query": result.semantic_query,
        "confidence_score": result.confidence_score
    }

# ==========================================================
# ĐÂY LÀ HÀM BỊ THIẾU GÂY RA LỖI (Ask Clarification Node)
# ==========================================================
def ask_clarification_node(state: AgentState):
    print("--- [NODE] Yêu cầu cung cấp thêm thông tin ---")
    return {
        "final_response": "Mình chưa hiểu rõ tâm trạng hiện tại của bạn lắm. Bạn có thể chia sẻ chi tiết hơn một chút để mình có thể tìm được bộ phim 'bắt' đúng tần số của bạn không?",
        "top_k_movies": [] # Trả về mảng rỗng để an toàn cho Frontend
    }

def retrieval_node(state: AgentState):
    print("--- [NODE] Lọc ứng viên thô từ JSON ---")
    candidates = retrieve_candidates(state['target_genres'], max_candidates=20)
    return {"candidate_movies": candidates}

def llm_ranking_node(state: AgentState):
    print("--- [NODE] LLM tự chấm điểm & chọn Top 15 ---")
    candidates = state.get('candidate_movies', [])
    if not candidates:
        return {"top_k_movies": []}

    # Bọc ID trong dấu nháy đơn để LLM không bị nhầm lẫn format
    candidates_text = "\n".join([f"- ID: '{m.get('show_id')}' | Phim: {m.get('title')}\n  Mô tả: {m.get('description')}" for m in candidates])

    system_prompt = """Bạn là một giám khảo điện ảnh công tâm. 
    Chỉ được trả về một danh sách chứa ĐÚNG mã show_id (copy chính xác từng ký tự, không thêm chữ 'ID:') của 15 bộ phim phù hợp nhất."""
    
    human_prompt = f"Tâm trạng: {state['user_story']} (Từ khóa: {state['semantic_query']})\n\nDanh sách ứng viên:\n{candidates_text}"
    
    selector = llm.with_structured_output(MovieSelection)
    result = selector.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])
    
    # Làm sạch ID (xóa khoảng trắng thừa) trước khi so sánh
    selected_ids = [str(sid).strip() for sid in result.selected_show_ids[:15]]
    print(f"[DEBUG] Các ID mà LLM đã chọn: {selected_ids}")
    
    top_k = []
    for m in candidates:
        m_id = str(m.get('show_id')).strip()
        if m_id in selected_ids:
            top_k.append(m)
            
    # FALLBACK AN TOÀN
    if not top_k and candidates:
        print("[WARNING] LLM trả về ID không khớp. Kích hoạt Fallback lấy 15 phim đầu.")
        top_k = candidates[:15]
        
    return {"top_k_movies": top_k}

def synthesize_response_node(state: AgentState):
    print("--- [NODE] Tổng hợp câu trả lời thấu cảm ---")
    
    system_prompt = """Bạn là một người bạn thân thiết, am hiểu điện ảnh và cực kỳ thấu cảm.
    Quy tắc bắt buộc:
    1. Xưng 'mình' và gọi người dùng là 'bạn'.
    2. Xác nhận và đồng cảm ngắn gọn với cảm xúc của họ.
    3. Dựa vào danh sách phim hệ thống đã cấp, giải thích TẠI SAO họ nên xem từng phim đó để vượt qua tâm trạng này.
    4. KHÔNG ĐƯỢC TÓM TẮT LẠI NỘI DUNG (description). Hãy nói về thông điệp và ý nghĩa của phim đối với cảm xúc của họ."""

    human_prompt = f"Tâm sự của tôi: '{state['user_story']}'\n\nPhim bạn đã chọn cho tôi: {state['top_k_movies']}"
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])
    return {"final_response": response.content}