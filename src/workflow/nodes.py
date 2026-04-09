from langchain_core.messages import HumanMessage, SystemMessage
from core.state import AgentState, MoodParsing, MovieSelection
from core.config import CONFIG
from tools.tools import retrieve_candidates

llm = CONFIG["LLM"]

def parse_mood_node(state: AgentState):
    print("--- [NODE] Trích xuất cảm xúc ---")
    
    # SYSTEM PROMPT cho Node 1
    system_prompt = """Bạn là một hệ thống phân tích tâm lý. 
    Nhiệm vụ: Trích xuất cảm xúc từ câu chuyện của người dùng, ánh xạ sang tối đa 3 thể loại phim (genres) và tạo một cụm từ tìm kiếm (semantic_query) bằng tiếng Anh."""
    
    parser = llm.with_structured_output(MoodParsing)
    result = parser.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Tâm sự: {state['user_story']}")
    ])
    
    return {
        "target_genres": result.target_genres, 
        "semantic_query": result.semantic_query
    }

def retrieval_node(state: AgentState):
    print("--- [NODE] Lọc ứng viên thô từ JSON ---")
    candidates = retrieve_candidates(state['target_genres'], max_candidates=15)
    return {"candidate_movies": candidates}

def llm_ranking_node(state: AgentState):
    print("--- [NODE] LLM tự chấm điểm & chọn Top 3 ---")
    candidates = state.get('candidate_movies', [])
    if not candidates:
        return {"top_k_movies": []}

    # 1. Bọc ID trong dấu nháy đơn để LLM không bị nhầm lẫn format
    candidates_text = "\n".join([f"- ID: '{m.get('show_id')}' | Phim: {m.get('title')}\n  Mô tả: {m.get('description')}" for m in candidates])

    system_prompt = """Bạn là một giám khảo điện ảnh công tâm. 
    Chỉ được trả về một danh sách chứa ĐÚNG 3 mã show_id (copy chính xác từng ký tự, không thêm chữ 'ID:') của 3 bộ phim phù hợp nhất."""
    
    human_prompt = f"Tâm trạng: {state['user_story']} (Từ khóa: {state['semantic_query']})\n\nDanh sách ứng viên:\n{candidates_text}"
    
    selector = llm.with_structured_output(MovieSelection)
    result = selector.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])
    
    # 2. Làm sạch ID (xóa khoảng trắng thừa) trước khi so sánh
    selected_ids = [str(sid).strip() for sid in result.selected_show_ids[:3]]
    print(f"[DEBUG] Các ID mà LLM đã chọn: {selected_ids}")
    
    top_k = []
    for m in candidates:
        m_id = str(m.get('show_id')).strip()
        if m_id in selected_ids:
            top_k.append(m)
            
    # 3. FALLBACK AN TOÀN: Nếu vì lý do nào đó LLM trả về ID sai khiến top_k rỗng
    if not top_k and candidates:
        print("[WARNING] LLM trả về ID không khớp. Kích hoạt Fallback lấy 3 phim đầu.")
        top_k = candidates[:3]
        
    return {"top_k_movies": top_k}
def synthesize_response_node(state: AgentState):
    print("--- [NODE] Tổng hợp câu trả lời thấu cảm ---")
    
    # SYSTEM PROMPT cho Node 4 (ĐÂY LÀ LINH HỒN CỦA AGENT)
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