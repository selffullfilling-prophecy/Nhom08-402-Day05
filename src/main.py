import json
from workflow.graph import build_graph

def main():
    print("=== ĐANG XỬ LÝ YÊU CẦU TỪ FRONTEND ===\n")
    agent_app = build_graph()
    
    initial_state = {
        "user_story": "Dạo này tôi thấy chênh vênh quá, mới ra trường đi làm mà thấy cái gì cũng khó khăn, không biết mình có đang đi đúng hướng không."
    }
    
    config = {"configurable": {"thread_id": "1"}}
    
    # [ĐÃ SỬA] Dùng .invoke() để lấy ngay lập tức TẤT CẢ các trường trong State cuối cùng
    try:
        final_state = agent_app.invoke(initial_state, config=config)
        
        # ==========================================
        # ĐÓNG GÓI PAYLOAD TRẢ VỀ CHO FRONTEND
        # ==========================================
        api_response = {
            "status": "success",
            "data": {
                "counselor_message": final_state.get("final_response", ""),
                "recommended_movies": final_state.get("top_k_movies", [])
            }
        }
        
        print("\n=== PAYLOAD TRẢ VỀ FRONTEND (JSON) ===")
        # In ra màn hình JSON chuẩn, giữ nguyên font tiếng Việt
        print(json.dumps(api_response, indent=4, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            "status": "error", 
            "message": f"Lỗi hệ thống: {str(e)}"
        }))

if __name__ == "__main__":
    main()