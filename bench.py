import os
import re
from pathlib import Path

from src.models import Document
from src.store import EmbeddingStore
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker, HeadingChunker

def parse_markdown(file_path: Path):
    text = file_path.read_text(encoding="utf-8")
    match = re.match(r'^---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if not match:
        return {"doc_id": file_path.stem}, text.strip()
    
    frontmatter_text = match.group(1)
    content = match.group(2).strip()
    
    metadata = {}
    for line in frontmatter_text.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            val = val.split("#")[0].strip().strip('"').strip("'")
            metadata[key.strip()] = val
            
    if "doc_id" not in metadata:
        metadata["doc_id"] = file_path.stem
        
    return metadata, content

def run_benchmark():
    data_dir = Path("data/khao-thi-phuc-khao")
    md_files = list(data_dir.glob("*.md"))
    print(f"Found {len(md_files)} markdown files in {data_dir}")

    # R3 (Strategy): Thay đổi chiến lược Chunking tại đây
    # chunker = FixedSizeChunker(chunk_size=500, overlap=100)
    # chunker = SentenceChunker(max_sentences_per_chunk=3)
    # chunker = RecursiveChunker(chunk_size=500)
    chunker = HeadingChunker(chunk_size=500)

    store = EmbeddingStore()

    documents_to_add = []
    
    for p in md_files:
        meta, content = parse_markdown(p)
        chunks = chunker.chunk(content)
        for i, chunk_text in enumerate(chunks):
            doc = Document(
                id=f"{p.stem}#{i}",
                content=chunk_text,
                metadata=meta.copy()
            )
            documents_to_add.append(doc)

    print(f"Loaded {len(documents_to_add)} chunks from {len(md_files)} files.\n")
    store.add_documents(documents_to_add)

    # R2 (Benchmark): 5 Benchmark queries
    queries = [
        {
            "q": "Tôi muốn phúc khảo bài thi tự luận thì phải làm gì và trong thời hạn bao lâu?",
            "filter": {"audience": "student"},
            "gold": "Làm đơn phúc khảo điểm thi (Mẫu 12), chuyển đơn cùng phiếu đóng tiền phúc khảo đến giáo vụ Khoa/Viện của đơn vị chủ quản học phần trong vòng 14 ngày làm việc kể từ ngày điểm thi được công bố. Nộp muộn hơn thì phải được Trưởng đơn vị chủ quản học phần đồng ý."
        },
        {
            "q": "Thời lượng tối đa của một bài thi tự luận là bao nhiêu phút?",
            "filter": None,
            "gold": "Tối thiểu 50 phút và tối đa 120 phút, tùy số tín chỉ của học phần và số câu hỏi trong đề."
        },
        {
            "q": "Đến phòng thi muộn bao lâu thì không được dự thi?",
            "filter": None,
            "gold": "Người học đến muộn quá 15 phút sau khi đã phát đề thi sẽ không được dự thi. Người học phải có mặt trước giờ thi ít nhất 15 phút."
        },
        {
            "q": "Hai giảng viên chấm tiểu luận lệch nhau từ 2 điểm trở lên thì xử lý thế nào?",
            "filter": None,
            "gold": "Hai GV thảo luận để thống nhất kết quả. Nếu không thống nhất được thì báo CNBM xem xét quyết định."
        },
        {
            "q": "Những lỗi vi phạm nào khiến người học bị đình chỉ thi?",
            "filter": None,
            "gold": "Mang tài liệu hoặc phương tiện bị cấm vào phòng thi; đưa đề thi ra ngoài khu vực thi hoặc nhận bài giải từ bên ngoài; đã bị cảnh cáo trong giờ thi của học phần đó mà vẫn vi phạm; viết, vẽ nội dung không liên quan; gây rối, đe dọa, xúc phạm CBCT hoặc người học khác; không chấp hành yêu cầu của CBCT về kỷ luật phòng thi. Hậu quả: điểm 0 cho học phần."
        },
    ]

    output_lines = []
    output_lines.append("=== BENCHMARK RESULTS ===\n")
    
    for idx, q_info in enumerate(queries, 1):
        q = q_info["q"]
        meta_filter = q_info["filter"]
        gold = q_info["gold"]
        
        output_lines.append(f"Q{idx}: {q}")
        output_lines.append(f"  Gold Answer: {gold}")
        if meta_filter:
            output_lines.append(f"  Filter: {meta_filter}")
            
        results = store.search_with_filter(q, top_k=3, metadata_filter=meta_filter)
        
        for i, r in enumerate(results, 1):
            score = r['score']
            doc_id = r['metadata'].get('doc_id', 'unknown')
            preview = r['content'].replace('\n', ' ')[:80]
            output_lines.append(f"  [{i}] (Score: {score:.3f} | doc: {doc_id}) {preview}...")
        
        output_lines.append("-" * 50)
        
    output_text = "\n".join(output_lines)
    
    # Save output to report/benchmark/
    report_dir = Path("report/benchmark")
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"{chunker.__class__.__name__}.txt").write_text(output_text, encoding="utf-8")
    
    try:
        print(output_text)
        print(f"\nSaved results to {report_dir / f'{chunker.__class__.__name__}.txt'}")
    except UnicodeEncodeError:
        print(f"Benchmark completed. Output saved to {report_dir / f'{chunker.__class__.__name__}.txt'}")

if __name__ == "__main__":
    run_benchmark()
