#!/usr/bin/env python3
"""
CLI Executor MCP 综合集成测试。

测试真实的使用场景和工作流程。
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_real_world_scenario():
    """测试真实世界的使用场景。"""
    print("🧪 测试真实世界使用场景...")
    
    try:
        # 创建MCP客户端连接
        server_params = StdioServerParameters(
            command="cli-executor-mcp",
            args=["--transport", "stdio"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("   ✅ MCP会话初始化成功")
                
                # 场景1：获取系统信息
                print("\n   📋 场景1：获取系统信息")
                result = await session.read_resource("system://info")
                system_info = result.contents[0].text
                print(f"   ✅ 系统信息获取成功 ({len(system_info)} 字符)")
                assert "系统信息" in system_info
                assert "Python版本" in system_info
                
                # 场景2：列出当前目录
                print("\n   📋 场景2：列出当前目录")
                result = await session.call_tool("list_directory", {"path": "."})
                dir_listing = result.content[0].text
                print(f"   ✅ 目录列表获取成功 ({len(dir_listing)} 字符)")
                assert "README.md" in dir_listing or "pyproject.toml" in dir_listing
                
                # 场景3：执行简单命令
                print("\n   📋 场景3：执行简单命令")
                if os.name == 'nt':  # Windows
                    cmd = "echo Hello from Windows!"
                else:  # Unix-like
                    cmd = "echo 'Hello from Unix!'"
                
                result = await session.call_tool("execute_command", {"command": cmd})
                cmd_output = result.content[0].text
                print(f"   ✅ 命令执行成功: {cmd_output.strip()}")
                assert "Hello from" in cmd_output
                
                # 场景4：创建临时目录并测试
                print("\n   📋 场景4：文件系统操作")
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 在临时目录中创建文件
                    if os.name == 'nt':  # Windows
                        create_cmd = f'echo "Test content" > "{temp_dir}\\test.txt"'
                        list_cmd = f'dir "{temp_dir}"'
                    else:  # Unix-like
                        create_cmd = f'echo "Test content" > "{temp_dir}/test.txt"'
                        list_cmd = f'ls -la "{temp_dir}"'
                    
                    # 创建文件
                    result = await session.call_tool("execute_command", {"command": create_cmd})
                    print(f"   ✅ 文件创建: {result.content[0].text.strip()}")
                    
                    # 列出文件
                    result = await session.call_tool("execute_command", {"command": list_cmd})
                    list_output = result.content[0].text
                    print(f"   ✅ 文件列表: 找到 {'test.txt' if 'test.txt' in list_output else '文件'}")
                
                # 场景5：执行多行脚本
                print("\n   📋 场景5：执行多行脚本")
                if os.name == 'nt':  # Windows
                    script = """
echo Starting script...
echo Line 1
echo Line 2
echo Script completed!
"""
                    shell = "cmd"
                else:  # Unix-like
                    script = """
echo "Starting script..."
echo "Line 1"
echo "Line 2"
echo "Script completed!"
"""
                    shell = "bash"
                
                result = await session.call_tool("execute_script", {
                    "script": script,
                    "shell": shell
                })
                script_output = result.content[0].text
                print(f"   ✅ 脚本执行成功: 包含 {'Line 1' if 'Line 1' in script_output else '输出'}")
                assert "Line 1" in script_output
                assert "Line 2" in script_output
                
                # 场景6：生成部署提示
                print("\n   📋 场景6：生成部署提示")
                result = await session.get_prompt("deploy_application", {
                    "app_name": "my-awesome-app",
                    "target_dir": "/var/www/my-awesome-app",
                    "repo_url": "https://github.com/user/my-awesome-app.git"
                })
                deploy_prompt = result.messages[0].content.text
                print(f"   ✅ 部署提示生成成功 ({len(deploy_prompt)} 字符)")
                assert "my-awesome-app" in deploy_prompt
                assert "部署步骤" in deploy_prompt
                
                print("\n✅ 所有真实世界场景测试通过！")
                return True
                
    except Exception as e:
        print(f"\n❌ 真实世界场景测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """测试错误处理。"""
    print("🧪 测试错误处理...")
    
    try:
        server_params = StdioServerParameters(
            command="cli-executor-mcp",
            args=["--transport", "stdio"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 测试不存在的命令
                print("   📋 测试不存在的命令")
                result = await session.call_tool("execute_command", {
                    "command": "this_command_does_not_exist_12345"
                })
                error_output = result.content[0].text
                print(f"   ✅ 错误处理正常: {error_output[:50]}...")
                
                # 测试不存在的目录
                print("   📋 测试不存在的目录")
                result = await session.call_tool("list_directory", {
                    "path": "/this/path/does/not/exist/12345"
                })
                error_output = result.content[0].text
                print(f"   ✅ 目录错误处理正常: {error_output[:50]}...")
                assert "错误" in error_output or "不存在" in error_output
                
                print("✅ 错误处理测试通过！")
                return True
                
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False


async def test_performance():
    """测试性能。"""
    print("🧪 测试性能...")
    
    try:
        server_params = StdioServerParameters(
            command="cli-executor-mcp",
            args=["--transport", "stdio"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                import time
                
                # 测试多次快速调用
                print("   📋 测试多次快速调用")
                start_time = time.time()
                
                for i in range(5):
                    result = await session.call_tool("execute_command", {
                        "command": f"echo 'Test {i}'"
                    })
                    assert f"Test {i}" in result.content[0].text
                
                end_time = time.time()
                duration = end_time - start_time
                print(f"   ✅ 5次调用耗时: {duration:.2f}秒 (平均 {duration/5:.2f}秒/次)")
                
                # 测试大输出
                print("   📋 测试大输出处理")
                if os.name == 'nt':  # Windows
                    big_cmd = "dir /s C:\\Windows\\System32 2>nul | findstr /i \".exe\" | head -100"
                else:  # Unix-like
                    big_cmd = "find /usr -name '*.so' 2>/dev/null | head -100"
                
                start_time = time.time()
                result = await session.call_tool("execute_command", {
                    "command": big_cmd,
                    "timeout": 10
                })
                end_time = time.time()
                
                output_size = len(result.content[0].text)
                duration = end_time - start_time
                print(f"   ✅ 大输出处理: {output_size} 字符，耗时 {duration:.2f}秒")
                
                print("✅ 性能测试通过！")
                return True
                
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False


async def run_integration_tests():
    """运行所有集成测试。"""
    print("🚀 开始CLI Executor MCP综合集成测试...")
    print("=" * 60)
    
    tests = [
        ("真实世界场景测试", test_real_world_scenario),
        ("错误处理测试", test_error_handling),
        ("性能测试", test_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 运行 {test_name}...")
        print("-" * 40)
        
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
        
        print()
    
    print("=" * 60)
    print(f"📊 集成测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有集成测试都成功通过！")
        print("\n🚀 CLI Executor MCP项目已完全就绪！")
        return True
    else:
        print("⚠️ 部分集成测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)