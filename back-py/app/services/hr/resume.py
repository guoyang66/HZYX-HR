"""
简历服务 - 简历上传、解析、技能提取、索引的完整流水线
对应 Java 版本: ResumeService.java
处理流程：文件上传 -> 文档解析(PDF/DOCX/TXT) -> 技能提取(知识图谱+AI) -> 向量索引(Milvus)
"""
import os
import uuid
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from app.config import settings
from app.models.resume import Resume
from app.schemas.resume import ResumeDTO, ResumeUploadResponse
from app.api.exception_handlers import BusinessException
from app.services.document.parser import DocumentParser
from app.services.document.skill_extractor import SkillExtractor


class ResumeService:
    """简历服务 - 负责简历全生命周期管理（上传、查询、删除）"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_resume(self, file: UploadFile, user_id: int) -> ResumeUploadResponse:
        """简历上传流水线：校验格式 -> 保存文件 -> 文档解析 -> 技能提取 -> 入库 -> 索引"""
        filename = file.filename or "unknown"
        if not DocumentParser.is_supported(filename):
            raise BusinessException("不支持的文件格式: " + filename)

        # 保存上传文件到本地存储
        os.makedirs(settings.storage_path, exist_ok=True)
        file_ext = os.path.splitext(filename)[1]
        saved_name = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(settings.storage_path, saved_name)

        content_bytes = await file.read()
        with open(file_path, "wb") as f:
            f.write(content_bytes)

        # 文档解析：提取纯文本内容
        parser = DocumentParser()
        content = parser.parse(file_path, filename)

        # 技能提取：知识图谱 + AI提取 + 正则兜底
        extractor = SkillExtractor()
        skills = await extractor.extract_skills(content, user_id, self.db)

        # 保存到数据库
        resume = Resume(
            user_id=user_id,
            file_name=filename,
            file_path=file_path,
            content=content,
            extracted_skills=skills,
        )
        self.db.add(resume)
        await self.db.flush()

        # 异步向量索引（非阻塞，失败不影响上传）
        try:
            from app.services.rag.embedding import EmbeddingService
            from app.services.vector.milvus_store import MilvusVectorStore
            store = MilvusVectorStore()
            emb_service = EmbeddingService()
            embedding = emb_service.embed(content)
            await store.add_document(str(resume.id), content, embedding)
        except Exception:
            pass  # 向量库索引失败不阻塞上传流程

        return ResumeUploadResponse(
            resumeId=resume.id,
            fileName=filename,
            parsedContent=content,
            extractedSkills=skills or [],
            message="简历解析完成",
        )

    async def get_resume(self, resume_id: int) -> ResumeDTO:
        """根据ID获取简历详情"""
        result = await self.db.execute(select(Resume).where(Resume.id == resume_id))
        resume = result.scalar_one_or_none()
        if not resume:
            raise BusinessException("简历不存在", 404)
        return self._to_dto(resume)

    async def list_resumes(self, page: int, size: int, keyword: str | None = None) -> dict:
        """分页查询简历列表，支持关键词搜索"""
        query = select(Resume)
        count_query = select(func.count()).select_from(Resume)

        if keyword:
            keyword_filter = Resume.file_name.ilike(f"%{keyword}%")
            query = query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.offset(page * size).limit(size).order_by(Resume.created_at.desc())
        result = await self.db.execute(query)
        resumes = result.scalars().all()

        return {
            "content": [self._to_dto(r) for r in resumes],
            "totalElements": total,
            "totalPages": max(1, (total + size - 1) // size),
            "number": page,
            "size": size,
        }

    async def delete_resume(self, resume_id: int, user_id: int):
        """删除简历：删文件 + 删向量索引 + 删数据库记录"""
        result = await self.db.execute(select(Resume).where(Resume.id == resume_id))
        resume = result.scalar_one_or_none()
        if not resume:
            raise BusinessException("简历不存在", 404)

        # 删除本地文件
        if resume.file_path and os.path.exists(resume.file_path):
            os.remove(resume.file_path)

        # 删除向量索引（非阻塞，失败不影响主流程）
        try:
            from app.services.vector.milvus_store import MilvusVectorStore
            store = MilvusVectorStore()
            await store.delete_document(str(resume_id))
        except Exception:
            pass

        await self.db.delete(resume)
        await self.db.flush()

    async def get_all_resumes(self) -> list[ResumeDTO]:
        """获取所有简历（用于匹配选择列表）"""
        query = select(Resume).order_by(Resume.created_at.desc())
        result = await self.db.execute(query)
        resumes = result.scalars().all()
        return [self._to_dto(r) for r in resumes]

    @staticmethod
    def _to_dto(r: Resume) -> ResumeDTO:
        """ORM转为DTO"""
        return ResumeDTO(
            id=r.id,
            userId=r.user_id,
            fileName=r.file_name,
            filePath=r.file_path,
            content=r.content,
            extractedSkills=r.extracted_skills,
            createdAt=r.created_at,
        )
