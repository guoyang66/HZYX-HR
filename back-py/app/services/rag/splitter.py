"""
文档分割器 - 将长文本按段落和句子切分为固定大小的块（Chunk）
用于RAG场景下超长简历的分段嵌入和检索
"""
import re
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """文档块数据结构"""
    id: str               # 块ID（如 "1_chunk_0"）
    document_id: str      # 所属文档ID
    content: str          # 块文本内容
    chunk_index: int      # 块序号
    metadata: dict = None


class DocumentSplitter:
    """文档分割器 - 按段落分割，超长段落按句子再分割"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size          # 每块最大字符数
        self.chunk_overlap = chunk_overlap    # 块间重叠字符数

    def split(self, document_id: str, content: str) -> list[DocumentChunk]:
        """将文档内容分割为多个块"""
        if not content:
            return []
        # 先按空行分隔段落
        paragraphs = re.split(r'\n\s*\n', content)
        chunks = []
        chunk_index = 0
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            # 当前块还能容纳此段落则追加
            if len(current) + len(para) + 1 <= self.chunk_size:
                current = f"{current}\n{para}" if current else para
            else:
                # 保存当前块，开始新块
                if current:
                    chunks.append(DocumentChunk(
                        id=f"{document_id}_chunk_{chunk_index}",
                        document_id=document_id,
                        content=current,
                        chunk_index=chunk_index,
                    ))
                    chunk_index += 1
                # 超长段落按句子分割
                if len(para) > self.chunk_size:
                    sub_chunks = self._split_large_paragraph(para, document_id, chunk_index)
                    chunks.extend(sub_chunks)
                    chunk_index += len(sub_chunks)
                    current = ""
                else:
                    current = para

        # 保存最后一个块
        if current:
            chunks.append(DocumentChunk(
                id=f"{document_id}_chunk_{chunk_index}",
                document_id=document_id,
                content=current,
                chunk_index=chunk_index,
            ))

        return chunks

    def _split_large_paragraph(self, text: str, document_id: str, start_index: int) -> list[DocumentChunk]:
        """将超大段落按句子进一步分割"""
        sentences = re.split(r'(?<=[。！？.!?])\s*', text)
        chunks = []
        current = ""
        index = start_index
        for sentence in sentences:
            if len(current) + len(sentence) <= self.chunk_size:
                current += sentence
            else:
                if current:
                    chunks.append(DocumentChunk(id=f"{document_id}_chunk_{index}", document_id=document_id, content=current, chunk_index=index))
                    index += 1
                current = sentence
        if current:
            chunks.append(DocumentChunk(id=f"{document_id}_chunk_{index}", document_id=document_id, content=current, chunk_index=index))
        return chunks
