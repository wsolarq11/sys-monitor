#!/usr/bin/env python3
"""
操作日志系统

功能：
1. 记录所有自动化操作
2. 支持查询和过滤
3. 生成审计报告
4. 维护操作历史
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class OperationLogger:
    """
    操作日志管理器
    
    负责记录、查询和管理所有自动化操作的日志
    """
    
    def __init__(self, log_dir: str = ".lingma/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 日志文件路径
        self.operation_log_path = self.log_dir / "operations.json"
        self.audit_log_path = self.log_dir / "audit.log"
        self.error_log_path = self.log_dir / "errors.json"
        
        # 加载现有日志
        self.operations = self._load_operations()
        
    def _load_operations(self) -> List[Dict[str, Any]]:
        """加载操作日志"""
        if self.operation_log_path.exists():
            try:
                with open(self.operation_log_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_operations(self):
        """保存操作日志"""
        # 只保留最近 5000 条记录
        recent_ops = self.operations[-5000:]
        
        with open(self.operation_log_path, 'w', encoding='utf-8') as f:
            json.dump(recent_ops, f, indent=2, ensure_ascii=False)
    
    def log_operation(self, operation: Dict[str, Any], result: Dict[str, Any]):
        """
        记录操作
        
        Args:
            operation: 操作描述
            result: 执行结果
        """
        log_entry = {
            "id": self._generate_id(),
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "result": result,
            "duration_ms": result.get("duration_ms", 0),
            "session_id": self._get_session_id()
        }
        
        self.operations.append(log_entry)
        self._save_operations()
        
        # 同时写入审计日志（纯文本，便于查看）
        self._write_audit_log(log_entry)
        
        # 如果失败，记录到错误日志
        if result.get("status") == "failed":
            self._log_error(log_entry)
        
        return log_entry["id"]
    
    def _write_audit_log(self, entry: Dict[str, Any]):
        """写入审计日志（追加模式）"""
        timestamp = entry["timestamp"]
        op_type = entry["operation"].get("type", "unknown")
        status = entry["result"].get("status", "unknown")
        duration = entry.get("duration_ms", 0)
        
        audit_line = f"[{timestamp}] {op_type} - {status} ({duration}ms)\n"
        
        with open(self.audit_log_path, 'a', encoding='utf-8') as f:
            f.write(audit_line)
    
    def _log_error(self, entry: Dict[str, Any]):
        """记录错误"""
        error_entry = {
            "id": entry["id"],
            "timestamp": entry["timestamp"],
            "operation": entry["operation"],
            "error": entry["result"].get("error", "Unknown error"),
            "stack_trace": entry["result"].get("stack_trace")
        }
        
        # 加载现有错误日志
        errors = []
        if self.error_log_path.exists():
            try:
                with open(self.error_log_path, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
            except (json.JSONDecodeError, IOError):
                errors = []
        
        errors.append(error_entry)
        
        # 只保留最近 1000 个错误
        errors = errors[-1000:]
        
        with open(self.error_log_path, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)
    
    def _generate_id(self) -> str:
        """生成唯一 ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_session_id(self) -> str:
        """获取会话 ID"""
        # 简单实现：使用时间戳
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def query_operations(self, 
                        operation_type: Optional[str] = None,
                        status: Optional[str] = None,
                        start_time: Optional[str] = None,
                        end_time: Optional[str] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询操作日志
        
        Args:
            operation_type: 操作类型过滤
            status: 状态过滤 (success/failed/cancelled)
            start_time: 开始时间 (ISO format)
            end_time: 结束时间 (ISO format)
            limit: 返回数量限制
            
        Returns:
            匹配的操作列表
        """
        results = self.operations
        
        # 应用过滤器
        if operation_type:
            results = [
                op for op in results 
                if op["operation"].get("type") == operation_type
            ]
        
        if status:
            results = [
                op for op in results 
                if op["result"].get("status") == status
            ]
        
        if start_time:
            results = [
                op for op in results 
                if op["timestamp"] >= start_time
            ]
        
        if end_time:
            results = [
                op for op in results 
                if op["timestamp"] <= end_time
            ]
        
        # 按时间倒序排列
        results = sorted(results, key=lambda x: x["timestamp"], reverse=True)
        
        # 限制数量
        return results[:limit]
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            统计数据
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_time.isoformat()
        
        recent_ops = [
            op for op in self.operations 
            if op["timestamp"] >= cutoff_str
        ]
        
        if not recent_ops:
            return {
                "period_days": days,
                "total_operations": 0,
                "message": "No operations in the specified period"
            }
        
        # 计算统计
        total = len(recent_ops)
        successful = sum(1 for op in recent_ops if op["result"]["status"] == "success")
        failed = sum(1 for op in recent_ops if op["result"]["status"] == "failed")
        
        # 按类型统计
        type_stats = {}
        for op in recent_ops:
            op_type = op["operation"].get("type", "unknown")
            if op_type not in type_stats:
                type_stats[op_type] = {"total": 0, "success": 0, "failed": 0}
            
            type_stats[op_type]["total"] += 1
            if op["result"]["status"] == "success":
                type_stats[op_type]["success"] += 1
            elif op["result"]["status"] == "failed":
                type_stats[op_type]["failed"] += 1
        
        # 平均执行时间
        durations = [op.get("duration_ms", 0) for op in recent_ops]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "period_days": days,
            "total_operations": total,
            "successful_operations": successful,
            "failed_operations": failed,
            "success_rate": round(successful / total * 100, 2) if total > 0 else 0,
            "average_duration_ms": round(avg_duration, 2),
            "operations_by_type": type_stats,
            "error_rate": round(failed / total * 100, 2) if total > 0 else 0
        }
    
    def generate_report(self, days: int = 7) -> str:
        """
        生成可读的报告
        
        Args:
            days: 报告覆盖的天数
            
        Returns:
            格式化的报告字符串
        """
        stats = self.get_statistics(days)
        
        report_lines = [
            "=" * 60,
            f"操作日志报告 (最近 {days} 天)",
            "=" * 60,
            "",
            f"总操作数: {stats['total_operations']}",
            f"成功: {stats['successful_operations']}",
            f"失败: {stats['failed_operations']}",
            f"成功率: {stats['success_rate']}%",
            f"平均耗时: {stats['average_duration_ms']}ms",
            "",
            "-" * 60,
            "按类型统计:",
            "-" * 60,
        ]
        
        for op_type, type_stat in stats.get("operations_by_type", {}).items():
            report_lines.append(
                f"  {op_type}: {type_stat['total']} 次 "
                f"(成功: {type_stat['success']}, 失败: {type_stat['failed']})"
            )
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def clear_old_logs(self, days_to_keep: int = 30):
        """
        清理旧日志
        
        Args:
            days_to_keep: 保留的天数
        """
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_time.isoformat()
        
        original_count = len(self.operations)
        self.operations = [
            op for op in self.operations 
            if op["timestamp"] >= cutoff_str
        ]
        removed_count = original_count - len(self.operations)
        
        self._save_operations()
        
        return {
            "removed": removed_count,
            "remaining": len(self.operations)
        }
    
    def export_logs(self, output_path: str, format: str = "json"):
        """
        导出日志
        
        Args:
            output_path: 输出文件路径
            format: 导出格式 (json/csv)
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.operations, f, indent=2, ensure_ascii=False)
        elif format == "csv":
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if self.operations:
                    writer = csv.DictWriter(f, fieldnames=self.operations[0].keys())
                    writer.writeheader()
                    writer.writerows(self.operations)
        
        return str(output_file)


# 便捷函数
def log_operation(operation: Dict[str, Any], result: Dict[str, Any]) -> str:
    """快速记录操作"""
    logger = OperationLogger()
    return logger.log_operation(operation, result)


def get_recent_operations(limit: int = 10) -> List[Dict[str, Any]]:
    """获取最近的操作"""
    logger = OperationLogger()
    return logger.query_operations(limit=limit)


if __name__ == "__main__":
    # 测试示例
    logger = OperationLogger()
    
    # 模拟记录一些操作
    test_op = {
        "type": "create_file",
        "details": {"file": "test.txt"}
    }
    
    test_result = {
        "status": "success",
        "duration_ms": 150
    }
    
    log_id = logger.log_operation(test_op, test_result)
    print(f"操作已记录，ID: {log_id}")
    
    # 查询最近操作
    recent = logger.query_operations(limit=5)
    print(f"\n最近 {len(recent)} 条操作:")
    for op in recent:
        print(f"  - {op['operation']['type']} at {op['timestamp']}")
    
    # 显示统计
    print("\n" + logger.generate_report(days=7))
