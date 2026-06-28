// HZYX-HR Neo4j 知识图谱初始化脚本
// @author QinFeng Luo
// @date 2026/01/09

// 创建约束
CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT category_code IF NOT EXISTS FOR (c:SkillCategory) REQUIRE c.code IS UNIQUE;

// 创建技能分类节点
MERGE (c1:SkillCategory {code: 'BACKEND', name: '后端开发', description: '服务端开发相关技能'})
MERGE (c2:SkillCategory {code: 'FRONTEND', name: '前端开发', description: '客户端开发相关技能'})
MERGE (c3:SkillCategory {code: 'DATABASE', name: '数据库', description: '数据库相关技能'})
MERGE (c4:SkillCategory {code: 'DEVOPS', name: 'DevOps', description: '运维与部署相关技能'})
MERGE (c5:SkillCategory {code: 'AI', name: '人工智能', description: 'AI与机器学习相关技能'})
MERGE (c6:SkillCategory {code: 'TESTING', name: '测试', description: '软件测试相关技能'})
MERGE (c7:SkillCategory {code: 'MANAGEMENT', name: '项目管理', description: '项目管理相关技能'})
MERGE (c8:SkillCategory {code: 'GENERAL', name: '通用能力', description: '通用软技能'});

// ========== 后端开发技能 ==========
// Java 生态
MERGE (java:Skill {name: 'Java', level: 2, description: 'Java 编程语言', keywords: ['JDK', 'JVM', 'Java SE']})
MERGE (oop:Skill {name: '面向对象编程', level: 1, description: 'OOP 设计思想', keywords: ['OOP', '封装', '继承', '多态']})
MERGE (spring:Skill {name: 'Spring Framework', level: 3, description: 'Spring 核心框架', keywords: ['IoC', 'AOP', 'DI']})
MERGE (springboot:Skill {name: 'Spring Boot', level: 3, description: 'Spring Boot 快速开发框架', keywords: ['自动配置', '起步依赖']})
MERGE (springcloud:Skill {name: 'Spring Cloud', level: 4, description: 'Spring Cloud 微服务框架', keywords: ['微服务', 'Nacos', 'Gateway']})
MERGE (springai:Skill {name: 'Spring AI', level: 4, description: 'Spring AI 框架', keywords: ['LLM', 'Embedding', 'RAG']})
MERGE (mybatis:Skill {name: 'MyBatis', level: 3, description: 'MyBatis ORM 框架', keywords: ['ORM', 'Mapper', 'SQL']})
MERGE (jpa:Skill {name: 'JPA', level: 3, description: 'Java Persistence API', keywords: ['Hibernate', 'ORM']})
MERGE (jvm:Skill {name: 'JVM 调优', level: 4, description: 'JVM 性能调优', keywords: ['GC', '内存模型', '性能优化']})
MERGE (concurrent:Skill {name: 'Java 并发编程', level: 4, description: 'Java 多线程与并发', keywords: ['多线程', '锁', '线程池']})

// Python 生态
MERGE (python:Skill {name: 'Python', level: 2, description: 'Python 编程语言', keywords: ['Python3', 'PEP']})
MERGE (django:Skill {name: 'Django', level: 3, description: 'Django Web 框架', keywords: ['MTV', 'ORM']})
MERGE (flask:Skill {name: 'Flask', level: 3, description: 'Flask 轻量级框架', keywords: ['微框架', 'WSGI']})
MERGE (fastapi:Skill {name: 'FastAPI', level: 3, description: 'FastAPI 异步框架', keywords: ['异步', 'OpenAPI']})

// Go 生态
MERGE (golang:Skill {name: 'Go', level: 2, description: 'Go 编程语言', keywords: ['Golang', '协程']})
MERGE (gin:Skill {name: 'Gin', level: 3, description: 'Gin Web 框架', keywords: ['HTTP', '中间件']})

// Node.js 生态
MERGE (nodejs:Skill {name: 'Node.js', level: 2, description: 'Node.js 运行时', keywords: ['V8', 'NPM', '事件驱动']})
MERGE (express:Skill {name: 'Express', level: 3, description: 'Express 框架', keywords: ['中间件', '路由']})
MERGE (nestjs:Skill {name: 'NestJS', level: 3, description: 'NestJS 框架', keywords: ['TypeScript', '装饰器']})

// 后端技能关系
MERGE (java)-[:REQUIRES]->(oop)
MERGE (spring)-[:REQUIRES]->(java)
MERGE (springboot)-[:REQUIRES]->(spring)
MERGE (springcloud)-[:REQUIRES]->(springboot)
MERGE (springai)-[:REQUIRES]->(springboot)
MERGE (mybatis)-[:REQUIRES]->(java)
MERGE (jpa)-[:REQUIRES]->(java)
MERGE (jvm)-[:REQUIRES]->(java)
MERGE (concurrent)-[:REQUIRES]->(java)
MERGE (django)-[:REQUIRES]->(python)
MERGE (flask)-[:REQUIRES]->(python)
MERGE (fastapi)-[:REQUIRES]->(python)
MERGE (gin)-[:REQUIRES]->(golang)
MERGE (express)-[:REQUIRES]->(nodejs)
MERGE (nestjs)-[:REQUIRES]->(nodejs)

// 后端技能分类
MERGE (java)-[:BELONGS_TO]->(c1)
MERGE (spring)-[:BELONGS_TO]->(c1)
MERGE (springboot)-[:BELONGS_TO]->(c1)
MERGE (springcloud)-[:BELONGS_TO]->(c1)
MERGE (springai)-[:BELONGS_TO]->(c1)
MERGE (mybatis)-[:BELONGS_TO]->(c1)
MERGE (jpa)-[:BELONGS_TO]->(c1)
MERGE (python)-[:BELONGS_TO]->(c1)
MERGE (django)-[:BELONGS_TO]->(c1)
MERGE (flask)-[:BELONGS_TO]->(c1)
MERGE (fastapi)-[:BELONGS_TO]->(c1)
MERGE (golang)-[:BELONGS_TO]->(c1)
MERGE (gin)-[:BELONGS_TO]->(c1)
MERGE (nodejs)-[:BELONGS_TO]->(c1)
MERGE (express)-[:BELONGS_TO]->(c1)
MERGE (nestjs)-[:BELONGS_TO]->(c1)

// ========== 前端开发技能 ==========
MERGE (html:Skill {name: 'HTML/CSS', level: 1, description: 'Web 基础', keywords: ['HTML5', 'CSS3', '布局']})
MERGE (js:Skill {name: 'JavaScript', level: 2, description: 'JavaScript 语言', keywords: ['ES6+', 'DOM', '异步']})
MERGE (ts:Skill {name: 'TypeScript', level: 3, description: 'TypeScript 语言', keywords: ['类型系统', '泛型']})
MERGE (react:Skill {name: 'React', level: 3, description: 'React 框架', keywords: ['Hooks', 'JSX', '组件化']})
MERGE (vue:Skill {name: 'Vue', level: 3, description: 'Vue 框架', keywords: ['响应式', '组合式API']})
MERGE (angular:Skill {name: 'Angular', level: 3, description: 'Angular 框架', keywords: ['依赖注入', 'RxJS']})
MERGE (nextjs:Skill {name: 'Next.js', level: 4, description: 'Next.js 框架', keywords: ['SSR', 'SSG', 'App Router']})
MERGE (webpack:Skill {name: 'Webpack', level: 3, description: 'Webpack 构建工具', keywords: ['打包', 'Loader', 'Plugin']})
MERGE (vite:Skill {name: 'Vite', level: 3, description: 'Vite 构建工具', keywords: ['ESM', '热更新']})

// 前端技能关系
MERGE (js)-[:REQUIRES]->(html)
MERGE (ts)-[:REQUIRES]->(js)
MERGE (react)-[:REQUIRES]->(js)
MERGE (vue)-[:REQUIRES]->(js)
MERGE (angular)-[:REQUIRES]->(ts)
MERGE (nextjs)-[:REQUIRES]->(react)
MERGE (webpack)-[:REQUIRES]->(js)
MERGE (vite)-[:REQUIRES]->(js)

// 前端技能分类
MERGE (html)-[:BELONGS_TO]->(c2)
MERGE (js)-[:BELONGS_TO]->(c2)
MERGE (ts)-[:BELONGS_TO]->(c2)
MERGE (react)-[:BELONGS_TO]->(c2)
MERGE (vue)-[:BELONGS_TO]->(c2)
MERGE (angular)-[:BELONGS_TO]->(c2)
MERGE (nextjs)-[:BELONGS_TO]->(c2)
MERGE (webpack)-[:BELONGS_TO]->(c2)
MERGE (vite)-[:BELONGS_TO]->(c2)

// ========== 数据库技能 ==========
MERGE (sql:Skill {name: 'SQL', level: 2, description: 'SQL 查询语言', keywords: ['查询', '索引', '优化']})
MERGE (mysql:Skill {name: 'MySQL', level: 3, description: 'MySQL 数据库', keywords: ['InnoDB', '主从', '分库分表']})
MERGE (postgresql:Skill {name: 'PostgreSQL', level: 3, description: 'PostgreSQL 数据库', keywords: ['JSONB', '扩展']})
MERGE (redis:Skill {name: 'Redis', level: 3, description: 'Redis 缓存', keywords: ['缓存', '数据结构', '集群']})
MERGE (mongodb:Skill {name: 'MongoDB', level: 3, description: 'MongoDB 文档数据库', keywords: ['NoSQL', '文档', '聚合']})
MERGE (elasticsearch:Skill {name: 'Elasticsearch', level: 3, description: 'Elasticsearch 搜索引擎', keywords: ['全文检索', '分词', '聚合']})
MERGE (neo4j:Skill {name: 'Neo4j', level: 3, description: 'Neo4j 图数据库', keywords: ['图数据库', 'Cypher', '知识图谱']})
MERGE (milvus:Skill {name: 'Milvus', level: 3, description: 'Milvus 向量数据库', keywords: ['向量检索', 'RAG']})

// 数据库技能关系
MERGE (mysql)-[:REQUIRES]->(sql)
MERGE (postgresql)-[:REQUIRES]->(sql)

// 数据库技能分类
MERGE (sql)-[:BELONGS_TO]->(c3)
MERGE (mysql)-[:BELONGS_TO]->(c3)
MERGE (postgresql)-[:BELONGS_TO]->(c3)
MERGE (redis)-[:BELONGS_TO]->(c3)
MERGE (mongodb)-[:BELONGS_TO]->(c3)
MERGE (elasticsearch)-[:BELONGS_TO]->(c3)
MERGE (neo4j)-[:BELONGS_TO]->(c3)
MERGE (milvus)-[:BELONGS_TO]->(c3)

// ========== DevOps 技能 ==========
MERGE (linux:Skill {name: 'Linux', level: 2, description: 'Linux 操作系统', keywords: ['Shell', '命令行']})
MERGE (docker:Skill {name: 'Docker', level: 3, description: 'Docker 容器', keywords: ['容器', '镜像', 'Compose']})
MERGE (k8s:Skill {name: 'Kubernetes', level: 4, description: 'Kubernetes 容器编排', keywords: ['K8s', 'Pod', 'Service']})
MERGE (jenkins:Skill {name: 'Jenkins', level: 3, description: 'Jenkins CI/CD', keywords: ['Pipeline', '自动化']})
MERGE (git:Skill {name: 'Git', level: 2, description: 'Git 版本控制', keywords: ['分支', '合并', 'GitHub']})
MERGE (nginx:Skill {name: 'Nginx', level: 3, description: 'Nginx 服务器', keywords: ['反向代理', '负载均衡']})

// DevOps 技能关系
MERGE (docker)-[:REQUIRES]->(linux)
MERGE (k8s)-[:REQUIRES]->(docker)

// DevOps 技能分类
MERGE (linux)-[:BELONGS_TO]->(c4)
MERGE (docker)-[:BELONGS_TO]->(c4)
MERGE (k8s)-[:BELONGS_TO]->(c4)
MERGE (jenkins)-[:BELONGS_TO]->(c4)
MERGE (git)-[:BELONGS_TO]->(c4)
MERGE (nginx)-[:BELONGS_TO]->(c4)

// ========== AI 技能 ==========
MERGE (ml:Skill {name: '机器学习', level: 3, description: '机器学习基础', keywords: ['ML', '监督学习', '无监督学习']})
MERGE (dl:Skill {name: '深度学习', level: 4, description: '深度学习', keywords: ['神经网络', 'CNN', 'RNN']})
MERGE (pytorch:Skill {name: 'PyTorch', level: 3, description: 'PyTorch 框架', keywords: ['张量', '自动微分']})
MERGE (tensorflow:Skill {name: 'TensorFlow', level: 3, description: 'TensorFlow 框架', keywords: ['Keras', '模型']})
MERGE (nlp:Skill {name: 'NLP', level: 4, description: '自然语言处理', keywords: ['文本处理', '语义理解']})
MERGE (cv:Skill {name: '计算机视觉', level: 4, description: '计算机视觉', keywords: ['图像处理', '目标检测']})
MERGE (llm:Skill {name: '大语言模型', level: 4, description: 'LLM 大语言模型', keywords: ['GPT', 'Prompt', '微调']})
MERGE (rag:Skill {name: 'RAG', level: 4, description: '检索增强生成', keywords: ['向量检索', '知识库']})
MERGE (langchain:Skill {name: 'LangChain', level: 4, description: 'LangChain 框架', keywords: ['Agent', 'Chain']})
MERGE (embedding:Skill {name: 'Embedding', level: 3, description: '文本向量化', keywords: ['词向量', '语义表示']})

// AI 技能关系
MERGE (dl)-[:REQUIRES]->(ml)
MERGE (pytorch)-[:REQUIRES]->(python)
MERGE (pytorch)-[:REQUIRES]->(dl)
MERGE (tensorflow)-[:REQUIRES]->(python)
MERGE (tensorflow)-[:REQUIRES]->(dl)
MERGE (nlp)-[:REQUIRES]->(dl)
MERGE (cv)-[:REQUIRES]->(dl)
MERGE (llm)-[:REQUIRES]->(nlp)
MERGE (rag)-[:REQUIRES]->(llm)
MERGE (rag)-[:REQUIRES]->(embedding)
MERGE (langchain)-[:REQUIRES]->(llm)
MERGE (springai)-[:RELATED_TO]->(rag)
MERGE (springai)-[:RELATED_TO]->(llm)
MERGE (milvus)-[:RELATED_TO]->(rag)
MERGE (neo4j)-[:RELATED_TO]->(rag)

// AI 技能分类
MERGE (ml)-[:BELONGS_TO]->(c5)
MERGE (dl)-[:BELONGS_TO]->(c5)
MERGE (pytorch)-[:BELONGS_TO]->(c5)
MERGE (tensorflow)-[:BELONGS_TO]->(c5)
MERGE (nlp)-[:BELONGS_TO]->(c5)
MERGE (cv)-[:BELONGS_TO]->(c5)
MERGE (llm)-[:BELONGS_TO]->(c5)
MERGE (rag)-[:BELONGS_TO]->(c5)
MERGE (langchain)-[:BELONGS_TO]->(c5)
MERGE (embedding)-[:BELONGS_TO]->(c5)

// ========== 测试技能 ==========
MERGE (functest:Skill {name: '功能测试', level: 2, description: '功能测试', keywords: ['测试用例', '缺陷']})
MERGE (autotest:Skill {name: '自动化测试', level: 3, description: '自动化测试', keywords: ['脚本', '框架']})
MERGE (perftest:Skill {name: '性能测试', level: 3, description: '性能测试', keywords: ['压测', 'JMeter']})
MERGE (junit:Skill {name: 'JUnit', level: 3, description: 'JUnit 测试框架', keywords: ['单元测试', '断言']})
MERGE (selenium:Skill {name: 'Selenium', level: 3, description: 'Selenium UI测试', keywords: ['Web测试', '元素定位']})
MERGE (pytest:Skill {name: 'Pytest', level: 3, description: 'Pytest 测试框架', keywords: ['Python测试', 'fixture']})

// 测试技能关系
MERGE (autotest)-[:REQUIRES]->(functest)
MERGE (junit)-[:REQUIRES]->(java)
MERGE (selenium)-[:REQUIRES]->(autotest)
MERGE (pytest)-[:REQUIRES]->(python)

// 测试技能分类
MERGE (functest)-[:BELONGS_TO]->(c6)
MERGE (autotest)-[:BELONGS_TO]->(c6)
MERGE (perftest)-[:BELONGS_TO]->(c6)
MERGE (junit)-[:BELONGS_TO]->(c6)
MERGE (selenium)-[:BELONGS_TO]->(c6)
MERGE (pytest)-[:BELONGS_TO]->(c6)

// ========== 项目管理技能 ==========
MERGE (scrum:Skill {name: 'Scrum', level: 2, description: 'Scrum 敏捷方法', keywords: ['Sprint', '迭代']})
MERGE (agile:Skill {name: '敏捷开发', level: 2, description: '敏捷开发方法论', keywords: ['Agile', '迭代']})
MERGE (jira:Skill {name: 'JIRA', level: 2, description: 'JIRA 项目管理工具', keywords: ['任务管理', '看板']})
MERGE (requirement:Skill {name: '需求分析', level: 3, description: '需求分析能力', keywords: ['PRD', '用例']})
MERGE (risk:Skill {name: '风险管理', level: 3, description: '风险管理', keywords: ['识别', '应对']})

// 项目管理技能关系
MERGE (scrum)-[:REQUIRES]->(agile)

// 项目管理技能分类
MERGE (scrum)-[:BELONGS_TO]->(c7)
MERGE (agile)-[:BELONGS_TO]->(c7)
MERGE (jira)-[:BELONGS_TO]->(c7)
MERGE (requirement)-[:BELONGS_TO]->(c7)
MERGE (risk)-[:BELONGS_TO]->(c7)

// ========== 通用能力 ==========
MERGE (comm:Skill {name: '沟通能力', level: 1, description: '沟通表达能力', keywords: ['表达', '倾听']})
MERGE (team:Skill {name: '团队协作', level: 1, description: '团队协作能力', keywords: ['配合', '协调']})
MERGE (learn:Skill {name: '学习能力', level: 1, description: '持续学习能力', keywords: ['自学', '成长']})
MERGE (problem:Skill {name: '问题解决', level: 2, description: '问题分析解决能力', keywords: ['分析', '方案']})
MERGE (logic:Skill {name: '逻辑思维', level: 2, description: '逻辑思维能力', keywords: ['推理', '分析']})

// 通用能力分类
MERGE (comm)-[:BELONGS_TO]->(c8)
MERGE (team)-[:BELONGS_TO]->(c8)
MERGE (learn)-[:BELONGS_TO]->(c8)
MERGE (problem)-[:BELONGS_TO]->(c8)
MERGE (logic)-[:BELONGS_TO]->(c8)

// 输出统计
MATCH (s:Skill) RETURN count(s) as totalSkills;
MATCH (c:SkillCategory) RETURN count(c) as totalCategories;
MATCH ()-[r:REQUIRES]->() RETURN count(r) as requiresRelations;
MATCH ()-[r:BELONGS_TO]->() RETURN count(r) as belongsToRelations;


