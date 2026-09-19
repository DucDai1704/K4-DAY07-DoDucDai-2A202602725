# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm Khảo Thí IUH
**Thành viên:** Đỗ Ngọc Phi, Phạm Công Quốc, Nguyễn Trọng Bảo, Đỗ Đức Đại
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế Đào tạo, Thi cử & Kiểm tra của Đại học Công nghiệp TP.HCM (IUH).

**Tại sao nhóm chọn chủ đề này?**
> Đây là một bộ tài liệu thực tế, rất sát với đời sống sinh viên. Văn bản pháp quy của IUH có cấu trúc Điều/Khoản/Điểm cực kỳ chặt chẽ, và có sự phân định rõ ràng giữa quy định cho sinh viên, giảng viên và cán bộ coi thi. Điều này tạo điều kiện hoàn hảo để nhóm thử nghiệm tính năng lọc `metadata_filter` bằng `audience`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Phúc khảo — quy định dành cho sinh viên (`phuc-khao-sinh-vien`) | PDF Quy chế 610 — Điều 26 (khoản 1, 2c, 3, 5), Điều 28 | 2026-09-19 / 610/QĐ-ĐHCN | 3 150 | audience=student, category=phuc-khao |
| 2 | Khảo thí — quy định chung (`khao-thi-chung`) | PDF Quy chế 610 — Điều 1, 2, 3, 4, 5, 9 | 2026-09-19 / 610/QĐ-ĐHCN | 4 820 | audience=all, category=quy-dinh-chung |
| 3 | Phúc khảo — quy định dành cho giảng viên và đơn vị (`phuc-khao-giang-vien`) | PDF Quy chế 610 — Điều 26 (khoản 2a, 2b, 4), Điều 27 | 2026-09-19 / 610/QĐ-ĐHCN | 2 442 | audience=faculty, category=phuc-khao |
| 4 | Trách nhiệm của cán bộ coi thi (`can-bo-coi-thi`) | PDF Quy chế 610 — Điều 10 (khoản 3), Điều 11 | 2026-09-19 / 610/QĐ-ĐHCN | 6 373 | audience=faculty, category=to-chuc-thi |
| 5 | Chấm thi và nhập điểm (`cham-thi`) | PDF Quy chế 610 — Điều 21, 23, 24, 25 | 2026-09-19 / 610/QĐ-ĐHCN | 5 316 | audience=faculty, category=cham-thi |
| 6 | Nội dung và biên soạn đề thi (`bien-soan-de-thi`) | PDF Quy chế 610 — Điều 7, 8 | 2026-09-19 / 610/QĐ-ĐHCN | 6 038 | audience=faculty, category=ra-de |
| 7 | Hình thức và thời lượng thi (`hinh-thuc-thoi-luong-thi`) | PDF Quy chế 610 — Điều 6 | 2026-09-19 / 610/QĐ-ĐHCN | 3 426 | audience=all, category=hinh-thuc-thi |
| 8 | Xử lý người học vi phạm quy chế thi (`xu-ly-vi-pham-nguoi-hoc`) | PDF Quy chế 610 — Điều 29 | 2026-09-19 / 610/QĐ-ĐHCN | 3 808 | audience=student, category=xu-ly-vi-pham |
| 9 | Xử lý cán bộ vi phạm quy chế thi (`xu-ly-vi-pham-can-bo`) | PDF Quy chế 610 — Điều 30 | 2026-09-19 / 610/QĐ-ĐHCN | 2 105 | audience=faculty, category=xu-ly-vi-pham |
| 10 | Các loại hình thi trực tuyến (`loai-hinh-thi-truc-tuyen`) | https://tqa.iuh.edu.vn/cong-tac-khao-thi/loai-hinh-thi-truc-tuyen/ | 2026-09-19 / not-stated | 6 954 | audience=all, category=hinh-thuc-thi, source_type=html-crawled |

Phân bố `audience`: faculty 5, student 3, all 2. File `data/khao-thi-phuc-khao/sources.csv` khớp 1-1 với 10 file, và script kiểm tra CP2 của lab báo 10/10 OK.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

**Ghi chú về quá trình thu thập (những điều nhóm gặp phải):**
- **`robots.txt`:** chỉ cấm `/wp-admin/`. Tuy nhiên tường lửa của trường trả 403 cho User-Agent mặc định `Python-urllib`, và `RobotFileParser` của Python hiểu 403 là "cấm tất cả". Nhóm đọc lại `robots.txt` bằng **đúng UA của crawler** (`Day7DataFoundationsCourse/1.0`) thì được 200 và các trang đều được phép. Nhóm không giả làm trình duyệt, vẫn giữ giãn cách ≥1 giây giữa các request.
- **SSL:** server không gửi chứng chỉ trung gian (RapidSSL), nên Python báo `CERTIFICATE_VERIFY_FAILED`. Nhóm tải chứng chỉ trung gian từ địa chỉ chính thức của DigiCert ghi trong chứng chỉ, ghép vào bộ CA, **vẫn xác thực SSL đầy đủ**.
- **PDF là bản scan** (28 trang, 0 ký tự trích được), nên nhóm chép tay các Điều cần dùng, giữ nguyên văn, và ghi `source_type: pdf-scan-transcribed`. Không đưa PDF thô vào `data/`.
- **Bản tóm tắt trên web lệch với văn bản gốc.** Trang Quy định phúc khảo ghi là trích Điều 26 của chính quy chế này, nhưng ghi "14 ngày" thay vì "14 ngày **làm việc**", và ghi phúc khảo trắc nghiệm "trong vòng 03 ngày" thay vì "trả kết quả trong vòng **2 ngày làm việc**". Nhóm **dùng PDF làm nguồn chính thức** và loại trang tóm tắt, để corpus không chứa hai đáp án mâu thuẫn nhau.
- **Các trang bị loại:**
  - Trang "Tổng hợp kết quả phúc khảo": chỉ là danh sách link tới file kết quả, có thể chứa dữ liệu cá nhân của sinh viên.
  - 4 trang con của "Loại hình thi trực tuyến": trùng nội dung với trang tổng quan.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string | `student`, `faculty`, `all` | Phân loại rõ ràng quy định dành cho ai, giúp tránh agent lấy nhầm quy chế của cán bộ đem trả lời cho sinh viên. |
| `category` | string | `phuc-khao`, `cham-thi` | Giúp lọc nhanh khi câu hỏi khu trú vào một quy trình đào tạo cụ thể. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `quy-che-thi-sv` | FixedSizeChunker (`fixed_size`) | 45 | 200 | Kém, các điều khoản bị cắt ngang giữa chừng, mất liên kết. |
| `quy-che-thi-sv` | SentenceChunker (`by_sentences`) | 28 | 320 | Tốt với các câu dài, giữ trọn vẹn danh sách liệt kê bằng dấu `;`. |
| `quy-che-thi-sv` | RecursiveChunker (`recursive`) | 35 | 250 | Khá tốt, giữ trọn khoản nhưng bị mất tiêu đề Điều (ngữ cảnh gốc). |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Trọng Bảo**
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn:** Cắt theo kích thước cố định (chunk_size=500, overlap=50). Đây là phương pháp cơ bản nhất để làm baseline đối chiếu với các thuật toán phức tạp hơn.

**Thành viên 2 — Phạm Công Quốc**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Cắt đệ quy theo cấu trúc văn bản tự nhiên (đoạn văn, câu). Phù hợp để tách rời các khoản độc lập trong văn bản pháp quy.

**Thành viên 3 — Đỗ Đức Đại**
- **Loại chiến lược:** HeadingChunker (custom)
- **Mô tả & lý do chọn:** Văn bản IUH có cấu trúc Điều 1, Điều 2 rõ ràng bằng thẻ `#`. Việc cắt theo Heading giúp giữ toàn vẹn một Điều luật. Nếu đoạn quá dài, em dùng Recursive cắt thêm nhưng luôn nối tên Điều lên đầu để bảo toàn ngữ cảnh.
- **Code snippet (nếu custom):**
```python
import re
from src.chunking import RecursiveChunker

class HeadingChunker:
    def __init__(self, max_chunk_size=500):
        self.max_chunk_size = max_chunk_size
        self.fallback = RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = re.split(r'(?m)(?=^#+\s)', text)
        chunks = []
        for section in sections:
            section = section.strip()
            if len(section) <= self.max_chunk_size:
                chunks.append(section)
            else:
                lines = section.split('\n', 1)
                heading = lines[0] if lines[0].startswith('#') else ""
                sub_chunks = self.fallback.chunk(section)
                for i, sub in enumerate(sub_chunks):
                    if i > 0 and heading and not sub.startswith('#'):
                        sub = f"{heading} (phần tiếp)\n{sub}"
                    chunks.append(sub)
        return chunks
```

**Thành viên 4 — Đỗ Ngọc Phi**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Cắt theo câu bằng Regex. Đặc thù của văn bản pháp quy là các điều khoản liệt kê (điểm a, b, c) thường nối nhau bằng dấu `;` tạo thành một câu rất dài. SentenceChunker giúp giữ trọn cả một danh sách như vậy.

### So Sánh Giữa Các Thành viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trọng Bảo | FixedSizeChunker | 5/10 | Nhanh, dễ cấu hình, kích thước chunk đều nhau. | Phá vỡ cấu trúc Điều/Khoản, dễ chia cắt các quy trình gắn liền nhau. |
| Công Quốc | RecursiveChunker | 6/10 | Giữ được trọn vẹn từng khoản/đoạn. | Không giữ được tên Điều, khiến đoạn văn bị cụt lủn thông tin nền. |
| Đức Đại | HeadingChunker | 7/10 | Giữ ngữ cảnh "Điều X" hoàn hảo. | Phức tạp, nếu một đoạn không có Heading sẽ tụt hiệu suất. |
| Ngọc Phi | SentenceChunker | 7/10 | Giữ được trọn vẹn các danh sách liệt kê pháp quy. | Dễ bị nhiễu bởi các câu ngắn không mang ý nghĩa. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> HeadingChunker (của Đại) kết hợp với SentenceChunker (của Phi). HeadingChunker xuất sắc trong việc gắn ngữ cảnh (biết đoạn văn thuộc Điều nào), trong khi SentenceChunker cực tốt trong việc giữ trọn vẹn danh sách liệt kê (vốn được ngăn bằng dấu chấm phẩy trong luật).

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Phúc khảo tự luận: làm gì, bao lâu? (Filter: audience=student) | Sinh viên nộp đơn trong 7 ngày. | Điều 26 (thời hạn, thủ tục phúc khảo) |
| 2 | Thời lượng tối đa bài tự luận là bao nhiêu? | 120 phút | Điều 6 (Thời lượng thi) |
| 3 | Đến muộn bao lâu thì không được vào thi? | Thí sinh đến muộn quá 15 phút sẽ không được dự thi. | Điều 13 khoản 2 |
| 4 | Hai giảng viên chấm tiểu luận lệch nhau ≥ 2 điểm thì xử lý thế nào? | Chấm chung hoặc mời người thứ ba chấm. | Điều 24 |
| 5 | Những lỗi nào khiến sinh viên bị đình chỉ thi? | Chép bài, mang tài liệu, không chấp hành kỷ luật CBCT. | Điều 29 khoản c |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Phúc khảo tự luận: làm gì, bao lâu | Recursive, Heading v2 (2đ) | Recursive và Heading v2: 3/3 ý, đoạn đúng ở top-1. Sentence: 3/3 ý nhưng top-1 là đoạn "thông báo kết quả trong 07 ngày" (1đ). Fixed chỉ có mảnh nộp muộn (0/3 ý), Heading v1 cũng 0/3 | **Bỏ filter thì cả 5 cấu hình đều 0đ**: top-3 toàn chunk về "thời lượng/thời gian" (Điều 6, Điều 8 "06 tuần") |
| 2 | Thời lượng tối đa bài tự luận | Fixed, Sentence (2đ); Recursive, Heading (1đ) | Có với cả 5. Fixed và Sentence có đoạn chứa "120 phút" ngay top-1; các cấu hình khác để nó ở hạng 2–3 | Top-1 luôn đúng Điều 6 nhưng có thể là khoản khác (trắc nghiệm, phòng máy): các khoản cùng Điều có điểm sát nhau |
| 3 | Đến muộn bao lâu thì không được thi | Cả 5 (2đ) | Có, top-1 chứa đúng Điều 13 khoản 2 | Câu dễ nhất |
| 4 | Hai GV chấm tiểu luận lệch ≥ 2 điểm | Heading v1/v2 (1đ) | Heading: đoạn Điều 24 ở hạng 3, top-1 là Điều 21. Fixed, Recursive, Sentence: chỉ có Điều 21 (0/2 ý) | **Đúng file nhưng sai Điều**. Bốn chiến lược đều có file `cham-thi` trong top-3 |
| 5 | Lỗi bị đình chỉ thi | Cả 5 (1đ); chỉ Sentence gom đủ 3/3 ý | Fixed, Recursive, Heading thiếu ý "không chấp hành yêu cầu của CBCT". Sentence đủ ý nhưng top-1 là đoạn thủ tục lập biên bản | Điểm c) dài 841 ký tự bị cắt qua 2 chunk ở các chiến lược theo kích thước; nửa sau mất nhãn "c) Đình chỉ thi" nên xếp hạng thấp. Sentence giữ trọn vì cả danh sách là một câu ngăn bằng `;`. Top-3 còn lẫn Điều 30 (vi phạm của **cán bộ**) |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Có, và quyết định kết quả ở Q1.**
> - **Có filter** `audience=student`: tập ứng viên giảm từ 118 xuống 24 chunk (Recursive), và Recursive cùng Heading v2 đạt 2/2.
> - **Không filter**: cả 5 cấu hình đều 0/2. Phần "trong thời hạn bao lâu" của câu hỏi kéo lên các chunk về thời lượng thi và hạn nộp tiểu luận (`bien-soan-de-thi`, `hinh-thuc-thoi-luong-thi`); chunk của người học còn không lọt top-3.
>
> **Filter cũng có cái giá.** Nhóm thử câu *"Thi tự luận thì sinh viên được ra về sớm khi nào?"*. Đáp án ("sau 2/3 thời gian làm bài") nằm trong Điều 11 khoản 6, thuộc tài liệu **cán bộ coi thi** (`faculty`).
> - Không filter: chunk này xếp hạng 3–6 tùy chiến lược. Với Sentence nó nằm **ngay trong top-3**.
> - Có filter `student`: chunk này **biến mất hoàn toàn** ở mọi chiến lược, tăng `top_k` bao nhiêu cũng không cứu được.
>
> Ngoài ra, filter so khớp chính xác nên cũng loại luôn tài liệu `audience: all`, ví dụ Điều 6 về thời lượng thi. Filter tăng precision nhưng có thể làm mất recall.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Chấm theo `doc_id` là ảo tưởng.** Cả 4 chiến lược đều 10/10 theo `doc_id`, nhưng chấm đúng rubric chỉ còn 5–7. Q4 là ví dụ điển hình: cả bốn đều có file `cham-thi` trong top-3, nhưng ba chiến lược chỉ lấy được Điều sai.
> 2. **Filter là con dao hai lưỡi.** Q1 từ 0/2 lên 2/2 nhờ `audience=student`, nhưng câu "ra về sớm" thì mất hẳn đáp án (với Sentence, đáp án đang ở hạng 3 thì biến mất) vì quy định nằm trong tài liệu của cán bộ coi thi.
> 3. **Metadata phải nằm trong metadata.** Một dòng ghi nguồn ~400 ký tự nằm trong nội dung chunk đủ làm loãng embedding và đánh rơi đáp án: Heading từ 5/10 lên 7/10 chỉ nhờ bỏ dòng đó ra. Mock embedder đạt **0/10** trên cùng bộ câu hỏi, nên benchmark bắt buộc phải dùng embedder thật.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng tài liệu và câu hỏi, khác biệt đến từ việc chunk có giữ được **đơn vị ngữ nghĩa của văn bản** hay không. Fixed-size chẻ đôi câu nên quy trình và thời hạn tách rời nhau. Recursive giữ trọn khoản nhưng không biết khoản đó thuộc Điều nào. Heading giữ được cả hai tầng. Sentence cho thấy một đơn vị ngữ nghĩa khác: **câu dài** của văn bản pháp quy (danh sách ngăn bằng `;`) nên nó là chiến lược duy nhất giữ trọn danh sách ở Q5. Mỗi chiến lược thắng ở một kiểu câu hỏi khác nhau, nên kết hợp heading (giữ ngữ cảnh Điều) với ranh giới câu (không cắt danh sách) có thể là hướng tốt nhất.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> 1. Cho `audience` nhận **nhiều giá trị** và cho filter hỗ trợ kiểu "student hoặc all", đồng thời tách riêng các khoản trong tài liệu cán bộ mà người học cũng cần biết (như Điều 11 khoản 6).
> 2. Chunk theo **khoản/điểm** và gắn nhãn điểm (vd. "Điều 29, c) Đình chỉ thi") vào từng mảnh con. Hoặc dùng parent-document retrieval: khớp chunk nhỏ nhưng trả về cả Điều.
> 3. Không để ghi chú nguồn trong phần thân tài liệu ngay từ đầu.
> 4. Kiểm chéo mọi bản tóm tắt trên web với văn bản gốc trước khi đưa vào corpus, vì nhóm đã gặp trường hợp web ghi "14 ngày" còn văn bản gốc ghi "14 ngày làm việc".

### Kịch bản demo (6–8 phút, Nguyễn Trường Bảo dẫn)

Mọi thành viên đều trình bày phần chiến lược của mình. Terminal mở sẵn với `bench.py` đã chạy được.

| Thời lượng | Người trình bày | Nội dung |
|---|---|---|
| 1' | Đỗ Ngọc Phi | Chủ đề, nguồn IUH, cách tách tài liệu theo `audience`, các vấn đề thu thập (robots.txt theo UA, chứng chỉ SSL, PDF scan, bản web lệch với văn bản gốc) |
| 2' | Cả 4 người (~30" mỗi người) | Mỗi người tóm tắt chiến lược và lý do chọn: Bảo (Fixed), Quốc (Recursive), Đại (Heading), Phi (Sentence) |
| 3' | Phạm Công Quốc, rồi Nguyễn Trọng Bảo | Quốc: 5 câu hỏi và cách chấm theo ý chính. Bảo: bảng ba mức chấm (10 → 5–7), A/B filter ở Q1 và câu thăm dò "ra về sớm" |
| 2' | Đỗ Đức Đại | Demo trực tiếp Q4 (đúng file, sai Điều) và Q1 với Heading v1 so với v2 (lỗi dòng ghi nguồn) |
| còn lại | Cả nhóm | Hỏi đáp |

Câu trả lời chuẩn bị sẵn cho ba câu giảng viên hay hỏi:
- *Chuyển chủ đề thì chiến lược nào còn dùng được?* Recursive dùng được gần như mọi nơi. Heading chỉ tốt khi văn bản có Điều/mục rõ ràng. Sentence hợp văn bản pháp quy có câu dài.
- *Metadata filter giúp ở đâu, làm mất kết quả ở đâu?* Giúp ở Q1 (0 → 2 điểm). Làm mất ở câu "ra về sớm" và loại cả tài liệu `audience: all`.
- *Học được gì từ nhóm khác?* Điền sau buổi demo.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
