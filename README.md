# Netflix Q&A Chatbot - Nhóm 08

## Đề Tài

**Netflix Q&A Chatbot** - một chatbot hội thoại giúp người dùng Netflix khám phá và chọn phim nhanh chóng và chính xác.

## Giới Thiệu Sơ Qua

Hiện tại, người dùng Netflix gặp khó khăn trong việc tìm phim phù hợp từ catalog khổng lồ. Không chỉ thiếu phim để xem, họ cần sự hỗ trợ để **đi từ nhu cầu mơ hồ đến lựa chọn xem cụ thể** nhanh chóng.

Chatbot này hoạt động như một lớp **conversational discovery**:
- Người dùng mô tả nhu cầu của mình (tâm trạng, thể loại, độ dài, v.v.)
- Bot tìm kiếm trong catalog hiện có và gợi ý phim phù hợp
- Bot giải thích lý do gợi ý bằng cách dễ hiểu
- Bot chỉ gợi ý phim **có sẵn trên nền tảng**, tránh hallucination

### Giá Trị Chính
- **Cho Người Dùng**: Tiết kiệm thời gian, giảm quyết định mệt mỏi, khám phá phim mới
- **Cho Business**: Cải thiện engagement, tăng watch time, hồi sinh nội dung cũ

---

## MVP (Minimum Viable Product)

### Tính Năng Chính
1. **Tìm kiếm phim theo mood/thể loại**: "Tôi muốn xem phim hành động nhanh nhịp" → gợi ý danh sách
2. **Tìm phim tương tự**: "Tôi thích phim này, có gợi ý gì tương tự?" 
3. **Tìm phim với điều kiện**: "Phim khoa học viễn tưởng dưới 90 phút"
4. **Hỏi thông tin phim**: "Phim này có dùng được cho trẻ em không?"
5. **Giải thích lý do gợi ý**: "Vì bạn thích sci-fi pha bí ẩn"

### Ràng Buộc
- Bot chỉ gợi ý từ catalog hiện có trên Netflix
- Không support hội thoại multi-turn quá sâu
- Tránh lý do gợi ý quá định lượng giả (ví dụ: "khớp 95%")
- Khi không chắc, bot phải nói không tìm thấy thay vì bịa câu trả lời



### Metrics Kiểm Chứng
- **Click-through rate**: Tỉ lệ user click vào gợi ý
- **Watch time > 10 phút**: Proxy signal cho gợi ý đúng
- **User retention**: Người dùng quay lại dùng chatbot

---

## Thành Viên
- Người Làm: Hoàng Đức Hưng
