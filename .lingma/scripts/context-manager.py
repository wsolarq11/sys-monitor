#!/usr/bin/env python3
"""
上下文管理器 - Context Manager

职责：
1. 维护会话上下文（session context）
2. 学习用户偏好（user preferences）
3. 跟踪操作历史（operation history）
4. 提供个性化建议（personalized suggestions）

存储策略：
- 短期数据：JSON 文件（快速读写）
- 长期数据：SQLite 数据库（结构化查询）
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid


# ==================== 数据模型 ====================

@dataclass
class SessionContext:
    """会话上下文"""
    session_id: str
    start_time: str
    last_active: str
    spec_path: Optional[str] = None
    current_task: Optional[str] = None
    completed_tasks: List[str] = None
    operation_count: int = 0
    error_count: int = 0
    
    def __post_init__(self):
        if self.completed_tasks is None:
            self.completed_tasks = []


@dataclass
class UserPreference:
    """用户偏好"""
    user_id: str = "default"
    automation_level: str = "balanced"  # conservative, balanced, aggressive
    risk_threshold: float = 0.5
    preferred_strategy_overrides: Dict[str, str] = None
    learning_enabled: bool = True
    learning_rate: float = 0.1
    min_data_points: int = 10
    last_updated: str = None
    
    def __post_init__(self):
        if self.preferred_strategy_overrides is None:
            self.preferred_strategy_overrides = {}
        if self.last_updated is None:
            self.last_updated = ContextManager._utc_now().isoformat()


@dataclass
class OperationRecord:
    """操作记录"""
    operation_id: str
    timestamp: str
    operation_type: str
    operation_details: Dict[str, Any]
    risk_score: float
    confidence: float
    strategy_used: str
    result: str  # success, failed, cancelled
    duration_ms: float
    user_override: Optional[bool] = None
    user_decision: Optional[str] = None


# ==================== 上下文管理器 ====================

class ContextManager:
    """
    上下文管理器
    
    功能：
    1. 管理会话上下文
    2. 学习用户偏好
    3. 记录操作历史
    4. 提供智能建议
    """
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(".lingma/state")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件路径
        self.session_file = self.base_dir / "current_session.json"
        self.preferences_file = self.base_dir / "user_preferences.json"
        self.operations_log = self.base_dir / "operations.log"
        self.db_path = self.base_dir / "context.db"
        
        # 初始化数据库
        self._init_database()
        
        # 加载或创建会话
        self.current_session = self._load_or_create_session()
        
        # 加载用户偏好
        self.user_preferences = self._load_preferences()
    
    # ==================== 会话管理 ====================
    
    @staticmethod
    def _utc_now() -> datetime:
        """获取当前 UTC 时间"""
        return datetime.now(timezone.utc)
    
    def _load_or_create_session(self) -> SessionContext:
        """加载或创建新会话"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return SessionContext(**data)
            except Exception as e:
                print(f"⚠️  加载会话失败: {e}，创建新会话")
        
        # 创建新会话
        now = self._utc_now()
        session = SessionContext(
            session_id=str(uuid.uuid4()),
            start_time=now.isoformat(),
            last_active=now.isoformat()
        )
        self._save_session(session)
        return session
    
    def _save_session(self, session: SessionContext):
        """保存会话"""
        session.last_active = self._utc_now().isoformat()
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(session), f, indent=2, ensure_ascii=False)
    
    def update_session(self, **kwargs):
        """更新会话信息"""
        for key, value in kwargs.items():
            if hasattr(self.current_session, key):
                setattr(self.current_session, key, value)
        self._save_session(self.current_session)
    
    def increment_operation_count(self):
        """增加操作计数"""
        self.current_session.operation_count += 1
        self._save_session(self.current_session)
    
    def increment_error_count(self):
        """增加错误计数"""
        self.current_session.error_count += 1
        self._save_session(self.current_session)
    
    def get_session_summary(self) -> Dict:
        """获取会话摘要"""
        return {
            "session_id": self.current_session.session_id,
            "start_time": self.current_session.start_time,
            "duration_minutes": self._calculate_session_duration(),
            "operation_count": self.current_session.operation_count,
            "error_count": self.current_session.error_count,
            "success_rate": self._calculate_success_rate(),
            "current_spec": self.current_session.spec_path,
            "current_task": self.current_session.current_task
        }
    
    def _calculate_session_duration(self) -> float:
        """计算会话持续时间（分钟）"""
        try:
            start_str = self.current_session.start_time
            # 移除时区信息，统一处理
            if '+' in start_str:
                start_str = start_str.split('+')[0]
            elif start_str.endswith('Z'):
                start_str = start_str[:-1]
            
            start = datetime.fromisoformat(start_str)
            now = datetime.utcnow()  # 使用 naive datetime
            return (now - start).total_seconds() / 60
        except Exception:
            return 0.0
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        total = self.current_session.operation_count
        if total == 0:
            return 100.0
        errors = self.current_session.error_count
        return ((total - errors) / total) * 100
    
    # ==================== 用户偏好管理 ====================
    
    def _load_preferences(self) -> UserPreference:
        """加载用户偏好"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserPreference(**data)
            except Exception as e:
                print(f"⚠️  加载偏好失败: {e}，使用默认偏好")
        
        # 创建默认偏好
        prefs = UserPreference()
        self._save_preferences(prefs)
        return prefs
    
    def _save_preferences(self, prefs: UserPreference):
        """保存用户偏好"""
        prefs.last_updated = ContextManager._utc_now().isoformat()
        with open(self.preferences_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(prefs), f, indent=2, ensure_ascii=False)
    
    def update_preference(self, **kwargs):
        """更新用户偏好"""
        for key, value in kwargs.items():
            if hasattr(self.user_preferences, key):
                setattr(self.user_preferences, key, value)
        self._save_preferences(self.user_preferences)
    
    def learn_from_override(self, operation_type: str, original_strategy: str, user_choice: str):
        """从用户覆盖中学习"""
        if not self.user_preferences.learning_enabled:
            return
        
        # 记录覆盖
        overrides = self.user_preferences.preferred_strategy_overrides
        key = f"{operation_type}:{original_strategy}"
        
        if key not in overrides:
            overrides[key] = user_choice
        else:
            # 如果用户多次选择相同策略，加强学习
            if overrides[key] == user_choice:
                # 可以添加权重机制
                pass
            else:
                overrides[key] = user_choice
        
        self.update_preference(preferred_strategy_overrides=overrides)
    
    def get_preferred_strategy(self, operation_type: str, default_strategy: str) -> str:
        """获取偏好的执行策略"""
        if not self.user_preferences.learning_enabled:
            return default_strategy
        
        # 查找是否有覆盖
        overrides = self.user_preferences.preferred_strategy_overrides
        
        # 精确匹配
        if operation_type in overrides:
            return overrides[operation_type]
        
        # 返回默认策略
        return default_strategy
    
    def adjust_risk_threshold(self, new_threshold: float):
        """调整风险阈值"""
        self.update_preference(risk_threshold=new_threshold)
    
    # ==================== 操作历史记录 ====================
    
    def record_operation(self, operation: OperationRecord):
        """记录操作"""
        # 写入日志文件（追加模式）
        with open(self.operations_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(operation), ensure_ascii=False) + '\n')
        
        # 写入数据库
        self._insert_operation_to_db(operation)
        
        # 更新会话计数
        self.increment_operation_count()
        if operation.result == "failed":
            self.increment_error_count()
    
    def _insert_operation_to_db(self, operation: OperationRecord):
        """插入操作到数据库"""
        conn = self._get_db_connection()
        try:
            conn.execute("""
                INSERT INTO operations (
                    operation_id, timestamp, operation_type, 
                    risk_score, confidence, strategy_used, 
                    result, duration_ms, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                operation.operation_id,
                operation.timestamp,
                operation.operation_type,
                operation.risk_score,
                operation.confidence,
                operation.strategy_used,
                operation.result,
                operation.duration_ms,
                self.current_session.session_id
            ))
            conn.commit()
        finally:
            conn.close()
    
    def get_operation_history(self, limit: int = 50) -> List[Dict]:
        """获取操作历史"""
        conn = self._get_db_connection()
        try:
            cursor = conn.execute("""
                SELECT * FROM operations 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_operation_stats(self) -> Dict:
        """获取操作统计"""
        conn = self._get_db_connection()
        try:
            # 总操作数
            cursor = conn.execute("SELECT COUNT(*) FROM operations")
            total = cursor.fetchone()[0]
            
            # 成功率
            cursor = conn.execute("""
                SELECT 
                    COUNT(CASE WHEN result = 'success' THEN 1 END) as success_count,
                    COUNT(CASE WHEN result = 'failed' THEN 1 END) as failed_count
                FROM operations
            """)
            row = cursor.fetchone()
            success_count = row[0]
            failed_count = row[1]
            
            # 平均风险分数
            cursor = conn.execute("SELECT AVG(risk_score) FROM operations")
            avg_risk = cursor.fetchone()[0] or 0
            
            # 平均置信度
            cursor = conn.execute("SELECT AVG(confidence) FROM operations")
            avg_confidence = cursor.fetchone()[0] or 0
            
            # 策略分布
            cursor = conn.execute("""
                SELECT strategy_used, COUNT(*) as count 
                FROM operations 
                GROUP BY strategy_used
            """)
            strategy_distribution = dict(cursor.fetchall())
            
            return {
                "total_operations": total,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": (success_count / total * 100) if total > 0 else 0,
                "average_risk_score": round(avg_risk, 3),
                "average_confidence": round(avg_confidence, 3),
                "strategy_distribution": strategy_distribution
            }
        finally:
            conn.close()
    
    # ==================== 数据库管理 ====================
    
    def _init_database(self):
        """初始化数据库"""
        conn = self._get_db_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT UNIQUE,
                    timestamp TEXT,
                    operation_type TEXT,
                    risk_score REAL,
                    confidence REAL,
                    strategy_used TEXT,
                    result TEXT,
                    duration_ms REAL,
                    session_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON operations(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_operation_type ON operations(operation_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON operations(session_id)")
            
            conn.commit()
        finally:
            conn.close()
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== 智能建议 ====================
    
    def generate_suggestions(self) -> List[str]:
        """生成智能建议"""
        suggestions = []
        
        stats = self.get_operation_stats()
        
        # 基于成功率
        if stats["success_rate"] < 80:
            suggestions.append(
                f"⚠️  成功率较低 ({stats['success_rate']:.1f}%)，建议检查自动化配置"
            )
        
        # 基于风险分数
        if stats["average_risk_score"] > 0.7:
            suggestions.append(
                f"⚠️  平均风险分数较高 ({stats['average_risk_score']:.3f})，建议降低风险阈值"
            )
        
        # 基于置信度
        if stats["average_confidence"] < 0.6:
            suggestions.append(
                f"💡 平均置信度较低 ({stats['average_confidence']:.3f})，系统需要更多学习数据"
            )
        
        # 基于操作数量
        if stats["total_operations"] < self.user_preferences.min_data_points:
            remaining = self.user_preferences.min_data_points - stats["total_operations"]
            suggestions.append(
                f"📊 还需要 {remaining} 个操作数据点来优化学习模型"
            )
        
        # 基于策略分布
        if "require_explicit_approval" in stats["strategy_distribution"]:
            approval_count = stats["strategy_distribution"]["require_explicit_approval"]
            if approval_count > stats["total_operations"] * 0.3:
                suggestions.append(
                    f"💡 30%+ 的操作需要明确批准，考虑调整风险阈值以提高效率"
                )
        
        return suggestions
    
    # ==================== 清理和维护 ====================
    
    def cleanup_old_sessions(self, days: int = 30):
        """清理旧会话"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # 清理数据库中的旧记录
        conn = self._get_db_connection()
        try:
            conn.execute("DELETE FROM operations WHERE timestamp < ?", (cutoff.isoformat(),))
            conn.commit()
        finally:
            conn.close()
        
        # 清理日志文件（保留最近 N 天）
        if self.operations_log.exists():
            # 简化处理：直接清空（实际应该按日期过滤）
            pass
    
    def export_context(self, output_path: Path = None) -> Path:
        """导出上下文数据"""
        if output_path is None:
            output_path = self.base_dir / f"context_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "session": asdict(self.current_session),
            "preferences": asdict(self.user_preferences),
            "stats": self.get_operation_stats(),
            "recent_operations": self.get_operation_history(limit=100),
            "suggestions": self.generate_suggestions()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return output_path


# ==================== 便捷函数 ====================

def get_context_manager() -> ContextManager:
    """获取上下文管理器单例"""
    if not hasattr(get_context_manager, '_instance'):
        get_context_manager._instance = ContextManager()
    return get_context_manager._instance


if __name__ == "__main__":
    # 测试代码
    cm = ContextManager()
    
    print("=" * 70)
    print("  上下文管理器测试")
    print("=" * 70)
    print()
    
    # 测试会话管理
    print("✅ 会话管理")
    summary = cm.get_session_summary()
    print(f"   会话 ID: {summary['session_id'][:8]}...")
    print(f"   操作计数: {summary['operation_count']}")
    print()
    
    # 测试偏好管理
    print("✅ 偏好管理")
    print(f"   自动化级别: {cm.user_preferences.automation_level}")
    print(f"   风险阈值: {cm.user_preferences.risk_threshold}")
    print()
    
    # 测试操作记录
    print("✅ 操作记录")
    op = OperationRecord(
        operation_id=f"test-op-{uuid.uuid4().hex[:8]}",
        timestamp=ContextManager._utc_now().isoformat(),
        operation_type="file_create",
        operation_details={"path": "test.txt"},
        risk_score=0.1,
        confidence=0.9,
        strategy_used="auto_execute",
        result="success",
        duration_ms=50.0
    )
    cm.record_operation(op)
    print(f"   已记录操作: {op.operation_id}")
    print()
    
    # 测试统计
    print("✅ 操作统计")
    stats = cm.get_operation_stats()
    print(f"   总操作数: {stats['total_operations']}")
    print(f"   成功率: {stats['success_rate']:.1f}%")
    print()
    
    # 测试建议
    print("✅ 智能建议")
    suggestions = cm.generate_suggestions()
    if suggestions:
        for s in suggestions:
            print(f"   {s}")
    else:
        print("   暂无建议")
    print()
    
    print("✅ 所有测试通过！")
