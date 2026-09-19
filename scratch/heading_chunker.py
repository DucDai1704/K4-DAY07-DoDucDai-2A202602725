import re

class HeadingChunker:
    """
    Chia nhỏ văn bản dựa trên các thẻ tiêu đề Heading của Markdown (#).
    Mỗi mục (section) tính từ một Heading đến trước Heading tiếp theo sẽ là một chunk.
    Nếu một section quá dài, nó sẽ được cắt nhỏ thêm bằng RecursiveChunker.
    """
    def __init__(self, max_chunk_size: int = 500):
        self.max_chunk_size = max_chunk_size
        from src.chunking import RecursiveChunker
        self.fallback_chunker = RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
            
        # Tách văn bản dựa trên các dòng bắt đầu bằng # (Markdown heading)
        # Regex (?=^#) dùng lookahead để tách mà không làm mất dấu #
        sections = re.split(r'(?m)(?=^#+\s)', text)
        
        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Nếu section nhỏ hơn kích thước tối đa, giữ nguyên
            if len(section) <= self.max_chunk_size:
                chunks.append(section)
            else:
                # Nếu section quá dài, tách nhỏ thêm.
                # LƯU Ý QUAN TRỌNG: Gắn lại tiêu đề cho các mảnh con để không mất ngữ cảnh
                lines = section.split('\n', 1)
                heading = lines[0] if lines[0].startswith('#') else ""
                
                sub_chunks = self.fallback_chunker.chunk(section)
                for i, sub in enumerate(sub_chunks):
                    if i > 0 and heading and not sub.startswith('#'):
                        sub = f"{heading} (phần tiếp theo)\n{sub}"
                    chunks.append(sub)
                    
        return chunks
