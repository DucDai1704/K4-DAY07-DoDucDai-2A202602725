import os
from pathlib import Path
import csv

out_dir = Path('data/university')
out_dir.mkdir(parents=True, exist_ok=True)

docs = [
    {
        'doc_id': 'dang-ky-hoc-phan',
        'title': 'Quy định Đăng ký học phần',
        'source_url': 'https://univ.edu.vn/dang-ky-hoc-phan',
        'retrieved_at': '2026-09-19',
        'document_version': '2026.1',
        'audience': 'student',
        'content': '# Quy định Đăng ký học phần\n\nSinh viên phải đăng ký học phần trong hệ thống trước 2 tuần khi học kỳ bắt đầu.\nNếu gặp lỗi trùng lịch học, sinh viên phải điều chỉnh lớp học phần trước thời hạn điều chỉnh được công bố trên cổng thông tin.\nMọi thắc mắc liên hệ phòng Đào tạo.'
    },
    {
        'doc_id': 'thu-vien-sinh-vien',
        'title': 'Quy định Thư viện cho Sinh viên',
        'source_url': 'https://univ.edu.vn/thu-vien/sinh-vien',
        'retrieved_at': '2026-09-19',
        'document_version': '2026.1',
        'audience': 'student',
        'content': '# Quy định Thư viện\n\nThư viện mở cửa tới 9h tối đối với sinh viên.\nSinh viên được mượn tối đa 5 cuốn sách trong thời gian 14 ngày.\nVui lòng xuất trình thẻ sinh viên khi mượn sách.'
    },
    {
        'doc_id': 'thu-vien-giang-vien',
        'title': 'Quy định Thư viện cho Giảng viên',
        'source_url': 'https://univ.edu.vn/thu-vien/giang-vien',
        'retrieved_at': '2026-09-19',
        'document_version': '2026.1',
        'audience': 'faculty',
        'content': '# Quy định Thư viện Giảng viên\n\nThư viện mở cửa tới 10h tối đối với giảng viên.\nGiảng viên được mượn tối đa 20 cuốn sách trong thời gian 180 ngày.\nGiảng viên có khu vực nghiên cứu riêng tại tầng 3.'
    },
    {
        'doc_id': 'hoc-bong-khuyen-khich',
        'title': 'Học bổng khuyến khích học tập',
        'source_url': 'https://univ.edu.vn/hoc-bong',
        'retrieved_at': '2026-09-19',
        'document_version': 'not-stated',
        'audience': 'student',
        'content': '# Học bổng khuyến khích\n\nSinh viên đạt điểm trung bình chung (GPA) từ 3.2 trở lên và không có môn nào rớt sẽ đủ điều kiện xét học bổng loại giỏi.\nGPA từ 3.6 trở lên đạt học bổng loại xuất sắc.\nHọc bổng được cấp vào tháng 11 hàng năm.'
    },
    {
        'doc_id': 'phuc-khao-diem',
        'title': 'Quy trình phúc khảo điểm',
        'source_url': 'https://univ.edu.vn/phuc-khao',
        'retrieved_at': '2026-09-19',
        'document_version': '2026.1',
        'audience': 'student',
        'content': '# Quy trình phúc khảo\n\nSinh viên có quyền làm đơn phúc khảo trong vòng 7 ngày kể từ ngày công bố điểm thi.\nĐơn phúc khảo nộp tại Phòng Đào tạo (Tầng 1).\nLệ phí phúc khảo là 50,000 VNĐ/môn.'
    }
]

for d in docs:
    filepath = out_dir / (d['doc_id'] + '.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write(f"doc_id: {d['doc_id']}\n")
        f.write(f"title: {d['title']}\n")
        f.write(f"source_url: {d['source_url']}\n")
        f.write(f"retrieved_at: {d['retrieved_at']}\n")
        f.write(f"document_version: {d['document_version']}\n")
        f.write(f"audience: {d['audience']}\n")
        f.write('---\n')
        f.write(d['content'])

with open(out_dir / 'sources.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['doc_id', 'title', 'source_url', 'retrieved_at', 'document_version', 'audience'])
    writer.writeheader()
    for d in docs:
        row = {k: d[k] for k in writer.fieldnames}
        writer.writerow(row)

print('Generated files successfully.')
