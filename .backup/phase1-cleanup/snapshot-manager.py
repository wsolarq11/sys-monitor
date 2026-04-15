#!/usr/bin/env python3
"""
快照和回滚系统

功能：
1. 创建文件系统快照
2. 保存 Git 状态
3. 执行回滚操作
4. 管理快照历史
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class SnapshotManager:
    """
    快照管理器
    
    负责创建和管理系统快照，支持回滚操作
    """
    
    def __init__(self, snapshot_dir: str = ".lingma/snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # 快照索引文件
        self.index_path = self.snapshot_dir / "index.json"
        self.snapshots = self._load_index()
        
    def _load_index(self) -> List[Dict[str, Any]]:
        """加载快照索引"""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_index(self):
        """保存快照索引"""
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.snapshots, f, indent=2, ensure_ascii=False)
    
    def create_snapshot(self, 
                       name: Optional[str] = None,
                       description: str = "",
                       include_git: bool = True,
                       paths_to_snapshot: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        创建快照
        
        Args:
            name: 快照名称（可选，自动生成）
            description: 快照描述
            include_git: 是否包含 Git 状态
            paths_to_snapshot: 要快照的路径列表
            
        Returns:
            快照信息
        """
        timestamp = datetime.now()
        snapshot_id = timestamp.strftime("%Y%m%d_%H%M%S")
        snapshot_name = name or f"snapshot_{snapshot_id}"
        
        snapshot_dir = self.snapshot_dir / snapshot_name
        snapshot_dir.mkdir(exist_ok=True)
        
        snapshot_info = {
            "id": snapshot_name,
            "timestamp": timestamp.isoformat(),
            "description": description,
            "paths": [],
            "git_state": None,
            "size_bytes": 0
        }
        
        try:
            # 1. 保存 Git 状态
            if include_git:
                git_state = self._capture_git_state()
                snapshot_info["git_state"] = git_state
                
                # 保存 Git diff
                diff_file = snapshot_dir / "git_diff.txt"
                with open(diff_file, 'w', encoding='utf-8') as f:
                    f.write(git_state.get("diff", ""))
            
            # 2. 快照指定路径
            if paths_to_snapshot:
                for path_str in paths_to_snapshot:
                    path = Path(path_str)
                    if path.exists():
                        dest = snapshot_dir / path.name
                        if path.is_file():
                            shutil.copy2(path, dest)
                        elif path.is_dir():
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(path, dest)
                        
                        snapshot_info["paths"].append(path_str)
            
            # 3. 计算快照大小
            snapshot_info["size_bytes"] = self._calculate_dir_size(snapshot_dir)
            
            # 4. 更新索引
            self.snapshots.append(snapshot_info)
            self._save_index()
            
            return {
                "success": True,
                "snapshot_id": snapshot_name,
                "info": snapshot_info,
                "message": f"Snapshot created: {snapshot_name}"
            }
            
        except Exception as e:
            # 清理失败的快照
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)
            
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create snapshot: {str(e)}"
            }
    
    def _capture_git_state(self) -> Dict[str, Any]:
        """捕获 Git 状态"""
        try:
            # 获取当前分支
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=".",
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # 获取当前 commit
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=".",
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # 获取未提交的更改
            diff = subprocess.check_output(
                ["git", "diff", "HEAD"],
                cwd=".",
                stderr=subprocess.DEVNULL
            ).decode()
            
            # 获取暂存区状态
            status = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=".",
                stderr=subprocess.DEVNULL
            ).decode()
            
            return {
                "branch": branch,
                "commit": commit,
                "has_uncommitted_changes": len(diff) > 0 or len(status) > 0,
                "diff": diff,
                "status": status
            }
            
        except subprocess.CalledProcessError:
            return {
                "branch": "unknown",
                "commit": "unknown",
                "has_uncommitted_changes": False,
                "diff": "",
                "status": "",
                "error": "Git command failed"
            }
    
    def _calculate_dir_size(self, path: Path) -> int:
        """计算目录大小（字节）"""
        total_size = 0
        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size
    
    def list_snapshots(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        列出快照
        
        Args:
            limit: 返回数量限制
            
        Returns:
            快照列表（按时间倒序）
        """
        sorted_snapshots = sorted(
            self.snapshots, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        return sorted_snapshots[:limit]
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """获取特定快照信息"""
        for snapshot in self.snapshots:
            if snapshot["id"] == snapshot_id:
                return snapshot
        return None
    
    def rollback_to_snapshot(self, 
                            snapshot_id: str,
                            rollback_git: bool = True,
                            dry_run: bool = False) -> Dict[str, Any]:
        """
        回滚到指定快照
        
        Args:
            snapshot_id: 快照 ID
            rollback_git: 是否回滚 Git 状态
            dry_run: 仅预览，不实际执行
            
        Returns:
            回滚结果
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            return {
                "success": False,
                "error": f"Snapshot not found: {snapshot_id}",
                "message": "快照不存在"
            }
        
        result = {
            "snapshot_id": snapshot_id,
            "actions": [],
            "success": True,
            "dry_run": dry_run
        }
        
        try:
            snapshot_dir = self.snapshot_dir / snapshot_id
            
            # 1. 回滚 Git 状态
            if rollback_git and snapshot.get("git_state"):
                git_action = self._rollback_git_state(snapshot["git_state"], dry_run)
                result["actions"].append(git_action)
            
            # 2. 恢复文件
            if snapshot.get("paths"):
                for path_str in snapshot["paths"]:
                    path = Path(path_str)
                    snapshot_file = snapshot_dir / path.name
                    
                    if snapshot_file.exists():
                        restore_action = self._restore_file(snapshot_file, path, dry_run)
                        result["actions"].append(restore_action)
            
            if dry_run:
                result["message"] = f"Dry run: Would rollback to {snapshot_id}"
            else:
                result["message"] = f"Successfully rolled back to {snapshot_id}"
            
            return result
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            result["message"] = f"Rollback failed: {str(e)}"
            return result
    
    def _rollback_git_state(self, git_state: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """回滚 Git 状态"""
        action = {
            "type": "git_rollback",
            "details": {},
            "success": True
        }
        
        if dry_run:
            action["details"]["preview"] = "Would reset to commit: " + git_state.get("commit", "unknown")
            return action
        
        try:
            # 如果有未提交的更改，先 stash
            if git_state.get("has_uncommitted_changes"):
                subprocess.run(
                    ["git", "stash", "push", "-m", "Auto-stash before rollback"],
                    cwd=".",
                    check=True,
                    capture_output=True
                )
                action["details"]["stashed"] = True
            
            # 重置到快照时的 commit
            commit = git_state.get("commit")
            if commit and commit != "unknown":
                subprocess.run(
                    ["git", "reset", "--hard", commit],
                    cwd=".",
                    check=True,
                    capture_output=True
                )
                action["details"]["reset_to"] = commit
            
            action["details"]["message"] = "Git state rolled back successfully"
            
        except subprocess.CalledProcessError as e:
            action["success"] = False
            action["details"]["error"] = str(e)
        
        return action
    
    def _restore_file(self, source: Path, destination: Path, dry_run: bool) -> Dict[str, Any]:
        """恢复文件"""
        action = {
            "type": "file_restore",
            "source": str(source),
            "destination": str(destination),
            "success": True
        }
        
        if dry_run:
            action["preview"] = f"Would restore {source} to {destination}"
            return action
        
        try:
            # 确保目标目录存在
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            if source.is_file():
                shutil.copy2(source, destination)
            elif source.is_dir():
                if destination.exists():
                    shutil.rmtree(destination)
                shutil.copytree(source, destination)
            
            action["message"] = f"Restored {source} to {destination}"
            
        except Exception as e:
            action["success"] = False
            action["error"] = str(e)
        
        return action
    
    def delete_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """删除快照"""
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            return {
                "success": False,
                "error": f"Snapshot not found: {snapshot_id}"
            }
        
        try:
            snapshot_dir = self.snapshot_dir / snapshot_id
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)
            
            # 从索引中移除
            self.snapshots = [s for s in self.snapshots if s["id"] != snapshot_id]
            self._save_index()
            
            return {
                "success": True,
                "message": f"Snapshot deleted: {snapshot_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup_old_snapshots(self, days_to_keep: int = 7, max_count: int = 20) -> Dict[str, Any]:
        """
        清理旧快照
        
        Args:
            days_to_keep: 保留的天数
            max_count: 最大保留数量
            
        Returns:
            清理结果
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_time.isoformat()
        
        # 找出需要删除的快照
        to_delete = []
        for snapshot in self.snapshots:
            if snapshot["timestamp"] < cutoff_str:
                to_delete.append(snapshot["id"])
        
        # 如果超过最大数量，删除最旧的
        if len(self.snapshots) > max_count:
            sorted_snapshots = sorted(
                self.snapshots, 
                key=lambda x: x["timestamp"]
            )
            excess_count = len(self.snapshots) - max_count
            for snapshot in sorted_snapshots[:excess_count]:
                if snapshot["id"] not in to_delete:
                    to_delete.append(snapshot["id"])
        
        # 执行删除
        deleted_count = 0
        freed_space = 0
        
        for snapshot_id in to_delete:
            snapshot = self.get_snapshot(snapshot_id)
            if snapshot:
                freed_space += snapshot.get("size_bytes", 0)
                result = self.delete_snapshot(snapshot_id)
                if result["success"]:
                    deleted_count += 1
        
        return {
            "deleted_count": deleted_count,
            "freed_space_bytes": freed_space,
            "remaining_count": len(self.snapshots)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取快照统计信息"""
        if not self.snapshots:
            return {
                "total_snapshots": 0,
                "total_size_bytes": 0,
                "oldest_snapshot": None,
                "newest_snapshot": None
            }
        
        total_size = sum(s.get("size_bytes", 0) for s in self.snapshots)
        timestamps = [s["timestamp"] for s in self.snapshots]
        
        return {
            "total_snapshots": len(self.snapshots),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_snapshot": min(timestamps),
            "newest_snapshot": max(timestamps)
        }


# 便捷函数
def create_quick_snapshot(description: str = "") -> Dict[str, Any]:
    """快速创建快照"""
    manager = SnapshotManager()
    return manager.create_snapshot(description=description)


def rollback_to_latest() -> Dict[str, Any]:
    """回滚到最新快照"""
    manager = SnapshotManager()
    snapshots = manager.list_snapshots(limit=1)
    
    if not snapshots:
        return {
            "success": False,
            "error": "No snapshots available"
        }
    
    return manager.rollback_to_snapshot(snapshots[0]["id"])


if __name__ == "__main__":
    # 测试示例
    manager = SnapshotManager()
    
    # 创建快照
    print("Creating snapshot...")
    result = manager.create_snapshot(
        description="Test snapshot before automation",
        include_git=True
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 列出快照
    print("\nSnapshots:")
    snapshots = manager.list_snapshots()
    for snap in snapshots:
        print(f"  - {snap['id']}: {snap['description']}")
    
    # 显示统计
    print("\nStatistics:")
    stats = manager.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
