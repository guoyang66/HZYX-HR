"""
岗位服务 - 招聘岗位的增删改查业务逻辑
"""
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.position import Position
from app.schemas.position import PositionCreateRequest, PositionDTO
from app.api.exception_handlers import BusinessException


class PositionService:
    """岗位服务 - 管理招聘岗位的完整生命周期（CRUD），支持软删除"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_position(self, request: PositionCreateRequest, user_id: int) -> PositionDTO:
        """创建新岗位"""
        position = Position(
            title=request.title,
            company=request.company,
            salary_range=request.salary_range,
            experience=request.experience,
            education=request.education,
            location=request.location,
            responsibilities=request.responsibilities,
            requirements=request.requirements,
            skills=request.skills,
            created_by=user_id,
        )
        self.db.add(position)
        await self.db.flush()
        return self._to_dto(position)

    async def update_position(self, position_id: int, request: PositionCreateRequest, user_id: int) -> PositionDTO:
        """更新岗位信息（只更新未删除的）"""
        result = await self.db.execute(
            select(Position).where(Position.id == position_id, Position.deleted == False)
        )
        position = result.scalar_one_or_none()
        if not position:
            raise BusinessException("岗位不存在", 404)

        position.title = request.title
        position.company = request.company
        position.salary_range = request.salary_range
        position.experience = request.experience
        position.education = request.education
        position.location = request.location
        position.responsibilities = request.responsibilities
        position.requirements = request.requirements
        position.skills = request.skills
        await self.db.flush()
        return self._to_dto(position)

    async def delete_position(self, position_id: int, user_id: int):
        """软删除岗位（标记deleted=True）"""
        result = await self.db.execute(
            select(Position).where(Position.id == position_id, Position.deleted == False)
        )
        position = result.scalar_one_or_none()
        if not position:
            raise BusinessException("岗位不存在", 404)
        position.deleted = True
        await self.db.flush()

    async def get_position(self, position_id: int) -> PositionDTO:
        """获取岗位详情（排除已删除的）"""
        result = await self.db.execute(
            select(Position).where(Position.id == position_id, Position.deleted == False)
        )
        position = result.scalar_one_or_none()
        if not position:
            raise BusinessException("岗位不存在", 404)
        return self._to_dto(position)

    async def list_positions(self, page: int, size: int, keyword: str | None = None) -> dict:
        """分页查询岗位列表，支持关键词搜索（标题/公司）"""
        query = select(Position).where(Position.deleted == False)
        count_query = select(func.count()).select_from(Position).where(Position.deleted == False)

        if keyword:
            keyword_filter = or_(
                Position.title.ilike(f"%{keyword}%"),
                Position.company.ilike(f"%{keyword}%"),
            )
            query = query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.offset(page * size).limit(size).order_by(Position.created_at.desc())
        result = await self.db.execute(query)
        positions = result.scalars().all()

        return {
            "content": [self._to_dto(p) for p in positions],
            "totalElements": total,
            "totalPages": max(1, (total + size - 1) // size),
            "number": page,
            "size": size,
        }

    async def get_all_positions(self) -> list[PositionDTO]:
        """获取所有未删除岗位（用于下拉选择）"""
        query = select(Position).where(Position.deleted == False).order_by(Position.title)
        result = await self.db.execute(query)
        positions = result.scalars().all()
        return [self._to_dto(p) for p in positions]

    @staticmethod
    def _to_dto(p: Position) -> PositionDTO:
        """ORM转DTO"""
        return PositionDTO(
            id=p.id,
            title=p.title,
            company=p.company,
            salary_range=p.salary_range,
            experience=p.experience,
            education=p.education,
            location=p.location,
            responsibilities=p.responsibilities,
            requirements=p.requirements,
            skills=p.skills,
            created_by=p.created_by,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
