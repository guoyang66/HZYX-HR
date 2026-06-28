# HZYX-HR 开发测试指南

## 📋 前置条件

确保你已安装：

- **Docker Desktop**（包含 Docker Compose）
- **Node.js 18+**（含 npm）

## 🚀 快速启动步骤

### 第一步：启动基础设施服务

```bash
# 进入 docker 目录
cd /HZYX-HR/docker

# 启动所有基础设施（PostgreSQL、Redis、Neo4j、Milvus）
docker-compose -f docker-compose.dev.yml up -d

# 查看服务状态
docker-compose -f docker-compose.dev.yml ps
```

等待所有服务启动（约 1-2 分钟），可以通过以下方式验证：

| 服务       | 验证方式                                             |
| ---------- | ---------------------------------------------------- |
| PostgreSQL | `docker exec smarthr-postgres pg_isready -U smarthr` |
| Redis      | `docker exec smarthr-redis redis-cli ping`           |
| Neo4j      | 浏览器访问 http://localhost:7474                     |
| Milvus     | `curl http://localhost:9091/healthz`                 |

### 第二步：初始化 Neo4j 知识图谱

Neo4j 启动后需要手动导入技能数据：

```bash
# 方法1：通过 Neo4j Browser 执行
# 1. 访问 http://localhost:7474
# 2. 登录（用户名: neo4j, 密码: neo4j123）
# 3. 复制 docker/neo4j/init.cypher 的内容执行
# 4. 复制 docker/neo4j/init-skills-extended.cypher 的内容执行

# 方法2：通过命令行执行
docker exec smarthr-neo4j cypher-shell -u neo4j -p neo4j123 < ./neo4j/init.cypher
docker exec smarthr-neo4j cypher-shell -u neo4j -p neo4j123 < ./neo4j/init-skills-extended.cypher
```

### 第三步：配置阿里云 API Key

在启动后端之前，需要在application.yml中配置阿里云百炼 以及 openAi的 API Key：

```bash
# 方法1：设置环境变量（推荐）
export DASHSCOPE_API_KEY=你的阿里云百炼API_KEY

# 方法2：直接修改 application.yml
# 编辑 back/src/main/resources/application.yml
# 找到 api-key: ${DASHSCOPE_API_KEY:} 改为你的 key
```

> 📌 如果暂时没有 API Key，可以先不配置，但 AI 相关功能（匹配分析、面试题生成）会失败

### 第四步：启动后端服务

```bash
# 进入后端目录
cd HZYX-HR/back-py

cd back-py
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

验证后端启动成功：

- 访问 http://localhost:8080/swagger-ui.html 查看 API 文档
- 或执行 `curl http://localhost:8080/actuator/health`

### 第五步：启动前端服务

```bash
# 新开一个终端，进入前端目录
cd HZYX-HR/front

# 安装依赖（首次启动需要）
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 查看前端页面

---

## 🧪 功能测试

### 1. 用户认证测试

**测试注册：**

1. 访问 http://localhost:5173/register
2. 填写用户名、邮箱、密码
3. 选择角色（HR 或 面试官）
4. 点击注册

**测试登录：**

1. 访问 http://localhost:5173/login
2. 使用预置账号登录：
   - HR 账号：`hr_admin` / `password`
   - 面试官账号：`interviewer_admin` / `password`

### 2. HR 功能测试

登录 HR 账号后：

1. **查看工作台**：`/hr/dashboard`
2. **岗位管理**：`/hr/positions`
   - 查看预置的 20 个岗位
   - 新建岗位
   - 编辑/删除岗位
3. **简历上传**：`/hr/resume-upload`
   - 上传 PDF/Word/TXT 格式简历
   - 查看提取的技能
   - 执行匹配分析
4. **匹配历史**：`/hr/match-history`

### 3. 面试官功能测试

登录面试官账号后：

1. **查看工作台**：`/interviewer/dashboard`
2. **生成面试题**：`/interviewer/generate`
   - 选择岗位或输入技能
   - 设置难度和题目数量
   - 点击生成
3. **生成历史**：`/interviewer/history`

### 4. API 测试（可选）

使用 Swagger UI 或 curl 测试：

```bash
# 登录获取 Token
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"hr_admin","password":"password123"}'

# 使用返回的 token 调用其他 API
curl http://localhost:8080/api/hr/positions \
  -H "Authorization: Bearer <your_token>"
```

---

## 🛠 常用命令

### Docker 相关

```bash
# 查看容器状态
docker-compose -f docker-compose.dev.yml ps

# 查看容器日志
docker-compose -f docker-compose.dev.yml logs -f postgres
docker-compose -f docker-compose.dev.yml logs -f neo4j
docker-compose -f docker-compose.dev.yml logs -f milvus

# 停止所有服务
docker-compose -f docker-compose.dev.yml stop

# 停止并删除容器（保留数据）
docker-compose -f docker-compose.dev.yml down

# 停止并删除容器和数据（重新开始）
docker-compose -f docker-compose.dev.yml down -v
```

### 数据库连接

```bash
# 连接 PostgreSQL
docker exec -it smarthr-postgres psql -U smarthr -d smarthr

# 连接 Redis
docker exec -it smarthr-redis redis-cli

# Neo4j Browser
# 浏览器访问 http://localhost:7474
# 用户名: neo4j
# 密码: neo4j123
```

---

## 📊 服务端口一览

| 服务          | 端口  | 说明            |
| ------------- | ----- | --------------- |
| PostgreSQL    | 5432  | 主数据库        |
| Redis         | 6379  | 缓存/会话       |
| Neo4j HTTP    | 7474  | Neo4j Browser   |
| Neo4j Bolt    | 7687  | Neo4j 连接协议  |
| Milvus        | 19530 | 向量数据库      |
| MinIO API     | 9000  | 对象存储        |
| MinIO Console | 9001  | MinIO 控制台    |
| 后端          | 8080  | Spring Boot     |
| 前端          | 5173  | Vite Dev Server |

---

## ❓ 常见问题

### Q1: Docker 服务启动失败

```bash
# 检查端口占用
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# 如果被占用，停止占用进程或修改 docker-compose.dev.yml 中的端口映射
```

### Q2: Neo4j 连接失败

```bash
# 确保 Neo4j 已完全启动（等待 30 秒）
docker logs smarthr-neo4j

# 首次启动可能需要更长时间初始化
```

### Q3: 后端启动报数据库连接错误

```bash
# 确保 PostgreSQL 已启动
docker exec smarthr-postgres pg_isready -U smarthr

# 检查连接配置是否正确
# application.yml 中默认连接 localhost:5432
```

### Q4: 前端无法连接后端

```bash
# 确保后端已启动并监听 8080 端口
curl http://localhost:8080/actuator/health

# 检查 vite.config.ts 中的代理配置
```

### Q5: Milvus 连接超时

```bash
# Milvus 依赖 etcd 和 minio，启动较慢
# 等待 1-2 分钟后重试

# 检查健康状态
curl http://localhost:9091/healthz
```

---

## 🎉 测试完成清单

- [ ] Docker 基础设施启动成功
- [ ] Neo4j 知识图谱初始化完成
- [ ] 后端服务启动成功（可访问 Swagger）
- [ ] 前端服务启动成功
- [ ] 用户注册/登录功能正常
- [ ] HR 岗位管理功能正常
- [ ] HR 简历上传功能正常
- [ ] 面试题生成功能正常（需要 API Key）
