#!/usr/bin/env python3
"""调试 Supervisor Agent 编排错误"""

import json
import sys
import io
from pathlib import Path

# 设置stdout为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent / ".lingma" / "scripts"))

import importlib.util
spec = importlib.util.spec_from_file_location("supervisor_agent", ".lingma/scripts/supervisor-agent.py")
supervisor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor_module)
SupervisorAgent = supervisor_module.SupervisorAgent

# 加载输入数据
with open(".lingma/logs/orchestration-input.json", "r", encoding="utf-8") as f:
    input_data = json.load(f)

# 创建 Supervisor
supervisor = SupervisorAgent()

# 执行编排
try:
    result = supervisor.orchestrate_tasks(
        tasks=input_data["params"]["tasks"],
        pattern=input_data["params"]["pattern"],
        quality_gates_enabled=input_data["params"]["quality_gates_enabled"]
    )
    
    print("OK - Orchestration succeeded!")
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"ERROR - Orchestration failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n=== Full Result ===")
    if 'result' in locals():
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
