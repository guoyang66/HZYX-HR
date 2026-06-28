"""
应用配置中心 - 从环境变量/.env文件加载所有配置项
对应 Java 版本: application.yml + AppConfig.java
使用 Pydantic Settings 实现类型安全的配置管理
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置类，所有配置项可通过环境变量或 .env 文件覆盖"""

    # ==================== 应用基础配置 ====================
    app_name: str = "hzyx-hr"
    port: int = 8080
    debug: bool = True

    # ==================== PostgreSQL 数据库配置 ====================
    db_host: str = "localhost"
    db_port: int = 15432
    db_name: str = "smarthr"
    db_user: str = "smarthr"
    db_password: str = "smarthr123"

    @property
    def database_url(self) -> str:
        """异步数据库连接URL（使用 asyncpg 驱动）"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def sync_database_url(self) -> str:
        """同步数据库连接URL（用于少数需要同步操作的场景）"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # ==================== Redis 缓存配置 ====================
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    # ==================== Neo4j 知识图谱配置 ====================
    neo4j_host: str = "localhost"
    neo4j_port: int = 7687
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j123"

    @property
    def neo4j_uri(self) -> str:
        """Neo4j Bolt 协议连接地址"""
        return f"bolt://{self.neo4j_host}:{self.neo4j_port}"

    # ==================== Milvus 向量数据库配置 ====================
    milvus_enabled: bool = True
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection_name: str = "smart_hr_resumes"          # 简历向量集合
    milvus_question_collection_name: str = "smart_hr_questions"  # 面试题向量集合
    milvus_embedding_dimension: int = 1536   # 向量维度（与模型输出对齐）
    milvus_index_type: str = "IVF_FLAT"      # 索引类型：IVF倒排索引
    milvus_metric_type: str = "COSINE"       # 相似度度量：余弦相似度
    milvus_nlist: int = 1024                 # IVF 聚类中心数
    milvus_nprobe: int = 16                  # 搜索时探测的聚类数

    @property
    def milvus_uri(self) -> str:
        return f"http://{self.milvus_host}:{self.milvus_port}"

    # ==================== JWT 认证配置 ====================
    jwt_secret: str = "c21hcnQtaHItand0LXNlY3JldC1rZXktZm9yLWRldmVsb3BtZW50LW9ubHktcGxlYXNlLWNoYW5nZS1pbi1wcm9kdWN0aW9u"
    jwt_expiration: int = 86400000         # 访问令牌有效期：24小时（毫秒）
    jwt_refresh_expiration: int = 604800000  # 刷新令牌有效期：7天（毫秒）
    jwt_token_prefix: str = "Bearer "
    jwt_header_name: str = "Authorization"

    # ==================== AI 模型配置 ====================
    ai_default_model: str = "aliyun"        # 默认AI模型
    ai_aliyun_enabled: bool = True
    ai_openai_enabled: bool = False

    # 阿里云百炼（DashScope）配置
    dashscope_api_key: str = ""
    dashscope_chat_model: str = "qwen-plus"            # 对话模型
    dashscope_embedding_model: str = "text-embedding-v2"  # 文本嵌入模型
    dashscope_temperature: float = 0.7                  # 生成温度（0-1，越高越随机）

    # OpenAI 配置
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/"
    openai_chat_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # ==================== 文件存储配置 ====================
    storage_path: str = "./uploads"          # 上传文件存储路径

    # 文件上传
    max_upload_size: int = 10 * 1024 * 1024  # 最大上传文件大小：10MB

    # Pydantic 配置：从 .env 文件读取，忽略多余字段
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# 全局配置单例
settings = Settings()
