#!/usr/bin/env python3
"""
MCP 配置验证脚本

检查 MCP 服务器配置是否正确
"""

import json
import subprocess
from pathlib import Path


def check_nodejs():
    """检查 Node.js 是否安装"""
    try:
        result = subprocess.run(
            ["node", "-v"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"✅ Node.js: {version}")
        
        # 检查版本是否 >= 18
        major_version = int(version.lstrip('v').split('.')[0])
        if major_version < 18:
            print(f"⚠️  Node.js 版本过低 (需要 v18+)")
            return False
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js 未安装或版本过低 (需要 v18+)")
        print("   下载地址: https://nodejs.org/")
        return False


def check_npm():
    """检查 npm 是否安装"""
    try:
        result = subprocess.run(
            ["npm", "-v"],
            capture_output=True,
            text=True,
            check=True,
            shell=True  # Windows 需要 shell=True
        )
        version = result.stdout.strip()
        print(f"✅ npm: {version}")
        
        # 检查版本是否 >= 8
        major_version = int(version.split('.')[0])
        if major_version < 8:
            print(f"⚠️  npm 版本过低 (需要 v8+)")
            return False
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm 未安装")
        return False


def check_mcp_config():
    """检查 MCP 配置文件"""
    config_file = Path(".lingma/config/mcp-servers.json")
    
    if not config_file.exists():
        print("❌ MCP 配置文件不存在")
        print(f"   期望路径: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        
        if not servers:
            print("⚠️  MCP 配置文件存在，但未配置任何服务器")
            return False
        
        print(f"✅ MCP 配置文件存在")
        print(f"   配置了 {len(servers)} 个服务器:")
        
        for name, server_config in servers.items():
            disabled = server_config.get("disabled", False)
            command = server_config.get("command", "unknown")
            status = "⚠️  禁用" if disabled else "✅ 启用"
            description = server_config.get("description", "")
            
            print(f"\n   📦 {name}:")
            print(f"      状态: {status}")
            print(f"      命令: {command}")
            if description:
                print(f"      说明: {description}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ MCP 配置文件格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取 MCP 配置文件失败: {e}")
        return False


def check_mcp_packages():
    """检查 MCP 包是否已安装（可选）"""
    config_file = Path(".lingma/config/mcp-servers.json")
    
    if not config_file.exists():
        return True  # 配置文件不存在，跳过此检查
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        servers = config.get("mcpServers", {})
        print(f"\n🔍 检查 MCP 包安装状态:")
        
        for name, server_config in servers.items():
            if server_config.get("disabled", False):
                print(f"   ⏭️  {name}: 已禁用，跳过检查")
                continue
            
            args = server_config.get("args", [])
            if len(args) >= 2 and args[0] == "-y":
                package_name = args[1]
                
                # 尝试运行 npx 检查包
                try:
                    result = subprocess.run(
                        ["npx", "--yes", package_name, "--help"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    # 如果返回 0 或包含帮助信息，说明包可用
                    if result.returncode == 0 or "usage" in result.stdout.lower() or "help" in result.stdout.lower():
                        print(f"   ✅ {name} ({package_name}): 可用")
                    else:
                        print(f"   ⚠️  {name} ({package_name}): 可能需要首次运行时下载")
                except subprocess.TimeoutExpired:
                    print(f"   ⚠️  {name} ({package_name}): 检查超时（可能需首次下载）")
                except Exception as e:
                    print(f"   ⚠️  {name} ({package_name}): 首次使用时会自动下载")
        
        return True
    except Exception as e:
        print(f"   ⚠️  无法检查 MCP 包状态: {e}")
        return True  # 不阻止流程


def verify_setup():
    """验证 MCP 设置"""
    print("=" * 70)
    print("  MCP 配置验证")
    print("=" * 70)
    print()
    
    checks = [
        ("Node.js", check_nodejs),
        ("npm", check_npm),
        ("MCP 配置", check_mcp_config),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'─' * 70}")
        print(f"检查 {name}:")
        print(f"{'─' * 70}")
        result = check_func()
        results.append(result)
    
    # 可选检查
    print(f"\n{'─' * 70}")
    print("检查 MCP 包 (可选):")
    print(f"{'─' * 70}")
    check_mcp_packages()
    
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"核心检查: {passed}/{total} 通过")
    
    if passed == total:
        print("\n✅ MCP 配置正确！")
        print("\n下一步:")
        print("  1. 在 IDE 中重启通义灵码插件")
        print("  2. 测试 MCP 工具调用:")
        print("     - 使用 filesystem MCP 列出文件")
        print("     - 使用 git MCP 查看 commits")
        print("  3. 根据需要启用/禁用 MCP 服务")
        print("\n💡 提示:")
        print("  - Shell MCP 默认禁用（高风险）")
        print("  - 如需启用，编辑 .lingma/config/mcp-servers.json")
        print("  - 将 shell 的 disabled 改为 false")
        return True
    else:
        print(f"\n❌ {total - passed} 个核心检查失败")
        print("\n建议:")
        
        if not results[0]:  # Node.js
            print("  1. 安装 Node.js v18+")
            print("     Windows: 从 https://nodejs.org/ 下载安装")
            print("     Mac: brew install node")
        
        if not results[1]:  # npm
            print("  2. 确保 npm 已安装（通常随 Node.js 一起安装）")
        
        if not results[2]:  # MCP 配置
            print("  3. 检查 MCP 配置文件格式")
            print("     参考: .lingma/specs/phase2-mcp-plan.md")
        
        print("\n  4. 查看 MCP_USAGE_GUIDE.md 获取详细帮助")
        return False


if __name__ == "__main__":
    import sys
    success = verify_setup()
    sys.exit(0 if success else 1)
