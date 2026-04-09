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
  
# 2. User Stories × 4 Paths (Netflix Q&A Chatbot)

* **Happy Path (Đúng nhu cầu - Phản hồi chính xác):**
    * **User:** "Tìm cho tôi một bộ phim trinh thám hack não giống *Dark* nhưng nội dung dễ hiểu hơn một chút."
    * **AI Agent:** Hệ thống truy vấn tập dữ liệu, trích xuất metadata và trả về kết quả: "Dựa trên sở thích về sự bí ẩn của *Dark*, bạn có thể thử *1899* hoặc *Bodies*. Cả hai đều có yếu tố du hành thời gian nhưng mạch phim trực diện hơn."
    * **Kết quả:** User hài lòng, bấm **Play** ngay trên thẻ phim. (Đạt mục tiêu tăng tỷ lệ xem).

* **Low-confidence Path (Mơ hồ - Cần làm rõ):**
    * **User:** "Gợi ý cho tôi phim nào hay hay để xem cuối tuần."
    * **AI Agent:** Nhận diện Intent quá rộng (Confidence < 60%). Thay vì đoán mò, bot phản hồi: "Để tìm được đúng phim bạn thích, bạn muốn một bộ phim lẻ để giải trí nhanh hay một series dài tập để 'cày' suốt cuối tuần? Bạn thích cảm giác nhẹ nhàng hay kịch tính?"
    * **Kết quả:** User cung cấp thêm thông tin "Phim lẻ, hài hước", giúp Agent thu hẹp phạm vi tìm kiếm và đạt Precision cao hơn.

* **Failure Path (Lỗi/Ngoài phạm vi - Fallback):**
    * **User:** "Đặt cho tôi một chiếc Pizza đến địa chỉ nhà hiện tại."
    * **AI Agent:** Nhận diện yêu cầu nằm ngoài phạm vi tư vấn phim (Out-of-scope).
    * **AI Agent:** "Xin lỗi, tôi là chuyên gia phim ảnh CineMate, tôi không có chức năng đặt đồ ăn. Tuy nhiên, nếu bạn muốn vừa ăn Pizza vừa xem phim về ẩm thực, tôi gợi ý bộ phim *Chef's Table* rất thú vị!"
    * **Kết quả:** Tránh được lỗi Hallucination (ảo giác) và quay lại đúng vai trò Augmentation.

* **Correction Path (User sửa lỗi - Cải thiện tín hiệu):**
    * **User:** "Gợi ý phim hành động cho trẻ em xem cùng gia đình."
    * **AI Agent:** Đưa ra danh sách phim hành động, nhưng có một phim nhãn R (18+).
    * **User:** Bấm nút **"Không đúng ý"** và nhắn: "Phim này bạo lực quá, tôi cần phim nhãn PG-13."
    * **AI Agent:** Kích hoạt Metadata Filtering, loại bỏ ngay các phim nhãn R và cập nhật: "Tôi đã hiểu, đây là danh sách phim hành động phiêu lưu phù hợp cho trẻ em (PG-13) như *The Sea Beast* hoặc *Spy Kids*."
    * **Kết quả:** User nhận được kết quả đúng sau 1 bước sửa; hệ thống lưu log để cải thiện thuật toán Ranking sau này.

# 3. Eval metrics + threshold

## Optimize Precision hay Recall?

**Lựa chọn:** **[x] Precision**

### **Tại sao?**
Trong bài toán hệ thống khuyến nghị (Recommendation System) và Agent tư vấn, **Precision (Độ chính xác)** quan trọng hơn vì:
* **Trải nghiệm người dùng:** Người dùng chỉ có thời gian xem 1-2 bộ phim mỗi tối. Nếu Agent đề xuất 5 phim và cả 5 đều đúng gu (High Precision), người dùng sẽ tin tưởng Agent tuyệt đối. 
* **Chi phí của sự sai lầm (Cost of False Positive):** Nếu Agent khẳng định "Bộ phim này chắc chắn bạn sẽ thích" nhưng khi bật lên lại cực kỳ tệ so với gu của họ, người dùng sẽ cảm thấy bị lừa và mất thời gian.
* **Đặc thù Dataset:** Dataset Netflix có hàng ngàn phim. Việc tìm bằng hết (Recall) tất cả các phim hợp gu là không khả thi và cũng không cần thiết, vì người dùng không bao giờ xem hết được toàn bộ kho phim.

#### **Nếu sai ngược lại thì chuyện gì xảy ra?**
* **Nếu chọn Recall nhưng Low Precision:** Agent sẽ cố gắng "vét" toàn bộ các phim có một chút liên quan đến yêu cầu. Kết quả là danh sách trả về quá dài, chứa nhiều phim "rác" hoặc phim không chất lượng. Người dùng phải tự lọc lại một lần nữa $\rightarrow$ Agent trở nên vô dụng vì không giúp tiết kiệm thời gian.
* **Hậu quả:** Người dùng cảm thấy bị "spam" thông tin, dẫn đến hiện tượng **Choice Overload** (quá tải lựa chọn) và cuối cùng là bỏ ứng dụng.

---

## Bảng chỉ số đánh giá (Eval Metrics + Threshold)

Đối với một Agent, chúng ta không chỉ đo lường độ chính xác của mô hình AI mà còn phải đo lường chất lượng của câu trả lời.

| Metric | Threshold (Ngưỡng đạt) | Red flag (Dừng/Sửa khi) | Giải thích |
| :--- | :--- | :--- | :--- |
| **Precision@5** | $\ge 80\%$ | $< 60\%$ | Trong 5 phim Agent gợi ý, ít nhất 4 phim phải thực sự liên quan đến yêu cầu của User. |
| **nDCG (Normalized Discounted Cumulative Gain)** | $\ge 0.85$ | $< 0.70$ | Đo lường xem phim "đúng gu nhất" có được xếp hạng đầu tiên hay không. Thứ tự hiển thị rất quan trọng. |
| **MRR (Mean Reciprocal Rank)** | $\ge 0.75$ | $< 0.50$ | Vị trí trung bình của bộ phim người dùng thực sự chọn. Nếu User luôn phải kéo xuống dưới cùng mới thấy phim hay $\rightarrow$ Fail. |
| **Hallucination Rate (Tỷ lệ ảo tưởng)** | $< 2\%$ | $> 5\%$ | Agent bịa ra tên phim không có trong Dataset Netflix 2025. Đây là lỗi nghiêm trọng nhất của LLM Agent. |
| **Response Latency (Độ trễ)** | $< 3s$ | $> 7s$ | Thời gian từ lúc User hỏi đến khi Agent trả lời. Quá 7 giây người dùng sẽ mất kiên nhẫn. |
| **Diversity Score (Độ đa dạng)** | $\ge 0.6$ | $< 0.3$ | Tránh việc Agent chỉ gợi ý đi gợi ý lại các phim quá nổi tiếng (như *Squid Game* hay *Stranger Things*) cho mọi User. |

# 4. Top 3 Failure Mode
**Failure Mode 1: ảo giác phim không tồn tại**
- Trigger: Người dùng yêu cầu 1 tổ hợp ngách, ví dụ "Gợi ý cho tôi một bộ phim hành động pha hài hước" thực tế trong file không có phim nào thỏa mãn điều kiện
- Consequence: Do bản tính chiều theo người dùng AI tự bịa ra một cái tên mới nghe hợp lý
- Mitigation: Bắt buộc dùng RAG cứng LLM không được phép tự bịa ra tên phim. Output tên phim trước khi hiển thị phải trải qua 1 hàm kiểm tra xem tên phim này có thật sự nằm trong dtb không, nếu không trả về luồng fallback

**Failure mode 2: Bỏ qua các ràng buộc cứng**
- Trigger: Người dùng ra lệnh: "Tôi muốn xem một phim khoa học viễn tưởng, dưới 90 phút, và chỉ dành cho trẻ em (rating PG-13) để xem cùng con
- Consequence: AI tìm thấy một bộ phim khoa học viễn tưởng có độ liên quan ngữ nghĩa cực cao nhưng nó bỏ qua điều kiện thời gian và nhãn dán. Kết quả trả ra phim dài hơn 90 phút hoặc một bộ phim kinh dị, bạo lực.
- Mitigation: Trước khi đem câu hỏi đi tìm kiếm, phải có một bước dùng AI (hoặc quy tắc) trích xuất các điều kiện cứng thành JSON, sử dụng Metadata Filtering trên dataset trước. Dùng code lọc bỏ tất cả phim > 90 phút và phim R-rated khỏi dữ liệu, sau đó AI mới được phép gợi ý các phim còn lại trong rổ

**Failure mode 3: Bị thiên kiến bias vì lạm dụng hành vi người dùng**
- Trigger: Người dùng có lịch sử 6 tháng qua chỉ toàn xem phim ngôn tình Hàn Quốc. Hôm nay họ nhắn với chatbot: "Cuối tuần này tôi đang chán, muốn xem một thể loại gì đó thật mới mẻ, giật gân, đột phá để đổi gió."
- Consequence: thuật toán bị Overfitting (High Bias vào quá khứ), nó đánh trọng số lịch sử quá cao. Kết quả là nó vẫn tiếp tục gợi ý phim tình cảm Hàn Quốc nhưng cố gắng miêu tả là rất đột phá. Bot không bắt được sự thay đổi ý định của người dùng
- Mitigation: Khi User yêu cầu "thể loại mới", Agent tự động gán điểm phạt (Penalty score) cho các phim có Tag trùng với Top 3 thể loại xem nhiều nhất trong lịch sử.


# 5. ROI 3 kịch bản

---

## a. Kịch bản: Conservative (Thận trọng)
**Mục tiêu:** Tăng hiệu suất khai thác kho nội dung (**Inventory Utilization**)

* **Vấn đề:** Người dùng thường chỉ tập trung vào các phim bom tấn mới nổi, khiến hàng ngàn bộ phim cũ hoặc phim độc lập (Indie) dù đã tốn hàng tỷ đô mua bản quyền nhưng bị "đắp chiếu".
* **Giải pháp AI:** Chatbot có khả năng **tìm kiếm ngữ nghĩa**, đưa các bộ phim "ngách" đến đúng người dùng dựa trên yêu cầu cụ thể (VD: *"Phim tâm lý kinh dị bối cảnh Bắc Âu"*).
* **ROI mong đợi:**
    * Tăng tỉ lệ xem các bộ phim ít nổi tiếng.
    * Tối ưu hóa chi phí bản quyền đã đầu tư, tránh việc phải chi thêm tiền mua phim mới liên tục khi kho phim cũ vẫn còn giá trị khai thác.

---

## b. Kịch bản: Realistic (Khả thi)
**Mục tiêu:** Tăng tổng thời gian sử dụng App (**Daily Watch Time**)

* **Vấn đề:** **"Nghịch lý lựa chọn"** khiến người dùng mất quá nhiều thời gian để lướt tìm phim. Đôi khi dành 30 phút chỉ để chọn phim rồi thoát App vì mệt mỏi (**Bounce rate cao**).
* **Giải pháp AI:** Rút ngắn quy trình từ lúc nảy sinh ý tưởng đến lúc phim bắt đầu chạy. AI đóng vai trò như một người bạn "sành phim" tư vấn ngay lập tức, giúp người dùng ra quyết định nhanh hơn.
* **ROI mong đợi:**
    * **Giảm thời gian tìm kiếm** phim đáng kể.
    * Tăng thời gian xem phim/ngày trên mỗi người dùng. Thời gian xem càng nhiều, **giá trị vòng đời khách hàng (LTV)** càng cao.

---

## c. Kịch bản: Optimistic (Lạc quan)
**Mục tiêu:** Giảm tỉ lệ rời bỏ dịch vụ (**Churn Rate**)

* **Vấn đề:** Khách hàng hủy gói cước vì cảm thấy *"Nền tảng không còn gì hay cho mình nữa"* – một sự đứt gãy về cảm xúc với dịch vụ.
* **Giải pháp AI:** Chatbot tạo ra sự **kết nối cá nhân hóa cao độ**. AI nhớ lịch sử xem phim và gu của khách hàng. Mỗi lần họ quay lại và hỏi *"Tối nay xem gì cho vui?"*, họ nhận được một câu trả lời mới mẻ và thú vị mà thuật toán cuộn trang thông thường không làm được.
* **ROI mong đợi:**
    * **Giảm tỉ lệ hủy gói cước (Churn rate).**
    * Với quy mô lớn, chỉ cần giảm **1% tỉ lệ hủy** đã tương đương với việc giữ lại hàng trăm triệu USD doanh thu mỗi năm mà không tốn thêm chi phí marketing tìm khách mới.


# 6. Mini AI Chatbot Phim Ảnh

## Tổng quan dự án (Overview)
CineMate là một Mini AI Chatbot chuyên biệt, được thiết kế để trở thành một "chuyên gia phim ảnh" cá nhân. Chatbot giúp người dùng tìm kiếm, khám phá và thảo luận về phim thông qua giao diện trò chuyện tự nhiên. Mục tiêu là giải quyết vấn đề "không biết xem gì hôm nay" và cung cấp thông tin phim nhanh chóng, chính xác.

## 2. Đối tượng mục tiêu (Target Audience)
* Người yêu thích phim ảnh (Cinephiles) muốn tìm hiểu sâu về điện ảnh.
* Người dùng thông thường cần gợi ý phim giải trí cuối tuần.
* Người dùng các nền tảng streaming (Netflix, Apple TV, rạp chiếu) cần tra cứu thông tin nhanh.

## Tính năng cốt lõi (Core Features - MVP)
* **Gợi ý phim thông minh (Smart Recommendations):** Đề xuất phim dựa trên thể loại, tâm trạng (mood), diễn viên, đạo diễn, hoặc phim tương tự (VD: *"Gợi ý cho tôi phim hành động giống John Wick nhưng có yếu tố hài hước"*).
* **Tra cứu thông tin chi tiết:** Cung cấp tóm tắt nội dung (không spoiler), điểm đánh giá (IMDb, Rotten Tomatoes, Letterboxd), dàn diễn viên, và năm phát hành.
* **Chỉ điểm nền tảng xem phim:** Cho biết phim hiện đang chiếu rạp hay có sẵn trên nền tảng streaming nào tại Việt Nam.
* **Giải đáp kiến thức điện ảnh (Movie Trivia/Q&A):** Trả lời các câu hỏi về giải thích cái kết (ending explanation), easter eggs, hoặc thông tin hậu trường.

## Yêu cầu kỹ thuật (Technical Architecture)
* **AI Engine / LLM:** Sử dụng các mô hình ngôn ngữ lớn (như Gemini Flash hoặc GPT-4o-mini) để xử lý ngôn ngữ tự nhiên, tối ưu chi phí và tốc độ phản hồi.
* **Kiến trúc RAG (Retrieval-Augmented Generation):**
    * **Cơ sở dữ liệu (Vector DB):** Sử dụng Pinecone hoặc Milvus để lưu trữ vector hóa dữ liệu kịch bản và tóm tắt phim.
    * **Nguồn dữ liệu API:** Tích hợp TMDB API (The Movie Database), OMDb API để cập nhật dữ liệu phim realtime.
* **Nền tảng triển khai (Platforms):** Tích hợp dưới dạng Web Widget, Telegram Bot và Facebook Messenger.

## Yêu cầu Giao diện (UI/UX)
* Hỗ trợ hiển thị dạng thẻ (Cards/Carousels) cho kết quả phim (gồm Poster, Tên phim, Điểm số, Nút "Xem trailer").
* Tốc độ phản hồi (Latency): Dưới 2 giây cho mỗi tin nhắn.
* Giọng văn (Tone of voice): Thân thiện, hài hước, và đam mê điện ảnh. Có thể thay đổi phong cách nói chuyện (VD: Giọng châm biếm như Deadpool hoặc nghiêm túc như nhà phê bình).

## Tiêu chí thành công (Success Metrics - KPIs)
* **Độ chính xác (Accuracy):** Tỷ lệ ảo giác AI (Hallucination rate) liên quan đến thông tin phim < 5%.
* **Mức độ tương tác:** Trung bình > 5 tin nhắn mỗi phiên trò chuyện (Session length).
* **Tỷ lệ chuyển đổi (CTR):** > 10% người dùng click vào link xem trailer hoặc link nền tảng streaming.

- Mitigation: Trong Prompt hệ thống, cần thiết lập quy tắc khi phát hiện từ khóa "đổi gió, mới mẻ, khác biệt, khác", hệ thống phải giảm trọng số lịch sử người dùng xuống 0% và kích hoạt thuật toán gợi ý ngẫu nhiên có kiểm soát hoặc gợi ý các phim "Trending Top 10" nằm ngoài cụm sở thích thường ngày của họ

# Phân Công
- Hoàng Đức Hưng: Canvas
- Lê Hồng Anh: User Stories × 4 Paths
- Nguyễn Hoàng Việt Hùng: Eval metrics và Threshold
- Nguyễn Thị Hương Giang: Top 3 Failure
- Mai Việt Hoàng: 3 ROI