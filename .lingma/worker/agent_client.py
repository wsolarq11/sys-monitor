#!/usr/bin/env python3
"""
Agent通信客户端 - 通过stdio调用目标Agent

职责:
1. 通过stdio调用目标Agent脚本
2. JSON-RPC 2.0协议封装
3. Session管理和超时控制
4. 请求/响应日志记录
5. traceId传递和链路追踪
"""

import json
import subprocess
import sys
import uuid
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class JSONRPCRequest:
    """JSON-RPC 2.0 请求"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: str = ""
    trace_id: str = ""  # 链路追踪ID
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.trace_id:
            self.trace_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id,
            "trace_id": self.trace_id
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class JSONRPCResponse:
    """JSON-RPC 2.0 响应"""
    jsonrpc: str = "2.0"
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    id: str = ""
    trace_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": self.jsonrpc,
            "result": self.result,
            "error": self.error,
            "id": self.id,
            "trace_id": self.trace_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JSONRPCResponse':
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            result=data.get("result"),
            error=data.get("error"),
            id=data.get("id", ""),
            trace_id=data.get("trace_id", "")
        )


class AgentSession:
    """Agent会话管理"""
    
    def __init__(self, agent_name: str, session_id: Optional[str] = None):
        self.agent_name = agent_name
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.request_count = 0
        self.error_count = 0
    
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = datetime.now()
    
    def increment_request(self):
        """增加请求计数"""
        self.request_count += 1
        self.update_activity()
    
    def increment_error(self):
        """增加错误计数"""
        self.error_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "request_count": self.request_count,
            "error_count": self.error_count
        }


class AgentClient:
    """
    Agent通信客户端
    
    通过subprocess调用目标Agent脚本,使用JSON-RPC 2.0协议进行通信。
    
    支持的Agent类型:
    - spec-driven-core-agent: 代码实现
    - test-runner-agent: 测试执行
    - code-review-agent: 代码审查
    - documentation-agent: 文档生成
    - supervisor-agent: 任务编排
    """
    
    def __init__(
        self,
        agents_dir: Optional[Path] = None,
        default_timeout: int = 60,
        log_dir: Optional[Path] = None
    ):
        """
        初始化Agent客户端
        
        Args:
            agents_dir: Agent定义目录,默认为 .lingma/agents
            default_timeout: 默认超时时间(秒)
            log_dir: 日志目录,默认为 .lingma/logs
        """
        self.agents_dir = agents_dir or (Path.cwd() / ".lingma" / "agents")
        self.default_timeout = default_timeout
        self.log_dir = log_dir or (Path.cwd() / ".lingma" / "logs")
        
        # 创建日志目录
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 会话管理
        self.sessions: Dict[str, AgentSession] = {}
        
        # 日志文件
        self.log_file = self.log_dir / "agent-client.log"
    
    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️  无法写入日志: {e}", file=sys.stderr)
    
    def _get_agent_script(self, agent_name: str) -> Optional[Path]:
        """
        获取Agent脚本路径
        
        Args:
            agent_name: Agent名称
            
        Returns:
            Agent脚本路径,如果不存在则返回None
        """
        # 映射Agent名称到脚本文件
        agent_scripts = {
            "spec-driven-core-agent": "spec-driven-agent.py",
            "test-runner-agent": "test-runner.py",
            "code-review-agent": "code-reviewer.py",
            "documentation-agent": "doc-generator.py",
            "supervisor-agent": "supervisor-agent.py"
        }
        
        script_name = agent_scripts.get(agent_name)
        if not script_name:
            # 尝试直接使用agent_name作为脚本名
            script_name = f"{agent_name}.py"
        
        # 在scripts目录中查找
        scripts_dir = Path.cwd() / ".lingma" / "scripts"
        script_path = scripts_dir / script_name
        
        if script_path.exists():
            self._log(f"找到Agent脚本: {agent_name} -> {script_path}")
            return script_path
        
        self._log(f"Agent脚本未找到: {agent_name} ({script_path})", "ERROR")
        return None
    
    def create_session(self, agent_name: str) -> str:
        """
        创建新的Agent会话
        
        Args:
            agent_name: Agent名称
            
        Returns:
            会话ID
        """
        session = AgentSession(agent_name)
        self.sessions[session.session_id] = session
        
        self._log(f"创建会话: {session.session_id} for {agent_name}")
        return session.session_id
    
    def destroy_session(self, session_id: str) -> bool:
        """
        销毁会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功销毁
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._log(f"销毁会话: {session_id}")
            return True
        return False
    
    def call_agent(
        self,
        agent_name: str,
        method: str,
        params: Dict[str, Any],
        timeout: Optional[int] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> JSONRPCResponse:
        """
        调用Agent方法
        
        Args:
            agent_name: Agent名称
            method: 方法名
            params: 方法参数
            timeout: 超时时间(秒),None则使用默认值
            session_id: 可选的会话ID
            trace_id: 链路追踪ID
            
        Returns:
            JSON-RPC响应
        """
        timeout = timeout or self.default_timeout
        trace_id = trace_id or str(uuid.uuid4())
        
        # 创建或更新会话
        if session_id:
            if session_id not in self.sessions:
                return JSONRPCResponse(
                    error={
                        "code": -32000,
                        "message": f"Invalid session ID: {session_id}"
                    },
                    trace_id=trace_id
                )
            session = self.sessions[session_id]
            session.increment_request()
        else:
            session_id = self.create_session(agent_name)
            session = self.sessions[session_id]
        
        # 构建请求
        request = JSONRPCRequest(
            method=method, 
            params=params, 
            id=str(uuid.uuid4()),
            trace_id=trace_id
        )
        
        self._log(f"[{trace_id}] 调用Agent: {agent_name}.{method} (session: {session_id})")
        self._log(f"[{trace_id}] 输入参数: {json.dumps(params, ensure_ascii=False)[:500]}")
        
        start_time = time.time()
        
        try:
            # 获取Agent脚本
            script_path = self._get_agent_script(agent_name)
            
            if script_path is None:
                # 如果没有专用脚本,返回错误(不再使用fallback)
                error_msg = f"Agent脚本不存在: {agent_name}"
                self._log(f"[{trace_id}] {error_msg}", "ERROR")
                
                return JSONRPCResponse(
                    error={
                        "code": -32003,
                        "message": error_msg
                    },
                    id=request.id,
                    trace_id=trace_id
                )
            
            # 执行Agent脚本
            result = self._execute_script(script_path, method, params, timeout, trace_id)
            
            duration = time.time() - start_time
            
            # 解析响应
            if isinstance(result, dict):
                response = JSONRPCResponse.from_dict(result)
            else:
                response = JSONRPCResponse(result=result)
            
            response.id = request.id
            response.trace_id = trace_id
            
            self._log(f"[{trace_id}] Agent调用成功: {agent_name}.{method} (耗时: {duration:.2f}s)")
            self._log(f"[{trace_id}] 输出结果: {json.dumps(response.result, ensure_ascii=False)[:500] if response.result else 'None'}")
            
            return response
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            session.increment_error()
            error_msg = f"Agent调用超时: {agent_name}.{method} (timeout: {timeout}s, elapsed: {duration:.2f}s)"
            self._log(f"[{trace_id}] {error_msg}", "ERROR")
            
            return JSONRPCResponse(
                error={
                    "code": -32001,
                    "message": error_msg
                },
                id=request.id,
                trace_id=trace_id
            )
            
        except Exception as e:
            duration = time.time() - start_time
            session.increment_error()
            error_msg = f"Agent调用失败: {str(e)} (耗时: {duration:.2f}s)"
            self._log(f"[{trace_id}] {error_msg}", "ERROR")
            
            return JSONRPCResponse(
                error={
                    "code": -32002,
                    "message": error_msg
                },
                id=request.id,
                trace_id=trace_id
            )
    
    def _execute_script(
        self,
        script_path: Path,
        method: str,
        params: Dict[str, Any],
        timeout: int,
        trace_id: str
    ) -> Any:
        """
        执行Agent脚本
        
        Args:
            script_path: 脚本路径
            method: 方法名
            params: 参数
            timeout: 超时时间
            trace_id: 链路追踪ID
            
        Returns:
            执行结果
        """
        # 构建命令
        cmd = [sys.executable, str(script_path), "--json-rpc"]
        
        # 准备输入数据
        input_data = {
            "method": method,
            "params": params,
            "trace_id": trace_id
        }
        
        self._log(f"[{trace_id}] 执行命令: {' '.join(cmd)}")
        
        # 执行子进程
        process = subprocess.run(
            cmd,
            input=json.dumps(input_data, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            cwd=str(Path.cwd())
        )
        
        # 检查返回码
        if process.returncode != 0:
            error_detail = process.stderr[:1000] if process.stderr else "Unknown error"
            raise RuntimeError(f"脚本执行失败 (returncode={process.returncode}): {error_detail}")
        
        # 解析输出
        try:
            output = json.loads(process.stdout)
            self._log(f"[{trace_id}] 脚本输出解析成功")
            return output
        except json.JSONDecodeError as e:
            # 如果不是JSON,返回原始输出
            self._log(f"[{trace_id}] 警告: 脚本输出不是有效JSON: {str(e)}", "WARNING")
            return {"result": process.stdout[:2000]}
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话信息字典
        """
        if session_id in self.sessions:
            return self.sessions[session_id].to_dict()
        return None
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有活跃会话
        
        Returns:
            会话信息列表
        """
        return [session.to_dict() for session in self.sessions.values()]
    
    def cleanup_inactive_sessions(self, max_idle_seconds: int = 3600):
        """
        清理不活跃的会话
        
        Args:
            max_idle_seconds: 最大空闲时间(秒)
        """
        inactive_sessions = []
        
        for session_id, session in self.sessions.items():
            idle_time = (datetime.now() - session.last_activity).total_seconds()
            if idle_time > max_idle_seconds:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            self.destroy_session(session_id)
            self._log(f"清理不活跃会话: {session_id}")


# 单元测试
def run_tests():
    """运行单元测试"""
    import tempfile
    
    print("🧪 运行AgentClient单元测试...\n")
    
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as tmpdir:
        agents_dir = Path(tmpdir) / "agents"
        log_dir = Path(tmpdir) / "logs"
        agents_dir.mkdir()
        log_dir.mkdir()
        
        client = AgentClient(agents_dir=agents_dir, log_dir=log_dir)
        
        # 测试1: 会话管理
        print("✅ 测试1: 会话管理")
        session_id = client.create_session("test-agent")
        assert session_id in client.sessions
        assert client.sessions[session_id].agent_name == "test-agent"
        print(f"   ✓ 会话创建成功: {session_id}")
        
        # 测试2: 会话信息查询
        print("\n✅ 测试2: 会话信息查询")
        session_info = client.get_session_info(session_id)
        assert session_info is not None
        assert session_info["agent_name"] == "test-agent"
        assert session_info["request_count"] == 0
        print(f"   ✓ 会话信息查询正常")
        
        # 测试3: 活跃会话列表
        print("\n✅ 测试3: 活跃会话列表")
        session_id2 = client.create_session("another-agent")
        active_sessions = client.get_active_sessions()
        assert len(active_sessions) == 2
        print(f"   ✓ 活跃会话数量: {len(active_sessions)}")
        
        # 测试4: 会话销毁
        print("\n✅ 测试4: 会话销毁")
        success = client.destroy_session(session_id)
        assert success
        assert session_id not in client.sessions
        assert client.get_session_info(session_id) is None
        print(f"   ✓ 会话销毁成功")
        
        # 测试5: Agent调用(脚本不存在应返回错误)
        print("\n✅ 测试5: Agent调用(脚本不存在)")
        response = client.call_agent(
            "nonexistent-agent",
            "test_method",
            {"param1": "value1"},
            timeout=5
        )
        assert response.error is not None
        assert response.error["code"] == -32003
        assert "Agent脚本不存在" in response.error["message"]
        print(f"   ✓ 正确返回错误(无fallback)")
        
        # 测试6: 无效会话调用
        print("\n✅ 测试6: 无效会话调用")
        response = client.call_agent(
            "test-agent",
            "test_method",
            {},
            session_id="invalid-session-id"
        )
        assert response.error is not None
        assert response.error["code"] == -32000
        print(f"   ✓ 无效会话检测正常")
        
        # 测试7: traceId传递
        print("\n✅ 测试7: traceId传递和链路追踪")
        custom_trace_id = "test-trace-12345"
        response = client.call_agent(
            "test-agent",
            "test_method",
            {},
            trace_id=custom_trace_id
        )
        assert response.trace_id == custom_trace_id
        print(f"   ✓ traceId正确传递: {response.trace_id}")
        
        # 测试8: 清理不活跃会话
        print("\n✅ 测试8: 清理不活跃会话")
        # 手动设置会话为不活跃
        from datetime import timedelta
        for session in client.sessions.values():
            session.last_activity = datetime.now() - timedelta(hours=2)
        
        client.cleanup_inactive_sessions(max_idle_seconds=3600)
        assert len(client.sessions) == 0
        print(f"   ✓ 不活跃会话已清理")
        
        # 测试9: JSON-RPC请求序列化
        print("\n✅ 测试9: JSON-RPC请求序列化")
        request = JSONRPCRequest(method="test", params={"key": "value"})
        request_dict = request.to_dict()
        assert request_dict["jsonrpc"] == "2.0"
        assert request_dict["method"] == "test"
        assert request_dict["params"]["key"] == "value"
        assert "id" in request_dict
        assert "trace_id" in request_dict
        print(f"   ✓ JSON-RPC请求序列化正常(包含trace_id)")
        
        # 测试10: JSON-RPC响应反序列化
        print("\n✅ 测试10: JSON-RPC响应反序列化")
        response_data = {
            "jsonrpc": "2.0",
            "result": {"output": "success"},
            "id": "test-id",
            "trace_id": "trace-xyz"
        }
        response = JSONRPCResponse.from_dict(response_data)
        assert response.jsonrpc == "2.0"
        assert response.result["output"] == "success"
        assert response.id == "test-id"
        assert response.trace_id == "trace-xyz"
        print(f"   ✓ JSON-RPC响应反序列化正常(包含trace_id)")
        
        print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        print("用法: python agent_client.py --test")
