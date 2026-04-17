#!/usr/bin/env python3
"""
Long-term Memory System - 长期记忆系统

基于向量数据库的语义记忆存储和检索
支持 ChromaDB/Pinecone/FAISS 等多种后端

参考社区最佳实践:
- ChromaDB for local persistent memory
- Pinecone for cloud-scale memory
- Hybrid approach (vector + metadata filtering)
- Memory consolidation and forgetting mechanisms
"""

import json
import time
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """记忆类型"""
    SEMANTIC = "semantic"  # 语义记忆（知识、事实）
    EPISODIC = "episodic"  # 情景记忆（事件、经历）
    PROCEDURAL = "procedural"  # 程序记忆（技能、方法）
    USER_PREFERENCE = "user_preference"  # 用户偏好


class MemoryBackend(Enum):
    """记忆后端"""
    CHROMADB = "chromadb"
    PINECONE = "pinecone"
    FAISS = "faiss"
    IN_MEMORY = "in_memory"  # 内存模式（测试用）


@dataclass
class MemoryItem:
    """记忆项"""
    memory_id: str
    content: str  # 记忆内容
    memory_type: MemoryType
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance_score: float = 0.5  # 重要性分数 (0-1)
    access_count: int = 0  # 访问次数
    last_accessed: Optional[str] = None
    created_at: str = ""
    updated_at: Optional[str] = None
    expires_at: Optional[str] = None  # 过期时间
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        """从字典创建"""
        data['memory_type'] = MemoryType(data['memory_type'])
        return cls(**data)


@dataclass
class MemoryQuery:
    """记忆查询"""
    query_text: str
    memory_types: List[MemoryType] = field(default_factory=list)
    user_id: Optional[str] = None
    min_importance: float = 0.0
    max_results: int = 5
    time_range: Optional[Tuple[str, str]] = None  # (start, end)
    metadata_filter: Optional[Dict[str, Any]] = None


class EmbeddingModel:
    """嵌入模型
    
    将文本转换为向量表示
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Args:
            model_name: 嵌入模型名称
        """
        self.model_name = model_name
        self._model = None
        self._dimension = 384  # all-MiniLM-L6-v2 的维度
    
    def encode(self, text: str) -> List[float]:
        """
        编码文本为向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        # Mock 实现（Phase 4），真实实现需要加载嵌入模型
        return self._mock_encode(text)
    
    def _mock_encode(self, text: str) -> List[float]:
        """Mock 编码（用于测试）"""
        # 简单的哈希-based 伪向量
        import hashlib
        hash_obj = hashlib.md5(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # 转换为浮点数向量
        vector = [b / 255.0 for b in hash_bytes]
        # 扩展到目标维度
        while len(vector) < self._dimension:
            vector.extend(vector[:min(16, self._dimension - len(vector))])
        
        return vector[:self._dimension]
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self._dimension


class VectorDatabase:
    """向量数据库抽象层
    
    支持多种后端：ChromaDB, Pinecone, FAISS, In-Memory
    """
    
    def __init__(self, backend: MemoryBackend = MemoryBackend.IN_MEMORY, config: Dict = None):
        """
        Args:
            backend: 数据库后端
            config: 配置参数
        """
        self.backend = backend
        self.config = config or {}
        self._client = None
        self._collection = None
        self._embedding_model = EmbeddingModel()
        
        # 初始化
        self._initialize()
    
    def _initialize(self):
        """初始化数据库连接"""
        if self.backend == MemoryBackend.IN_MEMORY:
            self._init_in_memory()
        elif self.backend == MemoryBackend.CHROMADB:
            self._init_chromadb()
        elif self.backend == MemoryBackend.PINECONE:
            self._init_pinecone()
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
    
    def _init_in_memory(self):
        """初始化内存数据库"""
        self._memories: Dict[str, MemoryItem] = {}
        self._index: Dict[str, List[float]] = {}  # id -> embedding
    
    def _init_chromadb(self):
        """初始化 ChromaDB"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            persist_dir = self.config.get("persist_directory", "./chroma_db")
            Path(persist_dir).mkdir(parents=True, exist_ok=True)
            
            self._client = chromadb.PersistentClient(path=persist_dir)
            collection_name = self.config.get("collection_name", "agent_memory")
            
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Agent long-term memory"}
            )
            
            logger.info(f"ChromaDB initialized: {persist_dir}")
        
        except ImportError:
            logger.warning("ChromaDB not installed, falling back to in-memory")
            self.backend = MemoryBackend.IN_MEMORY
            self._init_in_memory()
    
    def _init_pinecone(self):
        """初始化 Pinecone"""
        try:
            import pinecone
            
            api_key = self.config.get("api_key")
            environment = self.config.get("environment", "gcp-starter")
            index_name = self.config.get("index_name", "agent-memory")
            
            pinecone.init(api_key=api_key, environment=environment)
            
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=self._embedding_model.get_dimension(),
                    metric="cosine"
                )
            
            self._client = pinecone.Index(index_name)
            logger.info(f"Pinecone initialized: {index_name}")
        
        except ImportError:
            logger.warning("Pinecone not installed, falling back to in-memory")
            self.backend = MemoryBackend.IN_MEMORY
            self._init_in_memory()
    
    def add_memory(self, memory: MemoryItem) -> bool:
        """
        添加记忆
        
        Args:
            memory: 记忆项
            
        Returns:
            是否成功
        """
        # 生成嵌入
        if not memory.embedding:
            memory.embedding = self._embedding_model.encode(memory.content)
        
        if self.backend == MemoryBackend.IN_MEMORY:
            return self._add_in_memory(memory)
        elif self.backend == MemoryBackend.CHROMADB:
            return self._add_chromadb(memory)
        elif self.backend == MemoryBackend.PINECONE:
            return self._add_pinecone(memory)
        
        return False
    
    def _add_in_memory(self, memory: MemoryItem) -> bool:
        """内存数据库添加"""
        self._memories[memory.memory_id] = memory
        self._index[memory.memory_id] = memory.embedding
        return True
    
    def _add_chromadb(self, memory: MemoryItem) -> bool:
        """ChromaDB 添加"""
        try:
            metadata = {
                "memory_type": memory.memory_type.value,
                "user_id": memory.user_id or "",
                "importance": memory.importance_score,
                **memory.metadata
            }
            
            self._collection.add(
                embeddings=[memory.embedding],
                documents=[memory.content],
                metadatas=[metadata],
                ids=[memory.memory_id]
            )
            return True
        except Exception as e:
            logger.error(f"ChromaDB add failed: {e}")
            return False
    
    def _add_pinecone(self, memory: MemoryItem) -> bool:
        """Pinecone 添加"""
        try:
            metadata = {
                "memory_type": memory.memory_type.value,
                "user_id": memory.user_id or "",
                "importance": memory.importance_score,
                "content": memory.content,
                **memory.metadata
            }
            
            self._client.upsert(
                vectors=[(memory.memory_id, memory.embedding, metadata)]
            )
            return True
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {e}")
            return False
    
    def search(self, query: MemoryQuery) -> List[MemoryItem]:
        """
        搜索记忆
        
        Args:
            query: 查询条件
            
        Returns:
            匹配的记忆列表
        """
        # 生成查询向量
        query_embedding = self._embedding_model.encode(query.query_text)
        
        if self.backend == MemoryBackend.IN_MEMORY:
            return self._search_in_memory(query, query_embedding)
        elif self.backend == MemoryBackend.CHROMADB:
            return self._search_chromadb(query, query_embedding)
        elif self.backend == MemoryBackend.PINECONE:
            return self._search_pinecone(query, query_embedding)
        
        return []
    
    def _search_in_memory(self, query: MemoryQuery, query_embedding: List[float]) -> List[MemoryItem]:
        """内存数据库搜索"""
        import math
        
        results = []
        for mem_id, memory in self._memories.items():
            # 过滤条件
            if query.memory_types and memory.memory_type not in query.memory_types:
                continue
            if query.user_id and memory.user_id != query.user_id:
                continue
            if memory.importance_score < query.min_importance:
                continue
            
            # 计算余弦相似度
            similarity = self._cosine_similarity(query_embedding, memory.embedding)
            
            results.append((similarity, memory))
        
        # 按相似度排序
        results.sort(key=lambda x: x[0], reverse=True)
        
        # 返回前 N 个
        return [mem for _, mem in results[:query.max_results]]
    
    def _search_chromadb(self, query: MemoryQuery, query_embedding: List[float]) -> List[MemoryItem]:
        """ChromaDB 搜索"""
        try:
            where_clause = {}
            if query.user_id:
                where_clause["user_id"] = query.user_id
            if query.memory_types:
                where_clause["memory_type"] = {"$in": [t.value for t in query.memory_types]}
            
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=query.max_results,
                where=where_clause if where_clause else None
            )
            
            memories = []
            for i, doc_id in enumerate(results['ids'][0]):
                memory = MemoryItem(
                    memory_id=doc_id,
                    content=results['documents'][0][i],
                    memory_type=MemoryType.SEMANTIC,  # TODO: 从 metadata 恢复
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {}
                )
                memories.append(memory)
            
            return memories
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []
    
    def _search_pinecone(self, query: MemoryQuery, query_embedding: List[float]) -> List[MemoryItem]:
        """Pinecone 搜索"""
        try:
            filter_clause = {}
            if query.user_id:
                filter_clause["user_id"] = query.user_id
            if query.memory_types:
                filter_clause["memory_type"] = {"$in": [t.value for t in query.memory_types]}
            
            results = self._client.query(
                vector=query_embedding,
                top_k=query.max_results,
                filter=filter_clause if filter_clause else None,
                include_metadata=True
            )
            
            memories = []
            for match in results['matches']:
                metadata = match.get('metadata', {})
                memory = MemoryItem(
                    memory_id=match['id'],
                    content=metadata.get('content', ''),
                    memory_type=MemoryType(metadata.get('memory_type', 'semantic')),
                    metadata=metadata
                )
                memories.append(memory)
            
            return memories
        except Exception as e:
            logger.error(f"Pinecone query failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def update_memory(self, memory_id: str, updates: Dict) -> bool:
        """更新记忆"""
        if self.backend == MemoryBackend.IN_MEMORY:
            if memory_id in self._memories:
                memory = self._memories[memory_id]
                for key, value in updates.items():
                    if hasattr(memory, key):
                        setattr(memory, key, value)
                memory.updated_at = datetime.now(timezone.utc).isoformat()
                return True
        return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        if self.backend == MemoryBackend.IN_MEMORY:
            if memory_id in self._memories:
                del self._memories[memory_id]
                del self._index[memory_id]
                return True
        return False
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if self.backend == MemoryBackend.IN_MEMORY:
            return {
                "total_memories": len(self._memories),
                "backend": self.backend.value
            }
        return {"backend": self.backend.value}


class MemoryConsolidator:
    """记忆巩固器
    
    定期整理和优化记忆库
    """
    
    def __init__(self, db: VectorDatabase):
        self.db = db
        self.consolidation_rules = self._load_rules()
    
    def _load_rules(self) -> Dict:
        """加载巩固规则"""
        return {
            "forgetting_curve": {
                "half_life_days": 30,  # 半衰期
                "min_importance": 0.1   # 最低重要性
            },
            "merging_threshold": 0.9,  # 相似度阈值（合并相似记忆）
            "max_memories_per_user": 1000  # 每用户最大记忆数
        }
    
    def consolidate(self, user_id: Optional[str] = None) -> Dict:
        """
        执行记忆巩固
        
        Args:
            user_id: 用户ID（可选，针对特定用户）
            
        Returns:
            巩固结果
        """
        stats = {
            "forgotten": 0,
            "merged": 0,
            "updated": 0
        }
        
        # Step 1: 应用遗忘曲线
        forgotten = self._apply_forgetting_curve(user_id)
        stats["forgotten"] = forgotten
        
        # Step 2: 合并相似记忆
        merged = self._merge_similar_memories(user_id)
        stats["merged"] = merged
        
        # Step 3: 更新重要性分数
        updated = self._update_importance_scores(user_id)
        stats["updated"] = updated
        
        logger.info(f"Memory consolidation completed: {stats}")
        return stats
    
    def _apply_forgetting_curve(self, user_id: Optional[str]) -> int:
        """应用遗忘曲线"""
        # TODO: 实现基于时间的遗忘机制
        return 0
    
    def _merge_similar_memories(self, user_id: Optional[str]) -> int:
        """合并相似记忆"""
        # TODO: 实现基于相似度的合并
        return 0
    
    def _update_importance_scores(self, user_id: Optional[str]) -> int:
        """更新重要性分数"""
        # TODO: 基于访问频率更新时间重要性
        return 0


class LongTermMemory:
    """长期记忆系统
    
    整合向量数据库、嵌入模型、记忆巩固的完整系统
    """
    
    def __init__(
        self,
        backend: MemoryBackend = MemoryBackend.IN_MEMORY,
        config: Dict = None
    ):
        """
        Args:
            backend: 数据库后端
            config: 配置参数
        """
        self.db = VectorDatabase(backend, config or {})
        self.consolidator = MemoryConsolidator(self.db)
        self.embedding_model = EmbeddingModel()
    
    def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        user_id: Optional[str] = None,
        metadata: Dict = None
    ) -> str:
        """
        存储记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            user_id: 用户ID
            metadata: 元数据
            
        Returns:
            记忆ID
        """
        import uuid
        memory_id = str(uuid.uuid4())
        
        memory = MemoryItem(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            user_id=user_id,
            metadata=metadata or {},
            importance_score=metadata.get("importance", 0.5) if metadata else 0.5
        )
        
        success = self.db.add_memory(memory)
        
        if success:
            logger.info(f"Memory stored: {memory_id}")
            return memory_id
        else:
            raise RuntimeError(f"Failed to store memory: {memory_id}")
    
    def retrieve_memories(self, query: MemoryQuery) -> List[MemoryItem]:
        """
        检索记忆
        
        Args:
            query: 查询条件
            
        Returns:
            匹配的记忆列表
        """
        memories = self.db.search(query)
        
        # 更新访问统计
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed = datetime.now(timezone.utc).isoformat()
            self.db.update_memory(memory.memory_id, {
                "access_count": memory.access_count,
                "last_accessed": memory.last_accessed
            })
        
        logger.info(f"Retrieved {len(memories)} memories")
        return memories
    
    def forget_memory(self, memory_id: str) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否成功
        """
        success = self.db.delete_memory(memory_id)
        if success:
            logger.info(f"Memory forgotten: {memory_id}")
        return success
    
    def consolidate_memories(self, user_id: Optional[str] = None) -> Dict:
        """
        巩固记忆
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            巩固结果
        """
        return self.consolidator.consolidate(user_id)
    
    def get_stats(self) -> Dict:
        """获取记忆系统统计"""
        db_stats = self.db.get_stats()
        return {
            **db_stats,
            "embedding_dimension": self.embedding_model.get_dimension()
        }


def create_long_term_memory(config: Optional[Dict] = None) -> LongTermMemory:
    """工厂函数：创建长期记忆系统"""
    if config:
        backend = MemoryBackend(config.get("backend", "in_memory"))
        return LongTermMemory(backend, config)
    return LongTermMemory()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("Long-term Memory System 测试")
    print("="*60)
    
    # 创建记忆系统
    memory_system = create_long_term_memory({
        "backend": "in_memory"
    })
    
    # 存储记忆
    print("\n💾 存储记忆...")
    mem1 = memory_system.store_memory(
        content="用户喜欢 Python 编程",
        memory_type=MemoryType.USER_PREFERENCE,
        user_id="user-001",
        metadata={"importance": 0.8}
    )
    print(f"   记忆ID: {mem1}")
    
    mem2 = memory_system.store_memory(
        content="项目使用 FastAPI 框架",
        memory_type=MemoryType.SEMANTIC,
        user_id="user-001",
        metadata={"importance": 0.7}
    )
    print(f"   记忆ID: {mem2}")
    
    mem3 = memory_system.store_memory(
        content="昨天完成了用户认证模块",
        memory_type=MemoryType.EPISODIC,
        user_id="user-001",
        metadata={"importance": 0.6, "task_id": "task-auth"}
    )
    print(f"   记忆ID: {mem3}")
    
    # 检索记忆
    print("\n🔍 检索记忆...")
    query = MemoryQuery(
        query_text="Python 编程",
        memory_types=[MemoryType.USER_PREFERENCE],
        user_id="user-001",
        max_results=3
    )
    
    results = memory_system.retrieve_memories(query)
    print(f"   找到 {len(results)} 条相关记忆:")
    for i, mem in enumerate(results, 1):
        print(f"   {i}. [{mem.memory_type.value}] {mem.content[:50]}...")
        print(f"      重要性: {mem.importance_score}, 访问次数: {mem.access_count}")
    
    # 获取统计
    print("\n📊 系统统计:")
    stats = memory_system.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 巩固记忆
    print("\n🔄 巩固记忆...")
    consolidation_result = memory_system.consolidate_memories("user-001")
    print(json.dumps(consolidation_result, indent=2, ensure_ascii=False))
    
    print("\n✅ 测试完成！")
