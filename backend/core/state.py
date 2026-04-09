from typing import TypedDict, List
from pydantic import BaseModel, Field

class MovieData(TypedDict):
    """
    Cấu trúc chính xác của một bộ phim trả về từ Vector DB/Search Tool.
    Khớp 100% với schema JSON gốc.
    """
    show_id: str
    type: str
    title: str
    director: str
    cast: str
    country: str
    date_added: str
    release_year: str
    rating: str
    duration: str
    genres: str
    language: str
    description: str
    popularity: str
    vote_count: str
    vote_average: str
    budget: str
    revenue: str

class AgentState(TypedDict):
    user_story: str
    target_genres: List[str]
    semantic_query: str
    
    # BẮT BUỘC PHẢI CÓ DÒNG NÀY ĐỂ LANGGRAPH KHÔNG VỨT DỮ LIỆU ĐI
    candidate_movies: List[MovieData] 
    
    top_k_movies: List[MovieData]
    final_response: str

class MoodParsing(BaseModel):
    target_genres: List[str] = Field(description="Các thể loại Netflix phù hợp (VD: Action, Drama)")
    semantic_query: str = Field(description="Tóm tắt cảm xúc thành keyword tiếng Anh")

class MovieSelection(BaseModel):
    selected_show_ids: List[str] = Field(description="Danh sách show_id của Top 3 phim phù hợp nhất với tâm trạng")