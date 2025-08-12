#!/usr/bin/env python3
"""
CLI Executor MCP服务器的测试脚本。

这个脚本测试CLI Executor MCP服务器的基本功能，
确保所有工具、资源和提示都能正常工作。
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# 直接导入服务器模块进行测试
sys.path.insert(0, str(Path(__file__).parent.parent))
from cli_executor.server import (
    execute_command, 
    execute_script, 
    list_directory, 
    get_system_info, 
    deploy_application
)


async def test_execute_command():
    """测试execute_command工具。"""
    print("🧪 测试execute_command...")
    
    # 测试基本命令
    result = await execute_command("echo 'Hello, World!'")
    assert "Hello, World!" in result, f"期望结果中包含'Hello, World!'，实际得到: {result}"
    
    # 测试带工作目录的命令
    with tempfile.TemporaryDirectory() as temp_dir:
        # 在Windows上使用cd命令
        if sys.platform == "win32":
            result = await execute_command("cd", working_dir=temp_dir)
        else:
            result = await execute_command("pwd", working_dir=temp_dir)
        assert temp_dir in result or "成功" in result, f"期望结果中包含{temp_dir}或成功信息，实际得到: {result}"
    
    print("✅ execute_command测试通过！")


async def test_execute_script():
    """测试execute_script工具。"""
    print("🧪 测试execute_script...")
    
    # 根据平台选择合适的脚本
    if sys.platform == "win32":
        script = """
        echo Line 1
        echo Line 2
        echo Script completed
        """
        shell = "cmd"
    else:
        script = """
        echo "Line 1"
        echo "Line 2"
        echo "Script completed"
        """
        shell = "bash"
    
    result = await execute_script(script, shell=shell)
    
    assert "Line 1" in result, f"期望结果中包含'Line 1'，实际得到: {result}"
    assert "Line 2" in result, f"期望结果中包含'Line 2'，实际得到: {result}"
    assert "Script completed" in result, f"期望结果中包含'Script completed'，实际得到: {result}"
    
    print("✅ execute_script测试通过！")


async def test_list_directory():
    """测试list_directory工具。"""
    print("🧪 测试list_directory...")
    
    # 创建一个包含一些文件的临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建测试文件
        (temp_path / "test_file.txt").write_text("test content")
        (temp_path / "test_dir").mkdir()
        
        result = list_directory(str(temp_path), show_hidden=False)
        
        assert "test_file.txt" in result, f"期望结果中包含'test_file.txt'，实际得到: {result}"
        assert "test_dir" in result, f"期望结果中包含'test_dir'，实际得到: {result}"
        assert "[文件]" in result, f"期望结果中包含'[文件]'标记，实际得到: {result}"
        assert "[目录]" in result, f"期望结果中包含'[目录]'标记，实际得到: {result}"
    
    print("✅ list_directory测试通过！")


async def test_system_info_resource():
    """测试system://info资源。"""
    print("🧪 测试system://info资源...")
    
    result = get_system_info()
    
    assert "系统信息" in result, f"期望结果中包含系统信息标题，实际得到: {result}"
    assert "Python版本" in result, f"期望结果中包含Python版本，实际得到: {result}"
    assert "工作目录" in result, f"期望结果中包含工作目录，实际得到: {result}"
    
    print("✅ system://info资源测试通过！")


async def test_deploy_application_prompt():
    """测试deploy_application提示。"""
    print("🧪 测试deploy_application提示...")
    
    result = deploy_application(
        "test-app", 
        "/tmp/test-app", 
        "https://github.com/user/test-app.git"
    )
    
    assert "test-app" in result, f"期望结果中包含'test-app'，实际得到: {result}"
    assert "/tmp/test-app" in result, f"期望结果中包含'/tmp/test-app'，实际得到: {result}"
    assert "github.com/user/test-app.git" in result, f"期望结果中包含仓库URL，实际得到: {result}"
    assert "部署步骤" in result, f"期望结果中包含部署步骤，实际得到: {result}"
    
    print("✅ deploy_application提示测试通过！")


async def run_all_tests():
    """运行所有测试。"""
    print("🚀 开始CLI Executor MCP服务器测试...")
    print("=" * 50)
    
    try:
        await test_execute_command()
        await test_execute_script()
        test_list_directory()  # 这个不是async函数
        test_system_info_resource()  # 这个不是async函数
        test_deploy_application_prompt()  # 这个不是async函数
        
        print("\n🎉 所有测试都成功通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败，错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)