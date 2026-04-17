#!/usr/bin/env python3
"""
AI Agent Knowledge Graph & Advanced RAG System - AI Agent 知识图谱与高级 RAG 系统

GraphRAG、语义搜索、向量数据库集成、混合检索
实现生产级 AI Agent 的知识增强框架

参考社区最佳实践:
- GraphRAG (Knowledge Graph + RAG)
- Hybrid retrieval (vector + keyword + graph)
- Semantic search with vector databases
- Entity extraction and relationship mapping
- Multi-hop reasoning over knowledge graphs
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import math
import statistics

logger = logging.getLogger(__name__)


class RetrievalStrategy(Enum):
    """检索策略"""
    VECTOR_ONLY = "vector_only"  # 纯向量检索
    KEYWORD_ONLY = "keyword_only"  # 纯关键词检索
    HYBRID = "hybrid"  # 混合检索
    GRAPH_RAG = "graph_rag"  # 图增强检索
    MULTI_HOP = "multi_hop"  # 多跳推理


class EntityType(Enum):
    """实体类型"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    CONCEPT = "concept"
    EVENT = "event"
    PRODUCT = "product"
    TECHNOLOGY = "technology"


class RelationshipType(Enum):
    """关系类型"""
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    CREATED_BY = "created_by"
    LOCATED_IN = "located_in"
    WORKS_FOR = "works_for"
    SIMILAR_TO = "similar_to"
    DEPENDS_ON = "depends_on"


@dataclass
class Entity:
    """知识图谱实体"""
    entity_id: str
    name: str
    entity_type: EntityType
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class Relationship:
    """知识图谱关系"""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    weight: float = 1.0  # 关系权重 (0-1)
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class DocumentChunk:
    """文档分块"""
    chunk_id: str
    content: str
    document_id: str
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    entities: List[str] = field(default_factory=list)  # 提取的实体ID列表
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class SearchResult:
    """搜索结果"""
    result_id: str
    content: str
    score: float
    source_type: str  # vector/keyword/graph
    metadata: Dict[str, Any] = field(default_factory=dict)
    entities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class RAGResponse:
    """RAG 响应"""
    response_id: str
    query: str
    answer: str
    retrieved_context: List[SearchResult] = field(default_factory=list)
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    reasoning_path: List[str] = field(default_factory=list)
    generated_at: str = ""
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()


class VectorDatabase:
    """向量数据库
    
    支持语义相似度搜索
    """
    
    def __init__(self):
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict] = {}
    
    def add_vector(self, item_id: str, vector: List[float], metadata: Dict = None):
        """添加向量"""
        self.vectors[item_id] = vector
        self.metadata[item_id] = metadata or {}
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """
        向量相似度搜索
        
        Args:
            query_vector: 查询向量
            top_k: 返回前K个结果
            threshold: 相似度阈值
            
        Returns:
            [(item_id, similarity_score), ...]
        """
        if not self.vectors:
            return []
        
        # 计算余弦相似度
        similarities = []
        
        for item_id, vector in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, vector)
            
            if similarity >= threshold:
                similarities.append((item_id, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            raise ValueError("Vector dimensions must match")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a ** 2 for a in vec1))
        magnitude2 = math.sqrt(sum(b ** 2 for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)


class KnowledgeGraph:
    """知识图谱
    
    存储实体和关系，支持图遍历
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.adjacency_list: Dict[str, List[str]] = {}  # entity_id -> [relationship_ids]
    
    def add_entity(self, entity: Entity):
        """添加实体"""
        self.entities[entity.entity_id] = entity
        if entity.entity_id not in self.adjacency_list:
            self.adjacency_list[entity.entity_id] = []
        
        logger.debug(f"Entity added: {entity.name} ({entity.entity_id})")
    
    def add_relationship(self, relationship: Relationship):
        """添加关系"""
        self.relationships[relationship.relationship_id] = relationship
        
        # 更新邻接表
        if relationship.source_entity_id not in self.adjacency_list:
            self.adjacency_list[relationship.source_entity_id] = []
        self.adjacency_list[relationship.source_entity_id].append(relationship.relationship_id)
        
        logger.debug(f"Relationship added: {relationship.source_entity_id} -> {relationship.target_entity_id}")
    
    def get_neighbors(self, entity_id: str, max_depth: int = 2) -> List[Dict]:
        """
        获取邻居节点（BFS遍历）
        
        Args:
            entity_id: 起始实体ID
            max_depth: 最大深度
            
        Returns:
            邻居节点列表
        """
        visited = set()
        queue = [(entity_id, 0)]  # (entity_id, depth)
        neighbors = []
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            
            # 获取当前实体的关系
            rel_ids = self.adjacency_list.get(current_id, [])
            
            for rel_id in rel_ids:
                rel = self.relationships.get(rel_id)
                
                if rel:
                    target_id = rel.target_entity_id
                    
                    if target_id not in visited:
                        target_entity = self.entities.get(target_id)
                        
                        if target_entity:
                            neighbors.append({
                                "entity": asdict(target_entity),
                                "relationship": asdict(rel),
                                "depth": depth + 1
                            })
                            
                            queue.append((target_id, depth + 1))
        
        return neighbors
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[Dict]]:
        """
        查找两个实体之间的路径
        
        Args:
            source_id: 源实体ID
            target_id: 目标实体ID
            max_depth: 最大深度
            
        Returns:
            路径列表或None
        """
        if source_id == target_id:
            return []
        
        visited = set()
        queue = [(source_id, [])]  # (entity_id, path)
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id in visited or len(path) > max_depth:
                continue
            
            visited.add(current_id)
            
            # 获取当前实体的关系
            rel_ids = self.adjacency_list.get(current_id, [])
            
            for rel_id in rel_ids:
                rel = self.relationships.get(rel_id)
                
                if rel:
                    target_rel_id = rel.target_entity_id
                    new_path = path + [{"entity": current_id, "relationship": asdict(rel)}]
                    
                    if target_rel_id == target_id:
                        return new_path
                    
                    if target_rel_id not in visited:
                        queue.append((target_rel_id, new_path))
        
        return None
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """按类型获取实体"""
        return [e for e in self.entities.values() if e.entity_type == entity_type]
    
    def search_entities(self, query: str) -> List[Entity]:
        """搜索实体（基于名称）"""
        query_lower = query.lower()
        return [
            e for e in self.entities.values()
            if query_lower in e.name.lower() or query_lower in e.description.lower()
        ]


class HybridRetriever:
    """混合检索器
    
    结合向量、关键词和图检索
    """
    
    def __init__(self, vector_db: VectorDatabase, knowledge_graph: KnowledgeGraph):
        self.vector_db = vector_db
        self.knowledge_graph = knowledge_graph
        self.document_chunks: Dict[str, DocumentChunk] = {}
    
    def add_document_chunk(self, chunk: DocumentChunk):
        """添加文档分块"""
        self.document_chunks[chunk.chunk_id] = chunk
        
        # 添加到向量数据库
        if chunk.embedding:
            self.vector_db.add_vector(chunk.chunk_id, chunk.embedding, {
                "content": chunk.content,
                "document_id": chunk.document_id,
                "entities": chunk.entities
            })
    
    def retrieve(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID,
        top_k: int = 5
    ) -> List[SearchResult]:
        """
        检索相关内容
        
        Args:
            query: 查询文本
            query_embedding: 查询向量（可选）
            strategy: 检索策略
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        results = []
        
        if strategy == RetrievalStrategy.VECTOR_ONLY and query_embedding:
            results = self._vector_search(query_embedding, top_k)
        
        elif strategy == RetrievalStrategy.KEYWORD_ONLY:
            results = self._keyword_search(query, top_k)
        
        elif strategy == RetrievalStrategy.HYBRID:
            vector_results = self._vector_search(query_embedding, top_k) if query_embedding else []
            keyword_results = self._keyword_search(query, top_k)
            
            # 合并并去重
            results = self._merge_results(vector_results, keyword_results, top_k)
        
        elif strategy == RetrievalStrategy.GRAPH_RAG:
            results = self._graph_rag_search(query, top_k)
        
        elif strategy == RetrievalStrategy.MULTI_HOP:
            results = self._multi_hop_search(query, query_embedding, top_k)
        
        return results
    
    def _vector_search(self, query_embedding: List[float], top_k: int) -> List[SearchResult]:
        """向量搜索"""
        matches = self.vector_db.search(query_embedding, top_k=top_k)
        
        results = []
        for chunk_id, score in matches:
            chunk = self.document_chunks.get(chunk_id)
            
            if chunk:
                result = SearchResult(
                    result_id=str(uuid.uuid4()),
                    content=chunk.content,
                    score=score,
                    source_type="vector",
                    metadata=chunk.metadata,
                    entities=chunk.entities
                )
                results.append(result)
        
        return results
    
    def _keyword_search(self, query: str, top_k: int) -> List[SearchResult]:
        """关键词搜索"""
        query_words = set(query.lower().split())
        
        scored_chunks = []
        
        for chunk in self.document_chunks.values():
            chunk_words = set(chunk.content.lower().split())
            
            # 计算词重叠度
            overlap = len(query_words.intersection(chunk_words))
            score = overlap / len(query_words) if query_words else 0
            
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # 按分数排序
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for chunk, score in scored_chunks[:top_k]:
            result = SearchResult(
                result_id=str(uuid.uuid4()),
                content=chunk.content,
                score=score,
                source_type="keyword",
                metadata=chunk.metadata,
                entities=chunk.entities
            )
            results.append(result)
        
        return results
    
    def _graph_rag_search(self, query: str, top_k: int) -> List[SearchResult]:
        """图增强检索"""
        # 1. 搜索相关实体
        related_entities = self.knowledge_graph.search_entities(query)
        
        if not related_entities:
            return []
        
        # 2. 获取实体的邻居
        all_neighbors = []
        
        for entity in related_entities[:3]:  # 取前3个最相关的实体
            neighbors = self.knowledge_graph.get_neighbors(entity.entity_id, max_depth=2)
            all_neighbors.extend(neighbors)
        
        # 3. 找到包含这些实体的文档分块
        entity_ids = [e.entity_id for e in related_entities]
        neighbor_entity_ids = [n["entity"]["entity_id"] for n in all_neighbors]
        all_entity_ids = set(entity_ids + neighbor_entity_ids)
        
        results = []
        
        for chunk in self.document_chunks.values():
            # 检查分块是否包含相关实体
            matching_entities = set(chunk.entities).intersection(all_entity_ids)
            
            if matching_entities:
                score = len(matching_entities) / len(all_entity_ids)
                
                result = SearchResult(
                    result_id=str(uuid.uuid4()),
                    content=chunk.content,
                    score=score,
                    source_type="graph",
                    metadata={
                        **chunk.metadata,
                        "matched_entities": list(matching_entities),
                        "neighbors": all_neighbors[:5]
                    },
                    entities=chunk.entities
                )
                results.append(result)
        
        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:top_k]
    
    def _multi_hop_search(
        self,
        query: str,
        query_embedding: Optional[List[float]],
        top_k: int
    ) -> List[SearchResult]:
        """多跳推理检索"""
        # 第一跳：向量检索
        first_hop = self._vector_search(query_embedding, top_k * 2) if query_embedding else []
        
        # 从第一跳结果中提取实体
        first_hop_entities = set()
        for result in first_hop:
            first_hop_entities.update(result.entities)
        
        # 第二跳：基于实体的图检索
        second_hop_results = []
        
        for entity_id in list(first_hop_entities)[:5]:  # 取前5个实体
            neighbors = self.knowledge_graph.get_neighbors(entity_id, max_depth=1)
            
            for neighbor in neighbors:
                neighbor_entity_id = neighbor["entity"]["entity_id"]
                
                # 找到包含邻居实体的分块
                for chunk in self.document_chunks.values():
                    if neighbor_entity_id in chunk.entities:
                        result = SearchResult(
                            result_id=str(uuid.uuid4()),
                            content=chunk.content,
                            score=0.6,  # 第二跳分数较低
                            source_type="multi_hop",
                            metadata={
                                **chunk.metadata,
                                "hop": 2,
                                "via_entity": entity_id
                            },
                            entities=chunk.entities
                        )
                        second_hop_results.append(result)
        
        # 合并两跳结果
        all_results = first_hop + second_hop_results
        
        # 去重并排序
        seen_content = set()
        unique_results = []
        
        for result in all_results:
            if result.content not in seen_content:
                seen_content.add(result.content)
                unique_results.append(result)
        
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        return unique_results[:top_k]
    
    def _merge_results(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """合并向量和关键词结果"""
        # 使用倒数排名融合 (Reciprocal Rank Fusion)
        all_results = {}
        
        for rank, result in enumerate(vector_results, 1):
            if result.content not in all_results:
                all_results[result.content] = {
                    "result": result,
                    "rrf_score": 0.0
                }
            all_results[result.content]["rrf_score"] += 1.0 / (rank + 60)  # RRF公式
        
        for rank, result in enumerate(keyword_results, 1):
            if result.content not in all_results:
                all_results[result.content] = {
                    "result": result,
                    "rrf_score": 0.0
                }
            all_results[result.content]["rrf_score"] += 1.0 / (rank + 60)
        
        # 按RRF分数排序
        merged = sorted(all_results.values(), key=lambda x: x["rrf_score"], reverse=True)
        
        return [item["result"] for item in merged[:top_k]]


class RAGEngine:
    """RAG 引擎
    
    整合检索和生成的完整系统
    """
    
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.knowledge_graph = KnowledgeGraph()
        self.retriever = HybridRetriever(self.vector_db, self.knowledge_graph)
        self.response_history: List[RAGResponse] = []
    
    def ingest_document(
        self,
        document_id: str,
        content: str,
        chunk_size: int = 500,
        entities: Optional[List[Entity]] = None,
        relationships: Optional[List[Relationship]] = None
    ) -> Dict:
        """
        摄入文档
        
        Args:
            document_id: 文档ID
            content: 文档内容
            chunk_size: 分块大小
            entities: 提取的实体列表
            relationships: 提取的关系列表
            
        Returns:
            摄入统计
        """
        # 分块
        chunks = self._chunk_text(content, chunk_size)
        
        # 添加分块
        for i, chunk_content in enumerate(chunks):
            chunk = DocumentChunk(
                chunk_id=f"{document_id}_chunk_{i}",
                content=chunk_content,
                document_id=document_id,
                chunk_index=i,
                metadata={"document_id": document_id},
                embedding=self._generate_mock_embedding(chunk_content)  # 模拟嵌入
            )
            
            self.retriever.add_document_chunk(chunk)
        
        # 添加实体到知识图谱
        if entities:
            for entity in entities:
                self.knowledge_graph.add_entity(entity)
        
        # 添加关系到知识图谱
        if relationships:
            for relationship in relationships:
                self.knowledge_graph.add_relationship(relationship)
        
        stats = {
            "document_id": document_id,
            "chunks_created": len(chunks),
            "entities_added": len(entities) if entities else 0,
            "relationships_added": len(relationships) if relationships else 0
        }
        
        logger.info(f"Document ingested: {stats}")
        
        return stats
    
    def query(
        self,
        question: str,
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID,
        top_k: int = 5
    ) -> RAGResponse:
        """
        查询
        
        Args:
            question: 问题
            strategy: 检索策略
            top_k: 检索结果数量
            
        Returns:
            RAG响应
        """
        logger.info(f"Query: {question}")
        
        # 生成查询向量（模拟）
        query_embedding = self._generate_mock_embedding(question)
        
        # 检索
        results = self.retriever.retrieve(
            query=question,
            query_embedding=query_embedding,
            strategy=strategy,
            top_k=top_k
        )
        
        # 生成答案（模拟）
        answer = self._generate_answer(question, results)
        
        # 计算置信度
        confidence = statistics.mean([r.score for r in results]) if results else 0.0
        
        # 创建响应
        response = RAGResponse(
            response_id=str(uuid.uuid4()),
            query=question,
            answer=answer,
            retrieved_context=results,
            confidence=round(confidence, 4),
            sources=[r.metadata.get("document_id", "unknown") for r in results],
            reasoning_path=[f"Retrieved {len(results)} chunks using {strategy.value}"]
        )
        
        self.response_history.append(response)
        
        logger.info(f"Response generated: confidence={confidence:.2f}")
        
        return response
    
    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """文本分块"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """生成模拟嵌入向量"""
        # 在实际应用中，这里应该调用嵌入模型
        # 目前使用简单的哈希作为模拟
        import hashlib
        
        hash_value = hashlib.md5(text.encode()).hexdigest()
        
        # 转换为384维向量（模拟）
        embedding = [ord(c) / 255.0 for c in hash_value[:32]]
        embedding.extend([0.0] * (384 - len(embedding)))
        
        return embedding
    
    def _generate_answer(self, question: str, results: List[SearchResult]) -> str:
        """生成答案（模拟）"""
        if not results:
            return "I don't have enough information to answer this question."
        
        # 简单拼接检索到的内容
        context_snippets = [r.content[:200] for r in results[:3]]
        
        answer = f"Based on the retrieved information:\n\n"
        answer += "\n\n".join(context_snippets)
        answer += f"\n\n[Confidence: {statistics.mean([r.score for r in results]):.2f}]"
        
        return answer
    
    def get_knowledge_graph_stats(self) -> Dict:
        """获取知识图谱统计"""
        entity_types = {}
        for entity in self.knowledge_graph.entities.values():
            etype = entity.entity_type.value
            if etype not in entity_types:
                entity_types[etype] = 0
            entity_types[etype] += 1
        
        return {
            "total_entities": len(self.knowledge_graph.entities),
            "total_relationships": len(self.knowledge_graph.relationships),
            "entity_types": entity_types
        }


def create_rag_engine() -> RAGEngine:
    """工厂函数：创建 RAG 引擎"""
    return RAGEngine()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Knowledge Graph & Advanced RAG 测试")
    print("="*60)
    
    engine = create_rag_engine()
    
    # 创建实体
    print("\n🔗 创建知识图谱...")
    entities = [
        Entity(entity_id="ent_1", name="Python", entity_type=EntityType.TECHNOLOGY, description="Programming language"),
        Entity(entity_id="ent_2", name="Machine Learning", entity_type=EntityType.CONCEPT, description="AI subfield"),
        Entity(entity_id="ent_3", name="TensorFlow", entity_type=EntityType.PRODUCT, description="ML framework"),
        Entity(entity_id="ent_4", name="Google", entity_type=EntityType.ORGANIZATION, description="Tech company"),
    ]
    
    relationships = [
        Relationship(relationship_id="rel_1", source_entity_id="ent_3", target_entity_id="ent_1", relationship_type=RelationshipType.DEPENDS_ON),
        Relationship(relationship_id="rel_2", source_entity_id="ent_3", target_entity_id="ent_4", relationship_type=RelationshipType.CREATED_BY),
        Relationship(relationship_id="rel_3", source_entity_id="ent_2", target_entity_id="ent_1", relationship_type=RelationshipType.RELATED_TO),
    ]
    
    print(f"   创建了 {len(entities)} 个实体")
    print(f"   创建了 {len(relationships)} 个关系")
    
    # 摄入文档
    print("\n📄 摄入文档...")
    doc_content = """
    Python is a versatile programming language widely used in machine learning and data science.
    TensorFlow is an open-source machine learning framework developed by Google.
    It provides comprehensive tools for building and deploying ML models.
    Machine learning is a subset of artificial intelligence that enables systems to learn from data.
    Python's simplicity and extensive libraries make it ideal for ML development.
    """
    
    stats = engine.ingest_document(
        document_id="doc_ml_intro",
        content=doc_content,
        chunk_size=50,
        entities=entities,
        relationships=relationships
    )
    
    print(f"   文档ID: {stats['document_id']}")
    print(f"   分块数: {stats['chunks_created']}")
    print(f"   实体数: {stats['entities_added']}")
    print(f"   关系数: {stats['relationships_added']}")
    
    # 查询
    print("\n❓ 执行查询...")
    questions = [
        ("What is TensorFlow?", RetrievalStrategy.HYBRID),
        ("Who created TensorFlow?", RetrievalStrategy.GRAPH_RAG),
        ("Explain machine learning", RetrievalStrategy.VECTOR_ONLY),
    ]
    
    for question, strategy in questions:
        print(f"\n   Q: {question}")
        print(f"   Strategy: {strategy.value}")
        
        response = engine.query(question, strategy=strategy, top_k=3)
        
        print(f"   A: {response.answer[:150]}...")
        print(f"   Confidence: {response.confidence:.2f}")
        print(f"   Sources: {len(response.sources)}")
    
    # 知识图谱统计
    print("\n📊 知识图谱统计:")
    kg_stats = engine.get_knowledge_graph_stats()
    print(f"   总实体数: {kg_stats['total_entities']}")
    print(f"   总关系数: {kg_stats['total_relationships']}")
    print(f"   实体类型分布:")
    for etype, count in kg_stats['entity_types'].items():
        print(f"     - {etype}: {count}")
    
    print("\n✅ 测试完成！")
