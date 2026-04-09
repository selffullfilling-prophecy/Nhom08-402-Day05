import json
from typing import List
from core.state import MovieData

DATASET_PATH = "netflix_movies_detailed_up_to_2025.json"
_json_cache = None

def load_json_dataset() -> List[MovieData]:
    global _json_cache
    if _json_cache is None:
        try:
            with open(DATASET_PATH, 'r', encoding='utf-8') as f:
                _json_cache = json.load(f)
        except Exception as e:
            print(f"[TOOL] Lỗi load JSON: {e}")
            _json_cache = []
    return _json_cache

def retrieve_candidates(target_genres: List[str], max_candidates: int = 15) -> List[MovieData]:
    """Lọc thô các phim khớp thể loại để đưa cho LLM chấm điểm."""
    all_movies = load_json_dataset()
    if not all_movies:
        return []

    candidates = []
    # Chuyển genres thành chữ thường để dễ so sánh
    lower_targets = [g.lower() for g in target_genres]
    
    for movie in all_movies:
        movie_genres = movie.get("genres", "").lower()
        # Nếu phim chứa ít nhất 1 thể loại mục tiêu
        if any(target in movie_genres for target in lower_targets):
            candidates.append(movie)
            if len(candidates) >= max_candidates:
                break
                
    # Fallback nếu lọc thể loại quá gắt (Lấy bừa 15 phim đầu)
    if not candidates:
        candidates = all_movies[:max_candidates]
        
    print(f"[TOOL] Đã lấy {len(candidates)} phim ứng viên đưa cho LLM.")
    return candidates