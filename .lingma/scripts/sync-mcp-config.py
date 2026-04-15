#!/usr/bin/env python3
"""
MCP 配置同步脚本

将项目级 MCP 配置同步到 Lingma 全局配置
"""

import json
import shutil
from pathlib import Path


def sync_mcp_config():
    """同步 MCP 配置"""
    
    # 项目配置文件
    project_config = Path(".lingma/config/mcp-servers.json")
    
    # 全局配置文件路径
    global_config = Path.home() / "AppData" / "Roaming" / "Lingma" / "SharedClientCache" / "mcp.json"
    
    print("=" * 70)
    print("  MCP 配置同步工具")
    print("=" * 70)
    print()
    
    # 检查项目配置是否存在
    if not project_config.exists():
        print(f"❌ 项目配置文件不存在: {project_config}")
        print("   请先创建 .lingma/config/mcp-servers.json")
        return False
    
    # 读取项目配置
    try:
        with open(project_config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        print(f"✅ 读取项目配置成功")
        print(f"   文件: {project_config}")
        
        servers = config_data.get("mcpServers", {})
        print(f"   配置了 {len(servers)} 个 MCP 服务器:")
        
        for name, server_config in servers.items():
            disabled = server_config.get("disabled", False)
            status = "⚠️  禁用" if disabled else "✅ 启用"
            print(f"   - {name}: {status}")
        
    except json.JSONDecodeError as e:
        print(f"❌ 项目配置文件格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取项目配置失败: {e}")
        return False
    
    print()
    
    # 确认同步
    print(f"目标位置: {global_config}")
    print()
    
    # 备份现有全局配置
    if global_config.exists():
        backup_path = global_config.with_suffix('.json.bak')
        try:
            shutil.copy2(global_config, backup_path)
            print(f"✅ 已备份全局配置到: {backup_path}")
        except Exception as e:
            print(f"⚠️  备份失败: {e}")
    
    # 同步配置
    try:
        shutil.copy2(project_config, global_config)
        print(f"✅ 配置同步成功！")
        print()
        print("下一步:")
        print("  1. 重启 IDE（或重新加载窗口）")
        print("  2. MCP 配置立即生效")
        print("  3. 在智能体模式中测试 MCP 调用")
        return True
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        print()
        print("可能的原因:")
        print("  1. 全局配置目录不存在")
        print("  2. 权限不足")
        print("  3. 文件被占用")
        return False


if __name__ == "__main__":
    import sys
    success = sync_mcp_config()
    sys.exit(0 if success else 1)
