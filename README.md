# HZYX-HR 智能招聘与面试助手

## 1. 项目简介 🚀
- 面向 HR 与面试官的智能招聘助手，覆盖简历解析、岗位匹配、面试题生成与模型切换。
- 引入 **Neo4j 知识图谱**（预置约 200 个技能节点及依赖关系）作为 HR 匹配的图谱评判依据；
- 引入 **Milvus 向量数据库** 作为 RAG 知识库，分为“企业特定金融知识”与“通用知识”两部分，支撑面试官题库生成与语义检索。
- 采用 **模型适配器模式**，可插拔接入多种大模型（当前支持阿里云百炼、OpenAI）；新增模型只需实现 Adapter 并注册到 ModelRouter。
- 后端基于 FastAPI + SQLAlchemy + LangChain + LangGraph，整合 Milvus/Neo4j/PostgreSQL；前端基于 React + Ant Design。

## 2. 技术栈与架构 🧰
- 前端：React 18、TypeScript、Vite、Ant Design、Zustand。
- 后端：Web 框架：FastAPI ORM：SQLAlchemy 2.0 async + asyncpg  AI： LangChain + LangGraph
- 数据与存储：PostgreSQL、Neo4j、Milvus。
- 运维：Docker / Docker Compose。

## 3. 系统架构图 🧭
**HR 流程：简历/岗位 → Neo4j 知识图谱 → 混合打分（图谱评分 + LLM 评估）**
```mermaid
flowchart LR
    FE_HR[前端·HR 页面] --> GW_HR[API 网关/路由]
    subgraph Backend_HR [后端服务·后端服务·FastAPI + SQLAlchemy 2.0 async + asyncpg + LangChain + LangGraph]
        GW_HR --> ResumeSvc[简历解析]
        GW_HR --> MatchSvc[匹配/图谱]
        GW_HR --> PositionSvc[岗位]
    end
    MatchSvc --> Neo4j[(Neo4j\n技能图谱)]
    MatchSvc --> HybridScore[混合打分\n图谱覆盖率/深度/前置完整度 + LLM 评估]
    HybridScore --> ModelRouter[模型路由器]
    ModelRouter --> Dashscope[阿里云百炼]
    ModelRouter --> OpenAI[OpenAI]
    PositionSvc --> PG[(PostgreSQL\n业务数据)]
    ResumeSvc --> PG
    MatchSvc --> PG
```

**面试官流程：岗位/技能 → RAG（Milvus 题库/技能向量）→ LLM**
```mermaid
flowchart LR
    FE_INT[前端·面试官页面] --> GW_INT[API 网关/路由]
    subgraph Backend_INT [后端服务·FastAPI + SQLAlchemy 2.0 async + asyncpg + LangChain + LangGraph]
        GW_INT --> InterviewSvc[面试题生成]
        GW_INT --> PositionSvc2[岗位]
    end
    InterviewSvc --> Milvus2[(Milvus\nRAG：题库/技能向量检索)]
    InterviewSvc --> ModelRouter2[模型路由器]
    ModelRouter2 --> Dashscope2[阿里云百炼]
    ModelRouter2 --> OpenAI2[OpenAI]
    PositionSvc2 --> PG2[(PostgreSQL\n业务数据)]
```

> HR 通过 Neo4j 图谱进行技能匹配后送入 LLM；面试官流程以 Milvus RAG 检索题库/技能语义，再送入 LLM。

## 4. 功能特性 🎯
### HR 🤝
- 岗位管理：岗位创建/编辑/删除，岗位列表。
- 简历处理：上传简历、技能提取、查看简历详情。
- 匹配分析：岗位 ⇄ 简历互相匹配，支持混合打分报告，匹配历史/详情查看。
- 记录管理：匹配结果列表、历史查询。

### 面试官 🎤
- 题目生成：按岗位或技能生成面试题，可选难度与题量。
- 记录管理：生成历史查看、记录删除。

### 通用 🧩
- 认证：登录/注册（JWT），当前用户信息。
- 模型：AI 模型列表与切换（阿里云百炼 / OpenAI，适配器模式）。
- API：Swagger UI。

## 5. 目录结构
- `back-python/`：langchain流程节点 后端。
- `front/`：React 前端。
- `docker/`：基础设施与一键部署的 Compose 文件、初始化脚本。

## 6. 环境准备
- Node.js 18+（含 npm）。
- Docker Desktop（含 Docker Compose）。

## 7. 快速开始 ⚡
> 详细步骤请参见 `DEV_GUIDE.md`。

1) 启动基础设施（本地开发）  
```bash
cd docker
docker-compose -f docker-compose.dev.yml up -d
```

2) 初始化 Neo4j 知识图谱  
- 浏览器执行 `docker/neo4j/init.cypher` 和 `docker/neo4j/init-skills-extended.cypher`，或使用 `cypher-shell`（详见 DEV_GUIDE）。

3) 配置大模型 API Key（至少需阿里云百炼，OpenAI 可选）  
```bash
export DASHSCOPE_API_KEY=你的阿里云百炼API_KEY
export OPENAI_API_KEY=你的OpenAI_API_KEY   # 可选
```

4)安装本地依赖
```bash
cd back-py
pip install -r requirements.txt
```

5) 启动后端（本地开发）  
```bash
cd back-py
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

6) 启动前端（本地开发）  
```bash
cd front
npm install
npm run dev
```

7) 全栈 Docker 一键启动（可选）  
```bash
cd docker
export DASHSCOPE_API_KEY=你的阿里云百炼API_KEY
export OPENAI_API_KEY=你的OpenAI_API_KEY   # 可选
docker-compose up -d
```

- Swagger API 文档：`http://localhost:8080/swagger-ui.html`
- 默认端口：后端 8080，前端 5173（开发）/ 3000（容器），Postgres 15432(dev)/5432(prod compose)，Neo4j 7474/7687，Milvus 19530/9091。

（更多启动、调试与排障说明，请查看 `DEV_GUIDE.md`）

