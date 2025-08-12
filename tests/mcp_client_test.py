#!/usr/bin/env python3
"""
使用真实MCP客户端测试CLI Executor MCP服务器。
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import fastmcp
    HAS_FASTMCP_CLIENT = True
except ImportError:
    HAS_FASTMCP_CLIENT = False


async def test_with_fastmcp_client():
    """使用FastMCP客户端测试服务器。"""
    if not HAS_FASTMCP_CLIENT:
        print("⚠️ FastMCP客户端不可用，跳过客户端测试")
        return True
    
    print("🧪 使用FastMCP客户端测试...")
    
    try:
        # 创建客户端连接
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        # 使用MCP SDK创建客户端
        server_params = StdioServerParameters(
            command="cli-executor-mcp",
            args=["--transport", "stdio"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化会话
                await session.initialize()
                print("   ✅ 客户端连接成功")
                
                # 测试执行简单命令
                result = await session.call_tool("execute_command", {
                    "command": "echo 'Hello from MCP!'"
                })
                print(f"   ✅ 命令执行结果: {str(result)[:50]}...")
                
                # 测试列出目录
                result = await session.call_tool("list_directory", {
                    "path": "."
                })
                print(f"   ✅ 目录列表结果: {len(str(result))} 字符")
                
                # 测试获取系统信息
                result = await session.read_resource("system://info")
                print(f"   ✅ 系统信息结果: {len(str(result))} 字符")
                
                print("   ✅ 客户端连接已关闭")
        

        
        print("✅ FastMCP客户端测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ FastMCP客户端测试失败: {e}")
        return False


def test_server_with_simple_input():
    """使用简单输入测试服务器。"""
    print("🧪 使用简单输入测试服务器...")
    
    try:
        # 启动服务器进程
        process = subprocess.Popen(
            ["cli-executor-mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        time.sleep(2)
        
        # 发送简单的MCP初始化消息
        init_message = '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}\n'
        
        try:
            # 发送消息
            process.stdin.write(init_message)
            process.stdin.flush()
            
            # 等待响应
            time.sleep(1)
            
            # 终止进程
            process.terminate()
            
            # 获取输出
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            
            # 检查是否有正确的启动信息
            assert "正在启动CLI Executor MCP服务器" in stderr, f"启动信息不正确: {stderr}"
            
            print("✅ 简单输入测试通过！")
            return True
            
        except Exception as e:
            process.kill()
            raise e
            
    except Exception as e:
        print(f"❌ 简单输入测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有MCP测试。"""
    print("🚀 开始CLI Executor MCP客户端测试...")
    print("=" * 50)
    
    tests = [
        ("简单输入测试", test_server_with_simple_input),
        ("FastMCP客户端测试", test_with_fastmcp_client),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行 {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有MCP测试都成功通过！")
        return True
    else:
        print("⚠️ 部分MCP测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)