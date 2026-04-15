#!/usr/bin/env python3
"""
MCP 配置同步和管理工具

功能:
- 同步项目配置到 Lingma 全局配置
- 管理配置模板
- 备份和恢复配置
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime


# 全局配置路径
GLOBAL_CONFIG = Path.home() / "AppData" / "Roaming" / "Lingma" / "SharedClientCache" / "mcp.json"
PROJECT_CONFIG = Path(".lingma/config/mcp-servers.json")
TEMPLATES_DIR = Path(".lingma/mcp-templates/")


def print_usage():
    """打印使用说明"""
    print("""
MCP 配置管理工具

用法:
  python sync-mcp-config.py                     # 同步项目配置到全局
  python sync-mcp-config.py list-templates      # 列出可用模板
  python sync-mcp-config.py apply-template <名称> # 应用模板
  python sync-mcp-config.py backup              # 备份当前配置
  python sync-mcp-config.py restore <备份名>     # 恢复备份

示例:
  python sync-mcp-config.py apply-template basic
  python sync-mcp-config.py backup
""")


def list_templates():
    """列出可用的配置模板"""
    print("=" * 70)
    print("  MCP 配置模板列表")
    print("=" * 70)
    print()
    
    if not TEMPLATES_DIR.exists():
        print(f"❌ 模板目录不存在: {TEMPLATES_DIR}")
        return []
    
    templates = list(TEMPLATES_DIR.glob("*.json"))
    
    if not templates:
        print("⚠️  没有找到模板文件")
        return []
    
    print(f"📋 可用的配置模板 ({len(templates)} 个):\n")
    
    for tpl in templates:
        try:
            with open(tpl, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            servers = config.get("mcpServers", {})
            server_names = ", ".join(servers.keys()) if servers else "无"
            
            print(f"✅ {tpl.stem}")
            print(f"   文件: {tpl}")
            print(f"   MCP 服务: {server_names}")
            print()
        except Exception as e:
            print(f"❌ {tpl.stem} - 读取失败: {e}")
            print()
    
    return templates


def apply_template(template_name):
    """应用配置模板"""
    template_path = TEMPLATES_DIR / f"{template_name}.json"
    
    print("=" * 70)
    print(f"  应用 MCP 配置模板: {template_name}")
    print("=" * 70)
    print()
    
    if not template_path.exists():
        print(f"❌ 模板不存在: {template_path}")
        print(f"   可用模板: ", end="")
        if TEMPLATES_DIR.exists():
            templates = [p.stem for p in TEMPLATES_DIR.glob("*.json")]
            print(", ".join(templates) if templates else "无")
        else:
            print("无")
        return False
    
    # 备份当前配置
    print("步骤 1/3: 备份当前配置...")
    if not backup_current_config():
        print("⚠️  备份失败，但继续执行")
    
    # 应用模板
    print(f"步骤 2/3: 应用模板 {template_name}...")
    try:
        shutil.copy2(template_path, GLOBAL_CONFIG)
        print(f"✅ 已应用模板: {template_name}")
    except Exception as e:
        print(f"❌ 应用模板失败: {e}")
        return False
    
    # 验证
    print("步骤 3/3: 验证配置...")
    try:
        with open(GLOBAL_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        print(f"✅ 配置验证成功")
        print(f"   激活的 MCP 服务: {', '.join(servers.keys()) if servers else '无'}")
    except Exception as e:
        print(f"⚠️  配置验证失败: {e}")
    
    print()
    print("下一步:")
    print("  1. 重启 IDE（或重新加载窗口）")
    print("  2. MCP 配置立即生效")
    print("  3. 在智能体模式中测试 MCP 调用")
    
    return True


def backup_current_config():
    """备份当前全局配置"""
    if not GLOBAL_CONFIG.exists():
        print("⚠️  全局配置文件不存在，跳过备份")
        return True
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(".lingma/backups/mcp/")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_path = backup_dir / f"mcp-{timestamp}.json"
        shutil.copy2(GLOBAL_CONFIG, backup_path)
        
        print(f"✅ 已备份全局配置到: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False


def restore_backup(backup_name):
    """恢复备份配置"""
    backup_dir = Path(".lingma/backups/mcp/")
    
    # 支持完整路径或仅文件名
    if Path(backup_name).is_absolute():
        backup_path = Path(backup_name)
    else:
        # 尝试在备份目录中查找
        if not backup_name.endswith('.json'):
            backup_name += '.json'
        backup_path = backup_dir / backup_name
    
    print("=" * 70)
    print(f"  恢复 MCP 配置备份: {backup_name}")
    print("=" * 70)
    print()
    
    if not backup_path.exists():
        print(f"❌ 备份文件不存在: {backup_path}")
        
        # 列出可用备份
        if backup_dir.exists():
            backups = list(backup_dir.glob("*.json"))
            if backups:
                print(f"\n可用的备份:")
                for b in backups:
                    print(f"  - {b.name}")
        
        return False
    
    # 备份当前配置
    print("步骤 1/2: 备份当前配置...")
    if not backup_current_config():
        print("⚠️  备份失败，但继续执行")
    
    # 恢复备份
    print(f"步骤 2/2: 恢复备份 {backup_name}...")
    try:
        shutil.copy2(backup_path, GLOBAL_CONFIG)
        print(f"✅ 已恢复备份: {backup_name}")
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False
    
    print()
    print("下一步:")
    print("  1. 重启 IDE（或重新加载窗口）")
    print("  2. 配置已恢复到备份时的状态")
    
    return True


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
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list-templates":
            list_templates()
        elif command == "apply-template" and len(sys.argv) > 2:
            template_name = sys.argv[2]
            apply_template(template_name)
        elif command == "backup":
            backup_current_config()
        elif command == "restore" and len(sys.argv) > 2:
            backup_name = sys.argv[2]
            restore_backup(backup_name)
        else:
            print("❌ 未知命令或参数不足")
            print_usage()
            sys.exit(1)
    else:
        # 默认行为：同步配置
        success = sync_mcp_config()
        sys.exit(0 if success else 1)
