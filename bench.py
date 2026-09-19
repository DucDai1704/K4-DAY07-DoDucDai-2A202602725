import os
import re
from pathlib import Path

from src.models import Document
from src.store import EmbeddingStore
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker

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
    data_dir = Path("data/university")
    md_files = list(data_dir.glob("*.md"))
    print(f"Found {len(md_files)} markdown files in {data_dir}")

    # R3 (Strategy): Thay đổi chiến lược Chunking tại đây
    chunker = FixedSizeChunker(chunk_size=200, overlap=20)
    # chunker = SentenceChunker(max_sentences_per_chunk=3)
    # chunker = RecursiveChunker(chunk_size=200)

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
            "q": "Sinh viên gặp lỗi trùng lịch học thì phải làm gì?",
            "filter": None,
            "gold": "Điều chỉnh lớp học phần trước thời hạn điều chỉnh được công bố trên cổng thông tin."
        },
        {
            "q": "Thư viện mở cửa tới mấy giờ đối với sinh viên?",
            "filter": {"audience": "student"},
            "gold": "Thư viện mở cửa tới 9h tối đối với sinh viên."
        },
        {
            "q": "Học bổng loại giỏi yêu cầu GPA bao nhiêu?",
            "filter": None,
            "gold": "GPA từ 3.2 trở lên"
        },
        {
            "q": "Giảng viên được mượn sách thư viện trong bao lâu?",
            "filter": {"audience": "faculty"},
            "gold": "180 ngày"
        },
        {
            "q": "Thời hạn để xin phúc khảo điểm thi là bao lâu?",
            "filter": None,
            "gold": "Trong vòng 7 ngày kể từ ngày công bố điểm thi."
        },
    ]

    print("=== BENCHMARK RESULTS ===\n")
    for idx, q_info in enumerate(queries, 1):
        q = q_info["q"]
        meta_filter = q_info["filter"]
        gold = q_info["gold"]
        
        print(f"Q{idx}: {q}")
        print(f"  Gold Answer: {gold}")
        if meta_filter:
            print(f"  Filter: {meta_filter}")
            
        results = store.search_with_filter(q, top_k=3, metadata_filter=meta_filter)
        
        for i, r in enumerate(results, 1):
            score = r['score']
            doc_id = r['metadata'].get('doc_id', 'unknown')
            preview = r['content'].replace('\n', ' ')[:80]
            print(f"  [{i}] (Score: {score:.3f} | doc: {doc_id}) {preview}...")
        
        print("-" * 50)

if __name__ == "__main__":
    run_benchmark()
