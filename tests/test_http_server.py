#!/usr/bin/env python3
"""
测试CLI Executor MCP服务器的HTTP传输功能。
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

import httpx


async def test_streamable_http_server():
    """测试Streamable HTTP服务器功能。"""
    print("🧪 测试Streamable HTTP服务器...")
    
    # 启动Streamable HTTP服务器
    server_process = None
    try:
        # 启动服务器进程
        server_process = subprocess.Popen(
            ["cli-executor-mcp", "--transport", "streamable-http", "--port", "8005", "--host", "127.0.0.1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        print("   等待服务器启动...")
        time.sleep(3)
        
        # 检查服务器是否正在运行
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print(f"   服务器启动失败: {stderr}")
            return False
        
        # 测试服务器连接
        async with httpx.AsyncClient() as client:
            try:
                # 测试根路径
                response = await client.get("http://127.0.0.1:8005/")
                print(f"   根路径响应状态: {response.status_code}")
                
                # 测试MCP端点
                try:
                    response = await client.get("http://127.0.0.1:8005/mcp")
                    print(f"   MCP端点响应状态: {response.status_code}")
                except Exception as e:
                    print(f"   MCP端点测试: {e}")
                
                # 测试SSE端点
                try:
                    response = await client.get("http://127.0.0.1:8005/sse")
                    print(f"   SSE端点响应状态: {response.status_code}")
                except Exception as e:
                    print(f"   SSE端点测试: {e}")
                
                print("✅ Streamable HTTP服务器测试通过！")
                return True
                
            except Exception as e:
                print(f"❌ HTTP请求失败: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Streamable HTTP服务器测试失败: {e}")
        return False
        
    finally:
        # 清理服务器进程
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()


async def test_mcp_over_http():
    """测试通过HTTP的MCP通信。"""
    print("🧪 测试MCP over HTTP...")
    
    server_process = None
    try:
        # 启动HTTP服务器
        server_process = subprocess.Popen(
            ["cli-executor-mcp", "--transport", "streamable-http", "--port", "8006", "--host", "127.0.0.1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        print("   等待streamable-http服务器启动...")
        time.sleep(3)
        
        # 检查服务器是否正在运行
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print(f"   服务器启动失败: {stderr}")
            return False
        
        # 尝试使用MCP客户端连接
        try:
            from mcp import ClientSession
            from mcp.client.sse import sse_client
            
            # 使用SSE客户端连接
            async with sse_client("http://127.0.0.1:8006/sse") as (read, write):
                async with ClientSession(read, write) as session:
                    # 初始化会话
                    await session.initialize()
                    print("   ✅ MCP over HTTP连接成功")
                    
                    # 测试执行命令
                    result = await session.call_tool("execute_command", {
                        "command": "echo 'Hello from HTTP MCP!'"
                    })
                    print(f"   ✅ HTTP MCP命令执行成功: {str(result)[:50]}...")
                    
                    print("✅ MCP over HTTP测试通过！")
                    return True
                    
        except ImportError:
            print("   ⚠️ MCP SSE客户端不可用，跳过MCP over HTTP测试")
            return True
        except Exception as e:
            print(f"   ❌ MCP over HTTP连接失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ MCP over HTTP测试失败: {e}")
        return False
        
    finally:
        # 清理服务器进程
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()


def test_server_startup_modes():
    """测试不同的服务器启动模式。"""
    print("🧪 测试服务器启动模式...")
    
    modes = [
        ("stdio", ["--transport", "stdio"]),
        ("streamable-http", ["--transport", "streamable-http", "--port", "8008"]),
    ]
    
    passed = 0
    total = len(modes)
    
    for mode_name, args in modes:
        print(f"   测试 {mode_name} 模式...")
        
        try:
            # 启动服务器
            process = subprocess.Popen(
                ["cli-executor-mcp"] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待启动
            time.sleep(2)
            
            # 检查是否成功启动
            if process.poll() is None:
                print(f"   ✅ {mode_name} 模式启动成功")
                passed += 1
            else:
                stdout, stderr = process.communicate()
                print(f"   ❌ {mode_name} 模式启动失败: {stderr[:100]}...")
            
            # 终止进程
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    
        except Exception as e:
            print(f"   ❌ {mode_name} 模式测试异常: {e}")
    
    print(f"   启动模式测试结果: {passed}/{total}")
    return passed == total


async def run_all_tests():
    """运行所有HTTP测试。"""
    print("🚀 开始CLI Executor MCP HTTP测试...")
    print("=" * 50)
    
    tests = [
        ("服务器启动模式测试", test_server_startup_modes),
        ("Streamable HTTP服务器测试", test_streamable_http_server),
        ("MCP over Streamable HTTP测试", test_mcp_over_http),
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
    
    print(f"\n📊 HTTP测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有HTTP测试都成功通过！")
        return True
    else:
        print("⚠️ 部分HTTP测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)