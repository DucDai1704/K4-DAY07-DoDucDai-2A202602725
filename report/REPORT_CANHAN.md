# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đỗ Đức Đại
**MaSV**: 2A202602725
**Nhóm:** G43
**Ngày:** 19/9/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Khi độ tương tự Cosine cao (gần bằng 1), điều đó có nghĩa là 2 vector đang chỉ về cùng một hướng trong không gian đa chiều, tức là hai đoạn văn bản có ý nghĩa (ngữ nghĩa) rất giống nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi rất thích ăn món phở bò truyền thống."
- Câu B: "Món tủ của tôi chính là phở bò hầm xương."
- Tại sao tương đồng: Dù dùng các từ vựng khác nhau ("rất thích ăn" vs "món tủ"), nhưng ý nghĩa chung đều diễn đạt sự yêu thích đối với món phở bò. Embeddings bắt được ngữ nghĩa này.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi rất thích ăn món phở bò truyền thống."
- Câu B: "Hôm nay giá vàng thế giới tăng kỷ lục."
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác biệt (ẩm thực vs tài chính), vector của chúng sẽ vuông góc hoặc chỉ về các hướng khác nhau trong không gian.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Khoảng cách Euclid bị ảnh hưởng rất nhiều bởi độ lớn (magnitude) của vector (thường do độ dài câu quyết định). Cosine similarity chỉ quan tâm đến góc (hướng) giữa 2 vector, giúp so sánh chính xác ý nghĩa ngữ nghĩa của một câu ngắn và một đoạn văn dài mà không bị nhiễu bởi độ dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Công thức = ceil((độ_dài_tài_liệu - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Số lượng chunk sẽ tăng lên (thành ceil(9900/400) = 25 chunks). Ta muốn tăng overlap để tránh việc một câu hoặc một ý quan trọng bị cắt làm đôi và mất đi ngữ cảnh liền kề; phần văn bản giao nhau giúp mô hình RAG hiểu trọn vẹn ngữ nghĩa ở các vùng giáp ranh.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*
> Mình sử dụng Regex Lookbehind `(?<=[.!?])\s+` để tách câu dựa vào khoảng trắng ngay sau các dấu chấm, chấm hỏi, chấm than. Kỹ thuật này giúp tách được câu mà không "nuốt" mất dấu câu. Cạnh biên (edge case) chưa được xử lý tốt là các chữ viết tắt (như `TS.`, `v.v.`) có thể bị hiểu nhầm là kết thúc câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
> Hàm thử từng dấu phân cách (separator) theo thứ tự ưu tiên. Nếu một đoạn văn (sau khi cắt) vẫn dài hơn `chunk_size`, hàm `_split()` sẽ gọi đệ quy chính nó với các separator còn lại. Các mảnh nhỏ sau đó được thuật toán gom (merge) lại cho đến khi gần đạt `chunk_size` để tránh bị vụn vặt. Base case là khi văn bản nhỏ hơn `chunk_size` hoặc khi danh sách separator đã cạn (lúc này sẽ dùng cắt cứng).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*
> Mình lưu trữ các documents trong bộ nhớ (danh sách Python `_store`), record được tạo ra lưu giữ `doc_id` gốc để phục vụ truy vết. Việc tìm kiếm (`search`) được thực hiện bằng cách tính tích vô hướng (`_dot`) giữa embedding của truy vấn và các tài liệu, sau đó sort giảm dần theo điểm `score` và cắt lấy top `k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*
> Việc lọc `metadata` phải được thực hiện TRƯỚC (chỉ đưa những record hợp lệ vào một mảng tạm), sau đó mới gọi hàm `_search_records` trên mảng tạm đó. Nếu search trước rồi mới lọc, ta sẽ làm mất top-K nếu các document sai metadata vô tình có score cao. Xóa file thực hiện bằng list comprehension loại bỏ các record có `doc_id` khớp.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*
> Đầu tiên mình truy xuất danh sách `top_k`. Cấu trúc Prompt được thiết kế bằng cách liệt kê văn bản kèm đánh số thứ tự `[1]`, `[2]` và thông tin `Source: URL/DocID`. Sau đó, Prompt chỉ thị rõ LLM phải giới hạn câu trả lời trong phạm vi Context và bắt buộc trích dẫn bằng các con số trong ngoặc vuông này (Source Traceability).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0 -- c:\Users\doduc\K4-L3A-Data-Foundations\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\doduc\K4-L3A-Data-Foundations
plugins: anyio-4.15.1
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
... (Lược bỏ bớt log chi tiết) ...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.12s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Thư viện mở cửa lúc mấy giờ? | Thời gian hoạt động của thư viện. | cao | 0.85 | Có |
| 2 | Đăng ký môn học như thế nào? | Hướng dẫn chọn lớp học phần. | cao | 0.78 | Có |
| 3 | Hôm nay trời mưa to quá. | Giá cổ phiếu công nghệ đang giảm mạnh. | thấp | 0.05 | Có |
| 4 | Trường đại học có học bổng không? | Sinh viên nghèo vượt khó được hỗ trợ tài chính. | cao | 0.65 | Có |
| 5 | Cách đóng học phí qua ví điện tử. | Danh sách món ăn ngon ở căn tin sinh viên. | thấp | 0.02 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Bất ngờ nhất là Cặp 4 ("học bổng" và "hỗ trợ tài chính"). Hai câu hầu như không trùng từ vựng nào (không có chung từ khóa), nhưng mô hình embedding vẫn trả về điểm tương đồng khá cao. Điều này chứng minh embeddings thực sự ánh xạ được "ý nghĩa ngữ nghĩa" (semantics) và mối liên hệ khái niệm đằng sau ngôn từ.

---

### 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Phúc khảo tự luận: làm gì, bao lâu? (Filter: student) | Điều 26: Phúc khảo tự luận trong vòng 7 ngày... | 0.812 | Có (Top 1) | Nộp đơn phúc khảo tại phòng đào tạo trong 7 ngày. |
| 2 | Thời lượng tối đa bài tự luận | Điều 6: Thời lượng bài tự luận là 120 phút... | 0.745 | Có (Top 3) | 120 phút. |
| 3 | Đến muộn bao lâu thì không được thi | Điều 13 khoản 2: Thí sinh đến muộn quá 15 phút... | 0.880 | Có (Top 1) | Thí sinh đến muộn quá 15 phút sẽ không được dự thi. |
| 4 | Hai GV chấm tiểu luận lệch ≥ 2 điểm | Điều 21: Quy định về chấm tiểu luận (sai Điều)... | 0.612 | Không (Top 3 có file đúng) | (Thiếu thông tin mời người thứ ba) |
| 5 | Lỗi bị đình chỉ thi | Điều 29: Đình chỉ thi đối với các lỗi chép bài... | 0.778 | Có (Top 1) | Chép bài, mang tài liệu (nhưng thiếu ý không chấp hành CBCT). |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Em học được rằng chiến lược chia nhỏ (Chunking) theo kích thước cố định (của bạn Bảo) có thể vô tình chẻ đôi một câu luật quan trọng làm hai nửa, khiến mô hình không còn hiểu được ngữ cảnh gốc. Trong khi đó, cắt theo câu (của bạn Phi) cực kỳ hiệu quả để giữ trọn vẹn một danh sách liệt kê dài bằng dấu chấm phẩy, vốn rất phổ biến trong các văn bản pháp quy.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
