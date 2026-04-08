# 1. AI Product Canvas

## Sản phẩm: Netflix Q&A Chatbot

|  | Value | Trust | Feasibility |
|---|---|---|---|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | **User**: người dùng nền tảng xem phim trực tuyến, đặc biệt là người mở app nhưng chưa biết xem gì.<br><br>**Pain**: mất nhiều thời gian lướt danh mục, khó diễn đạt nhu cầu bằng filter thường, dễ bị “decision fatigue”. Nhiều nhu cầu rất mơ hồ như “phim nhẹ nhàng trước khi ngủ”, “phim giống Dark nhưng dễ hiểu hơn”, “phim gia đình cuối tuần”.<br><br>**AI giải gì**: chatbot giúp user mô tả nhu cầu bằng ngôn ngữ tự nhiên, sau đó trả về danh sách phim/series phù hợp nhanh hơn, có giải thích ngắn gọn vì sao được gợi ý. Mục tiêu là giảm thời gian tìm phim và tăng tỷ lệ bấm Play. | **Khi AI sai**: bot có thể hiểu sai mood, gợi ý phim không hợp độ tuổi, hoặc trả về phim không đủ khớp nhu cầu. Trường hợp nguy hiểm nhất là gợi ý phim không có trong catalog hiện tại hoặc trả lời quá tự tin nhưng sai.<br><br>**User sửa thế nào**: user có thể bấm “Không đúng ý”, chọn lại tiêu chí nhanh như “ít bạo lực hơn”, “mới hơn”, “đừng là series”, hoặc chọn một trong vài intent gợi ý sẵn. Nếu bot không chắc, bot phải hỏi lại ngắn gọn thay vì tự đoán.<br><br>**Recovery tốt**: sửa càng ít bước càng tốt, tốt nhất là 1 click hoặc 1 câu follow-up. | **Cost**: mỗi lượt chat có chi phí suy luận + retrieval; cần giới hạn số turn và số item trả về để tránh cost tăng mạnh. Với MVP, nên tối ưu bot thành lớp discovery ngắn thay vì hội thoại dài.<br><br>**Latency**: nên dưới ~2 giây; nếu quá chậm user sẽ quay lại browsing thủ công.<br><br>**Risk chính**: hallucination; gợi ý phim ngoài catalog; sai profile/kids safety; retrieval không đủ tốt cho các nhu cầu mơ hồ; chi phí cao nếu mở hội thoại dài; learning signal nhiễu vì watch time không phải lúc nào cũng phản ánh đúng chất lượng gợi ý. |

**Automation hay augmentation?**  
- [ ] Automation  
- [x] Augmentation  

**Justify:** Augmentation hợp lý hơn vì việc chọn phim là quyết định mang tính sở thích và ngữ cảnh. User nên thấy gợi ý, xem lý do, rồi chọn hoặc sửa lại. Cost of reject thấp nếu bot chỉ đóng vai trò hỗ trợ khám phá nội dung, không tự quyết định thay user.

---

## Learning signal

1. **User correction đi vào đâu?**  
   Đi vào:
   - log truy vấn ban đầu + truy vấn sau khi sửa
   - các nút feedback như 👍 / 👎 / “Không đúng ý”
   - các refinement như “ít bạo lực hơn”, “mới hơn”, “phim giống X hơn”
   - tín hiệu phim nào được click / play / add to My List sau câu trả lời  
   Các correction này trước hết nên dùng để cải thiện **retrieval, ranking, prompt pattern và UX flow**, chưa nên coi là ground truth tuyệt đối để fine-tune model ngay.

2. **Product thu signal gì để biết tốt lên hay tệ đi?**  
   Một số signal chính:
   - tỷ lệ user bấm **Play** từ giao diện chat
   - thời gian từ lúc mở chat đến lúc chọn được phim
   - số lần phải reformulate query trước khi chọn được nội dung
   - tỷ lệ user bấm “Không đúng ý”
   - tỷ lệ user bỏ chat và quay lại browse thủ công
   - tỷ lệ add vào **My List**
   - tỷ lệ không tương tác với bất kỳ gợi ý nào  
   Lưu ý: đây là **proxy signals**, cần kết hợp nhiều tín hiệu; không nên dùng một chỉ số đơn lẻ như watch time > 10 phút để kết luận bot tốt.

3. **Data thuộc loại nào?**  
   - [x] User-specific  
   - [x] Domain-specific  
   - [x] Real-time  
   - [ ] Human-judgment  
   - [x] Khác: interaction logs / catalog availability / profile safety constraints  

   **Có marginal value không?**  
   Có. Dữ liệu này có marginal value vì:
   - lịch sử xem và profile giúp cá nhân hóa tốt hơn cho từng user
   - catalog availability theo quốc gia/thời điểm là dữ liệu động, model nền không tự biết chính xác
   - correction trong ngữ cảnh sản phẩm giúp cải thiện retrieval/ranking cho đúng use case discovery
   - các refinement như “đừng là series”, “ít máu me hơn”, “xem trước khi ngủ” phản ánh nhu cầu thực tế rất đặc thù mà model tổng quát không nắm chắc nếu không có signal từ sản phẩm


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

## Phân Công
- Hoàng Đức Hưng: Canvas