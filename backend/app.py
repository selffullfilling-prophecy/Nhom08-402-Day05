from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import uvicorn

# Import graph builder từ thư mục workflow của bạn
from workflow.graph import build_graph

# 1. Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Mood-to-Movie AI Counselor API",
    description="API tư vấn phim theo cảm xúc người dùng dựa trên LangGraph & OpenAI",
    version="1.0.0"
)

# 2. Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Khởi tạo Graph
print("=== ĐANG KHỞI TẠO LANGGRAPH AGENT & LOAD DATA ===")
agent_app = build_graph()
print("=== KHỞI TẠO THÀNH CÔNG ===")

# 4. Định nghĩa cấu trúc dữ liệu đầu vào (Request Body)
class UserRequest(BaseModel):
    user_story: str
    thread_id: str = None 

# 5. Xây dựng Endpoint (API Route)
@app.post("/api/v1/recommend")
async def get_movie_recommendation(request: UserRequest):
    try:
        thread_id = request.thread_id or str(uuid.uuid4())
        
        initial_state = {
            "user_story": request.user_story
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        final_state = agent_app.invoke(initial_state, config=config)
        
        return {
            "status": "success",
            "data": {
                "counselor_message": final_state.get("final_response", ""),
                "recommended_movies": final_state.get("top_k_movies", [])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống Backend: {str(e)}")

if __name__ == "__main__":
    # SỬA LẠI CHỖ NÀY: Trỏ vào app (tên file) : app (tên biến FastAPI)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)