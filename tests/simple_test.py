#!/usr/bin/env python3
"""
简单的功能测试脚本。

直接测试CLI Executor MCP服务器的基本功能。
"""

import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path


def test_command_line_tool():
    """测试命令行工具是否正常工作。"""
    print("🧪 测试命令行工具...")
    
    try:
        # 测试帮助命令
        result = subprocess.run(
            ["cli-executor-mcp", "--help"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        assert result.returncode == 0, f"帮助命令失败，返回码: {result.returncode}"
        assert "CLI Executor MCP服务器" in result.stdout, f"帮助信息不正确: {result.stdout}"
        
        print("✅ 命令行工具测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 命令行工具测试失败: {e}")
        return False


def test_import():
    """测试模块导入。"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试导入主模块
        import cli_executor
        assert hasattr(cli_executor, 'mcp'), "模块应该有mcp属性"
        
        # 测试导入服务器模块
        from cli_executor import server
        assert hasattr(server, 'mcp'), "服务器模块应该有mcp属性"
        assert hasattr(server, 'main'), "服务器模块应该有main函数"
        
        print("✅ 模块导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 模块导入测试失败: {e}")
        return False


def test_server_startup():
    """测试服务器启动（快速测试）。"""
    print("🧪 测试服务器启动...")
    
    try:
        # 启动服务器并快速停止
        process = subprocess.Popen(
            ["cli-executor-mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待一小段时间让服务器启动
        import time
        time.sleep(2)
        
        # 终止进程
        process.terminate()
        
        # 等待进程结束
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        # 检查是否有启动信息
        assert "正在启动CLI Executor MCP服务器" in stderr, f"启动信息不正确: {stderr}"
        
        print("✅ 服务器启动测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 服务器启动测试失败: {e}")
        return False


def test_basic_functions():
    """测试基本函数功能。"""
    print("🧪 测试基本函数功能...")
    
    try:
        # 导入FastMCP实例进行测试
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from cli_executor.server import mcp
        
        # 检查MCP实例是否正确创建
        assert hasattr(mcp, 'name'), "MCP实例应该有name属性"
        assert mcp.name == "CLI Executor", f"MCP名称不正确: {mcp.name}"
        
        # 检查是否有注册的工具
        tools = mcp._tools if hasattr(mcp, '_tools') else {}
        print(f"   已注册的工具数量: {len(tools)}")
        
        # 检查是否有注册的资源
        resources = mcp._resources if hasattr(mcp, '_resources') else {}
        print(f"   已注册的资源数量: {len(resources)}")
        
        # 检查是否有注册的提示
        prompts = mcp._prompts if hasattr(mcp, '_prompts') else {}
        print(f"   已注册的提示数量: {len(prompts)}")
        
        print("✅ 基本函数功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 基本函数功能测试失败: {e}")
        return False


def test_package_info():
    """测试包信息。"""
    print("🧪 测试包信息...")
    
    try:
        import cli_executor
        
        # 检查版本信息
        assert hasattr(cli_executor, '__version__'), "包应该有版本信息"
        assert cli_executor.__version__ == "1.0.0", f"版本信息不正确: {cli_executor.__version__}"
        
        # 检查作者信息
        assert hasattr(cli_executor, '__author__'), "包应该有作者信息"
        assert cli_executor.__author__ == "CaptainJi", f"作者信息不正确: {cli_executor.__author__}"
        
        print("✅ 包信息测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 包信息测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试。"""
    print("🚀 开始CLI Executor MCP简单测试...")
    print("=" * 50)
    
    tests = [
        test_import,
        test_package_info,
        test_basic_functions,
        test_command_line_tool,
        test_server_startup,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # 空行分隔
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            print()
    
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试都成功通过！")
        return True
    else:
        print("⚠️ 部分测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)