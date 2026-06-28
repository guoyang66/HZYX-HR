import hashlib
import json
import os
import sys
import time
from typing import List

from pymilvus import (
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    connections,
    utility,
)


COLLECTION_NAME = os.getenv("COLLECTION_NAME", "smart_hr_questions")
DIM = 1536


def log(msg: str):
    print(msg, flush=True)


def deterministic_embedding(text: str, dim: int = DIM) -> List[float]:
    """
    简单的可复现伪向量：将哈希展开为 0-1 之间的小数，重复至指定维度。
    仅用于示例数据，不适合生产检索。
    """
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    floats = []
    while len(floats) < dim:
        for i in range(0, len(digest), 4):
            chunk = digest[i : i + 4]
            if len(chunk) < 4:
                continue
            num = int.from_bytes(chunk, byteorder="big")
            floats.append((num % 1000) / 1000.0)
            if len(floats) >= dim:
                break
    return floats[:dim]


QUESTIONS = [
    # 通用 Java（5）
    {
        "id": "java_general_01",
        "question": "在 HZYX-HR 科技的微服务中，如何定位和解决 Java 线上内存泄漏？请给出排查思路和工具。",
        "answer": "观察 GC 指标与堆转储；使用 MAT/VisualVM 分析泄漏对象；检查缓存未清理、ThreadLocal 未移除、监听器未注销等；压测复现后修复并验证。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "通用",
    },
    {
        "id": "java_general_02",
        "question": "谈谈 Java 并发中的可见性、有序性问题，并说明在 HZYX-HR 科技的服务里如何用 volatile/锁/原子类来保障正确性。",
        "answer": "可见性靠 volatile/锁/原子类；有序性通过 happens-before 规则；复合操作使用锁或原子类；避免双重检查未加 volatile 等常见坑。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "通用",
    },
    {
        "id": "java_general_03",
        "question": "描述 Spring 事务传播行为在实际项目中的应用，举例 HZYX-HR 科技在批处理任务中的最佳实践。",
        "answer": "常用 REQUIRED、REQUIRES_NEW、NESTED；批处理时外层控制整体，子步骤需要独立提交用 REQUIRES_NEW；回滚范围控制 RuntimeException；结合幂等与重试。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "通用",
    },
    {
        "id": "java_general_04",
        "question": "如何在 HZYX-HR 科技的链路中实现接口幂等？请给出幂等键设计、存储方案以及与重试的配合。",
        "answer": "幂等键=业务单号/外部流水+调用方；唯一索引或幂等表记录状态；先查再写，重复请求直接返回；与重试结合，确保状态机单向流转。",
        "difficulty": "MIDDLE",
        "type": "SCENARIO",
        "domain": "通用",
    },
    {
        "id": "java_general_05",
        "question": "HZYX-HR 科技网关如何实现灰度发布与回滚？请说明路由规则、配置下发和监控指标。",
        "answer": "配置中心下发路由权重；支持按用户/租户/地域分桶；监控成功率、延迟、错误码，异常自动熔断回退；路由与幂等结合避免重复扣费。",
        "difficulty": "SENIOR",
        "type": "SCENARIO",
        "domain": "通用",
    },
    # 企业支付场景（5）
    {
        "id": "pay_01",
        "question": "在我们公司（HZYX-HR 科技）的企业支付系统中，如何设计跨通道的幂等与补单流程？",
        "answer": "幂等键=外部单号+通道+商户；状态机 INIT/PROCESSING/SUCCESS/FAIL；补单通过对账/回调差异触发，同一幂等键复用结果；补单需限速、可重入。",
        "difficulty": "MIDDLE",
        "type": "SCENARIO",
        "domain": "企业金融/支付",
    },
    {
        "id": "pay_02",
        "question": "HZYX-HR 科技的企业账户日切清结算如何避免长事务？请给出批次/游标/幂等设计。",
        "answer": "日切生成批次号；分页拉单+游标记录进度；每批独立事务并记录幂等表；失败可重跑未完成批次；结算结果写账务表与对账表用于校验。",
        "difficulty": "MIDDLE",
        "type": "SCENARIO",
        "domain": "企业金融/支付",
    },
    {
        "id": "pay_03",
        "question": "设计企业支付的限额与风控：单笔、日累计、产品维度；在高并发下如何实现？",
        "answer": "维度=商户/账户/产品/币种；单笔校验+日累计 Redis 原子计数(TTL=当日)；穿透防护用预热+滑动窗口；离线回灌校准，超限拒绝并告警。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "企业金融/支付",
    },
    {
        "id": "pay_04",
        "question": "HZYX-HR 科技在支付通道路由时如何做灰度与回退？需要监控哪些指标？",
        "answer": "路由权重下发，按商户/地域分桶；监控成功率、P99、超时率、差错率；异常自动降权或切回；幂等防止重复扣款；指标驱动回滚。",
        "difficulty": "MIDDLE",
        "type": "SCENARIO",
        "domain": "企业金融/支付",
    },
    {
        "id": "pay_05",
        "question": "企业支付回调丢失时如何保证账务一致？在 HZYX-HR 科技的实践是什么？",
        "answer": "回调+主动补单双通道；定时对账比对渠道流水与内部账；差异生成工单；账务更新幂等；补单走相同幂等键确保一致；监控缺口比例。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "企业金融/支付",
    },
]


def ensure_collection():
    if utility.has_collection(COLLECTION_NAME):
        return Collection(COLLECTION_NAME)

    log(f"Creating collection {COLLECTION_NAME}")
    fields = [
        FieldSchema(
            name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=128
        ),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIM),
        FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535),
    ]
    schema = CollectionSchema(fields=fields, description="HZYX-HR interview question bank")
    coll = Collection(name=COLLECTION_NAME, schema=schema)
    coll.create_index(field_name="embedding", index_params={"index_type": "IVF_FLAT", "metric_type": "COSINE"})
    coll.load()
    return coll


def seed():
    host = os.getenv("MILVUS_HOST", "milvus")
    port = os.getenv("MILVUS_PORT", "19530")
    log(f"Connecting to Milvus {host}:{port}")
    connections.connect(alias="default", host=host, port=port)

    coll = ensure_collection()
    if coll.num_entities >= len(QUESTIONS):
        log("Collection already has data, skip seeding")
        return

    log("Seeding question bank ...")
    data = [[], [], [], []]  # id, content, embedding, metadata
    for q in QUESTIONS:
        content = q["question"]
        data[0].append(q["id"])
        data[1].append(content)
        data[2].append(deterministic_embedding(content))
        metadata = {
            "question": q["question"],
            "answer": q["answer"],
            "difficulty": q["difficulty"],
            "type": q["type"],
            "domain": q["domain"],
            "tags": ["HZYX-HR", "面试题"],
        }
        data[3].append(json.dumps(metadata, ensure_ascii=False))

    coll.insert(data)
    coll.flush()
    log(f"Inserted {len(QUESTIONS)} questions into {COLLECTION_NAME}")


if __name__ == "__main__":
    # 等待 Milvus 可用
    retries = 10
    for i in range(retries):
        try:
            seed()
            sys.exit(0)
        except Exception as e:
            log(f"Seed failed (try {i + 1}/{retries}): {e}")
            time.sleep(5)
    sys.exit(1)
