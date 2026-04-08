# AI PRODUCT CANVAS: Netflix Q&A Chatbot (NGƯỜI LÀM: HOÀNG ĐỨC HƯNG)

## 1. Đánh giá nhanh

Bản canvas ban đầu **đúng hướng và khá tốt** ở 4 phần cốt lõi:

- **Value**: nêu đúng pain point và value cho cả user lẫn business
- **Trust**: chạm đúng rủi ro lớn nhất của chatbot phim là **hallucination + recommendation sai ngữ cảnh**
- **Feasibility**: chọn đúng hướng kỹ thuật là **RAG + filter metadata**
- **Learning signal**: đã phân biệt được **explicit** và **implicit**

Tuy nhiên, để dùng cho học tập, pitching, hoặc thảo luận sản phẩm, bản này vẫn còn vài điểm cần chỉnh để chặt hơn và hợp lý hơn.

---

## 2. Những điểm đang ổn

### 2.1. Value rõ
Bạn xác định đúng vấn đề: user không chỉ “thiếu phim để xem”, mà là **khó ra quyết định**. Đây là pain point rất thật.

### 2.2. Trust đi đúng trọng tâm
Bạn đã nhìn ra điều rất quan trọng: chatbot phim mà gợi ý **phim không có trên nền tảng**, hoặc **không đúng profile**, thì user mất niềm tin rất nhanh.

### 2.3. Feasibility có tư duy hệ thống
Bạn không nói chung chung “dùng AI”, mà đã nghĩ đến:
- nguồn data
- latency
- cost
- kiến trúc retrieval

### 2.4. Learning signal có thể dùng được
Bạn đã nêu được các tín hiệu hành vi sau gợi ý, đây là phần nhiều người hay bỏ sót.

---

## 3. Những điểm chưa hợp lý hoặc chưa đủ

### 3.1. Phần Value đang hơi solution-first
Bạn đang mô tả chatbot như một “chuyên gia điện ảnh”, nghe hay nhưng hơi lý tưởng hóa.

Thực tế hơn, nên framing sản phẩm này là:

> một lớp conversational discovery giúp user đi từ nhu cầu mơ hồ đến lựa chọn xem phù hợp nhanh hơn.

### 3.2. Business Value cần tránh claim quá mạnh
Các ý như:
- tăng retention rate
- tăng watch time
- hồi sinh phim cũ

đều là **giả thuyết kinh doanh**, chưa phải kết quả chắc chắn. Nên viết theo hướng:
- kỳ vọng cải thiện
- metrics cần kiểm chứng bằng experiment

### 3.3. Explainability không nên quá định lượng giả
Câu như:

> “khớp 95% với lịch sử xem của bạn”

nghe không tự nhiên và dễ tạo cảm giác chính xác giả. Tốt hơn là lý do ngắn, dễ hiểu:

- “Vì bạn thích sci-fi pha bí ẩn”
- “Vì phim này có nhịp vừa phải và ít bạo lực hơn”

### 3.4. “Zero-hallucination” là mục tiêu, không nên hứa tuyệt đối
Thay vì khẳng định tuyệt đối, nên viết:
- bot chỉ được trả lời dựa trên catalog hiện có
- nếu không chắc, bot phải nói không tìm thấy kết quả phù hợp
- bot đề xuất user nới tiêu chí thay vì bịa câu trả lời

### 3.5. Feasibility đang thiếu scope MVP
Hiện tại ý tưởng đang ôm khá nhiều:
- tìm phim theo mood
- hiểu ngôn ngữ mơ hồ
- dùng lịch sử xem
- giải thích lý do
- nhận diện kids profile
- xử lý license theo quốc gia

Cần tách rõ:

**MVP nên làm**
- discovery trong catalog hiện có
- tìm theo thể loại / mood đơn giản
- tìm phim giống phim đã biết
- tìm phim theo ràng buộc cơ bản
- hỏi thông tin ngắn về phim đang có trên nền tảng

**Chưa nên làm ở MVP**
- hội thoại dài nhiều bước quá sâu
- cá nhân hóa quá mạnh
- tranh luận / review phim dài
- trả lời kiến thức phim ngoài catalog

### 3.6. Learning Signal cần chặt hơn
Ví dụ:
- `watch time > 10 phút = gợi ý đúng` chưa chắc
- `thoát trong 2 phút = gợi ý sai` cũng chưa chắc

Đây chỉ nên coi là **proxy signal**, cần kết hợp nhiều tín hiệu thay vì dựa vào một chỉ số đơn lẻ.

### 3.7. Thiếu Failure mode / fallback
Đây là phần rất quan trọng.

Bot cần có cách xử lý khi:
- không hiểu query
- không có phim khớp
- user không muốn chat tiếp
- bot gợi ý nhưng user chưa hài lòng

---

## 4. Phiên bản đã sửa

## 4.1. Value (Giá trị cốt lõi)

**Vấn đề giải quyết:**  
Người dùng nền tảng xem phim trực tuyến thường mất nhiều thời gian để quyết định xem gì tiếp theo. Họ phải lướt qua quá nhiều lựa chọn, trong khi nhu cầu thực tế lại thường mơ hồ và mang tính ngữ cảnh, ví dụ như: “muốn xem phim nhẹ nhàng trước khi ngủ”, “muốn phim giống Dark nhưng dễ hiểu hơn”, hoặc “muốn xem gì đó cho cả gia đình cuối tuần”.

**User Value (Giá trị cho người dùng):**
- Giảm thời gian từ lúc mở ứng dụng đến lúc chọn được nội dung để xem.
- Cho phép người dùng diễn đạt nhu cầu bằng ngôn ngữ tự nhiên thay vì phải tự lọc qua danh mục.
- Hỗ trợ các nhu cầu mơ hồ hoặc khó biểu đạt bằng filter truyền thống, như mood, pacing, mức độ bạo lực, hoặc kiểu trải nghiệm mong muốn.

**Business Value (Giá trị cho doanh nghiệp):**
- Tăng tỷ lệ người dùng bắt đầu phát nội dung sau khi khám phá.
- Giảm tình trạng rời ứng dụng vì không tìm được phim phù hợp.
- Tăng khả năng khám phá catalog sâu hơn, bao gồm cả nội dung ngách hoặc ít được hiển thị ở các hàng đề xuất mặc định.
- Tạo thêm một giao diện khám phá nội dung mới bên cạnh search và recommendation feed truyền thống.

---

## 4.2. Trust (Độ tin cậy & an toàn)

**Rào cản lòng tin:**  
Người dùng sẽ nhanh chóng mất niềm tin nếu chatbot:
- gợi ý phim không có trên nền tảng,
- hiểu sai nhu cầu,
- đưa ra phim không phù hợp với độ tuổi hoặc profile,
- hoặc trả lời rất tự tin nhưng thực chất sai dữ liệu.

**Nguyên tắc xây dựng lòng tin:**
- **Grounded responses:** bot chỉ được trả lời dựa trên catalog hiện có của nền tảng ở thị trường của người dùng.
- **No-answer is better than fake-answer:** nếu không tìm thấy kết quả phù hợp, bot phải nói rõ và đề xuất nới tiêu chí thay vì bịa ra câu trả lời.
- **Explainable recommendation:** mỗi gợi ý nên có lý do ngắn, dễ hiểu, ví dụ:  
  “Gợi ý này phù hợp vì bạn muốn phim trinh thám nhưng không quá nặng nề và có nhịp xem vừa phải.”
- **Profile-aware safety:** nếu là Kids Profile, bot chỉ truy xuất và gợi ý từ tập nội dung an toàn cho trẻ em.
- **Consistency:** tiêu đề, rating, thể loại, thời lượng, availability phải khớp với dữ liệu thật trên hệ thống.

---

## 4.3. Feasibility (Tính khả thi)

**Dữ liệu khả dụng:**
- Metadata phim/series: tiêu đề, thể loại, mô tả, cast, đạo diễn, năm phát hành, rating, thời lượng, quốc gia, tags.
- Dữ liệu hành vi cơ bản: lịch sử xem, My List, lượt click Play, lượt bỏ dở.
- Dữ liệu ngữ cảnh hệ thống: profile hiện tại, ngôn ngữ, quốc gia, loại thiết bị.

**Kiến trúc đề xuất:**
- Dùng **RAG** để chatbot không sinh câu trả lời tự do từ trí nhớ mô hình.
- Lớp retrieval gồm:
  - **metadata filtering** cho các điều kiện cứng như rating, năm, thể loại, availability
  - **semantic retrieval / vector search** cho các nhu cầu mềm như mood, vibe, nhịp phim, hoặc “giống phim X”
- Lớp generation có nhiệm vụ:
  - diễn giải nhu cầu user
  - tổng hợp và trình bày danh sách gợi ý
  - đưa ra lý do gợi ý ngắn gọn

**Ràng buộc kỹ thuật:**
- Latency cần thấp, tốt nhất trong khoảng 1–2 giây.
- Cần giới hạn độ dài hội thoại và số lượng item trả về để kiểm soát cost.
- Cần cache cho các truy vấn phổ biến như:
  - “phim hài nhẹ nhàng”
  - “phim gia đình cuối tuần”
  - “phim giống Stranger Things”

**Phạm vi MVP đề xuất:**
- Chỉ hỗ trợ discovery trong catalog hiện có
- Chỉ xử lý 4 nhóm intent đầu tiên:
  1. tìm theo thể loại / mood
  2. tìm phim giống phim đã biết
  3. tìm phim theo ràng buộc đơn giản
  4. hỏi thông tin ngắn về phim đang có trên nền tảng

**Chưa nên làm ở MVP:**
- hội thoại dài nhiều bước quá sâu
- cá nhân hóa quá mạnh dựa trên toàn bộ lịch sử xem
- tranh luận, review phim dài kiểu “movie companion”
- trả lời kiến thức phim ngoài catalog nền tảng

---

## 4.4. Learning Signal (Tín hiệu học hỏi)

**Mục tiêu:**  
Dùng phản hồi người dùng để cải thiện retrieval, ranking và UX flow của chatbot theo thời gian.

**Explicit signals (tín hiệu chủ động):**
- Nút 👍 / 👎 cho câu trả lời
- Nút “Không đúng ý, thử lại”
- User sửa lại truy vấn, ví dụ:
  - “ít bạo lực hơn”
  - “đừng là series”
  - “phim mới hơn”
- User chọn trực tiếp một phim trong danh sách bot gợi ý

**Implicit signals (tín hiệu hành vi):**
- Tích cực:
  - user bấm Play từ kết quả chat
  - user thêm phim vào My List
  - user không cần reformulate query thêm
  - user xem đủ một khoảng meaningful sau khi chọn từ chat
- Tiêu cực:
  - user liên tục hỏi lại với tiêu chí khác vì bot chưa hiểu
  - user bỏ chat và quay lại browse thủ công
  - user bấm vào gợi ý nhưng thoát rất sớm nhiều lần liên tiếp
  - user không tương tác với bất kỳ gợi ý nào

**Lưu ý:**  
Các tín hiệu hành vi này chỉ là **proxy**, không phải ground truth. Cần kết hợp nhiều tín hiệu để đánh giá chất lượng recommendation thay vì dựa vào một chỉ số đơn lẻ.

---

## 4.5. Failure Modes / Fallbacks

**Khi bot không hiểu truy vấn:**
- hỏi lại bằng câu ngắn
- đề xuất 2–3 hướng chọn nhanh

Ví dụ:  
“Bạn muốn phim nhẹ nhàng, gay cấn, hay cảm động?”

**Khi không có phim khớp hoàn toàn:**
- nói rõ không có kết quả đúng 100%
- gợi ý nới lỏng một tiêu chí

Ví dụ:  
“Hiện chưa có phim Bắc Âu đúng yêu cầu này. Bạn có muốn mở rộng sang phim châu Âu cùng vibe không?”

**Khi user không muốn chat tiếp:**
- cho phép chuyển ngay sang danh sách click-able
- giữ bot như lớp hỗ trợ, không thay thế hoàn toàn browsing UI

---

## 5. Kết luận

Canvas ban đầu của bạn **đúng hướng và có nền khá tốt**. Sau khi sửa, bản này chặt hơn ở 4 điểm quan trọng:

1. Giảm bớt ngôn ngữ quá lý tưởng, tăng tính thực tế sản phẩm  
2. Tách rõ giả thuyết kinh doanh với kết quả cần kiểm chứng  
3. Thêm phạm vi MVP rõ ràng  
4. Bổ sung failure modes và fallback

Điểm mạnh nhất của ý tưởng này là nó giải quyết một pain point rất thật: **người dùng biết mình muốn cảm giác gì, nhưng không biết phải bắt đầu tìm từ đâu**.



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







### 6. Mini AI Chatbot Phim Ảnh

## 1. Tổng quan dự án (Overview)
CineMate là một Mini AI Chatbot chuyên biệt, được thiết kế để trở thành một "chuyên gia phim ảnh" cá nhân. Chatbot giúp người dùng tìm kiếm, khám phá và thảo luận về phim thông qua giao diện trò chuyện tự nhiên. Mục tiêu là giải quyết vấn đề "không biết xem gì hôm nay" và cung cấp thông tin phim nhanh chóng, chính xác.

## 2. Đối tượng mục tiêu (Target Audience)
* Người yêu thích phim ảnh (Cinephiles) muốn tìm hiểu sâu về điện ảnh.
* Người dùng thông thường cần gợi ý phim giải trí cuối tuần.
* Người dùng các nền tảng streaming (Netflix, Apple TV, rạp chiếu) cần tra cứu thông tin nhanh.

## 3. Tính năng cốt lõi (Core Features - MVP)
* **Gợi ý phim thông minh (Smart Recommendations):** Đề xuất phim dựa trên thể loại, tâm trạng (mood), diễn viên, đạo diễn, hoặc phim tương tự (VD: *"Gợi ý cho tôi phim hành động giống John Wick nhưng có yếu tố hài hước"*).
* **Tra cứu thông tin chi tiết:** Cung cấp tóm tắt nội dung (không spoiler), điểm đánh giá (IMDb, Rotten Tomatoes, Letterboxd), dàn diễn viên, và năm phát hành.
* **Chỉ điểm nền tảng xem phim:** Cho biết phim hiện đang chiếu rạp hay có sẵn trên nền tảng streaming nào tại Việt Nam.
* **Giải đáp kiến thức điện ảnh (Movie Trivia/Q&A):** Trả lời các câu hỏi về giải thích cái kết (ending explanation), easter eggs, hoặc thông tin hậu trường.

## 4. Yêu cầu kỹ thuật (Technical Architecture)
* **AI Engine / LLM:** Sử dụng các mô hình ngôn ngữ lớn (như Gemini Flash hoặc GPT-4o-mini) để xử lý ngôn ngữ tự nhiên, tối ưu chi phí và tốc độ phản hồi.
* **Kiến trúc RAG (Retrieval-Augmented Generation):**
    * **Cơ sở dữ liệu (Vector DB):** Sử dụng Pinecone hoặc Milvus để lưu trữ vector hóa dữ liệu kịch bản và tóm tắt phim.
    * **Nguồn dữ liệu API:** Tích hợp TMDB API (The Movie Database), OMDb API để cập nhật dữ liệu phim realtime.
* **Nền tảng triển khai (Platforms):** Tích hợp dưới dạng Web Widget, Telegram Bot và Facebook Messenger.

## 5. Yêu cầu Giao diện (UI/UX)
* Hỗ trợ hiển thị dạng thẻ (Cards/Carousels) cho kết quả phim (gồm Poster, Tên phim, Điểm số, Nút "Xem trailer").
* Tốc độ phản hồi (Latency): Dưới 2 giây cho mỗi tin nhắn.
* Giọng văn (Tone of voice): Thân thiện, hài hước, và đam mê điện ảnh. Có thể thay đổi phong cách nói chuyện (VD: Giọng châm biếm như Deadpool hoặc nghiêm túc như nhà phê bình).

## 6. Tiêu chí thành công (Success Metrics - KPIs)
* **Độ chính xác (Accuracy):** Tỷ lệ ảo giác AI (Hallucination rate) liên quan đến thông tin phim < 5%.
* **Mức độ tương tác:** Trung bình > 5 tin nhắn mỗi phiên trò chuyện (Session length).
* **Tỷ lệ chuyển đổi (CTR):** > 10% người dùng click vào link xem trailer hoặc link nền tảng streaming.