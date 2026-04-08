### 1. Optimize Precision hay Recall?

**Lựa chọn:** **[x] Precision**

#### **Tại sao?**
Trong bài toán hệ thống khuyến nghị (Recommendation System) và Agent tư vấn, **Precision (Độ chính xác)** quan trọng hơn vì:
* **Trải nghiệm người dùng:** Người dùng chỉ có thời gian xem 1-2 bộ phim mỗi tối. Nếu Agent đề xuất 5 phim và cả 5 đều đúng gu (High Precision), người dùng sẽ tin tưởng Agent tuyệt đối. 
* **Chi phí của sự sai lầm (Cost of False Positive):** Nếu Agent khẳng định "Bộ phim này chắc chắn bạn sẽ thích" nhưng khi bật lên lại cực kỳ tệ so với gu của họ, người dùng sẽ cảm thấy bị lừa và mất thời gian.
* **Đặc thù Dataset:** Dataset Netflix có hàng ngàn phim. Việc tìm bằng hết (Recall) tất cả các phim hợp gu là không khả thi và cũng không cần thiết, vì người dùng không bao giờ xem hết được toàn bộ kho phim.

#### **Nếu sai ngược lại thì chuyện gì xảy ra?**
* **Nếu chọn Recall nhưng Low Precision:** Agent sẽ cố gắng "vét" toàn bộ các phim có một chút liên quan đến yêu cầu. Kết quả là danh sách trả về quá dài, chứa nhiều phim "rác" hoặc phim không chất lượng. Người dùng phải tự lọc lại một lần nữa $\rightarrow$ Agent trở nên vô dụng vì không giúp tiết kiệm thời gian.
* **Hậu quả:** Người dùng cảm thấy bị "spam" thông tin, dẫn đến hiện tượng **Choice Overload** (quá tải lựa chọn) và cuối cùng là bỏ ứng dụng.

---

### 2. Bảng chỉ số đánh giá (Eval Metrics + Threshold)

Đối với một Agent, chúng ta không chỉ đo lường độ chính xác của mô hình AI mà còn phải đo lường chất lượng của câu trả lời.

| Metric | Threshold (Ngưỡng đạt) | Red flag (Dừng/Sửa khi) | Giải thích |
| :--- | :--- | :--- | :--- |
| **Precision@5** | $\ge 80\%$ | $< 60\%$ | Trong 5 phim Agent gợi ý, ít nhất 4 phim phải thực sự liên quan đến yêu cầu của User. |
| **nDCG (Normalized Discounted Cumulative Gain)** | $\ge 0.85$ | $< 0.70$ | Đo lường xem phim "đúng gu nhất" có được xếp hạng đầu tiên hay không. Thứ tự hiển thị rất quan trọng. |
| **MRR (Mean Reciprocal Rank)** | $\ge 0.75$ | $< 0.50$ | Vị trí trung bình của bộ phim người dùng thực sự chọn. Nếu User luôn phải kéo xuống dưới cùng mới thấy phim hay $\rightarrow$ Fail. |
| **Hallucination Rate (Tỷ lệ ảo tưởng)** | $< 2\%$ | $> 5\%$ | Agent bịa ra tên phim không có trong Dataset Netflix 2025. Đây là lỗi nghiêm trọng nhất của LLM Agent. |
| **Response Latency (Độ trễ)** | $< 3s$ | $> 7s$ | Thời gian từ lúc User hỏi đến khi Agent trả lời. Quá 7 giây người dùng sẽ mất kiên nhẫn. |
| **Diversity Score (Độ đa dạng)** | $\ge 0.6$ | $< 0.3$ | Tránh việc Agent chỉ gợi ý đi gợi ý lại các phim quá nổi tiếng (như *Squid Game* hay *Stranger Things*) cho mọi User. |

