"""
文档解析器 - 支持 PDF、DOCX、TXT 格式的简历文本提取
"""
import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class DocumentParser:
    """文档解析器 - 根据文件扩展名自动选择解析策略"""

    @staticmethod
    def parse(file_path: str, filename: str) -> str:
        """根据文件扩展名分派到对应的解析方法"""
        lower = filename.lower()
        try:
            if lower.endswith(".pdf"):
                return DocumentParser._parse_pdf(file_path)
            elif lower.endswith(".docx"):
                return DocumentParser._parse_docx(file_path)
            elif lower.endswith(".doc"):
                raise ValueError("暂不支持 .doc 格式，请转换为 .docx")
            elif lower.endswith(".txt"):
                return DocumentParser._parse_txt(file_path)
            else:
                raise ValueError("不支持的文件格式: " + filename)
        except Exception as e:
            logger.error("文档解析失败: %s", filename, exc_info=True)
            raise ValueError(f"文档解析失败: {e}")

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """使用 pdfplumber 逐页提取PDF文本"""
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return DocumentParser._clean_text("\n".join(text_parts))

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """使用 python-docx 提取Word文档段落文本"""
        from docx import Document
        doc = Document(file_path)
        text_parts = []
        for para in doc.paragraphs:
            if para.text and para.text.strip():
                text_parts.append(para.text)
        return DocumentParser._clean_text("\n".join(text_parts))

    @staticmethod
    def _parse_txt(file_path: str) -> str:
        """读取纯文本文件（UTF-8编码）"""
        with open(file_path, "r", encoding="utf-8") as f:
            return DocumentParser._clean_text(f.read())

    @staticmethod
    def _clean_text(text: str) -> str:
        """清洗文本：去空字符、合并多余空格/换行"""
        if not text:
            return ""
        text = text.replace("\x00", "")
        import re
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    @staticmethod
    def is_supported(filename: str) -> bool:
        """检查文件扩展名是否受支持（.pdf .docx .txt）"""
        if not filename:
            return False
        lower = filename.lower()
        return any(lower.endswith(ext) for ext in [".pdf", ".docx", ".txt"])
