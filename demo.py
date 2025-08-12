#!/usr/bin/env python3
"""
CLI Executor MCP 演示脚本

展示CLI Executor MCP服务器的所有功能和特性。
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def print_banner():
    """打印演示横幅。"""
    banner = """
╭─────────────────────────────────────────────────────────────────╮
│                                                                 │
│  🚀 CLI Executor MCP - 命令行执行器演示                           │
│                                                                 │
│  基于FastMCP 2.11+构建的MCP服务器                                │
│  支持命令执行、脚本运行、目录操作等功能                             │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯
"""
    print(banner)


def print_section(title):
    """打印章节标题。"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)


async def demo_basic_commands():
    """演示基本命令执行。"""
    print_section("基本命令执行演示")
    
    server_params = StdioServerParameters(
        command="cli-executor-mcp",
        args=["--transport", "stdio"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ MCP会话初始化成功\n")
            
            # 演示1：简单命令
            print("📋 演示1：执行简单命令")
            if os.name == 'nt':
                cmd = "echo 欢迎使用CLI Executor MCP!"
            else:
                cmd = "echo '欢迎使用CLI Executor MCP!'"
            
            result = await session.call_tool("execute_command", {"command": cmd})
            output = result.content[0].text
            print(f"命令: {cmd}")
            print(f"输出: {output.strip()}\n")
            
            # 演示2：获取系统信息
            print("📋 演示2：获取系统信息")
            result = await session.read_resource("system://info")
            system_info = result.contents[0].text
            
            # 只显示前几行
            lines = system_info.split('\n')[:10]
            for line in lines:
                print(f"  {line}")
            print(f"  ... (共 {len(system_info)} 字符)\n")
            
            # 演示3：列出目录
            print("📋 演示3：列出当前目录")
            result = await session.call_tool("list_directory", {"path": "."})
            dir_listing = result.content[0].text
            
            # 只显示前几行
            lines = dir_listing.split('\n')[:8]
            for line in lines:
                print(f"  {line}")
            print(f"  ... (共 {len(dir_listing)} 字符)\n")


async def demo_script_execution():
    """演示脚本执行。"""
    print_section("脚本执行演示")
    
    server_params = StdioServerParameters(
        command="cli-executor-mcp",
        args=["--transport", "stdio"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("📋 演示：执行多行脚本")
            
            if os.name == 'nt':  # Windows
                script = """
echo 开始执行脚本...
echo 当前时间: %date% %time%
echo 正在创建临时文件...
echo Hello World > temp_demo.txt
echo 文件内容:
type temp_demo.txt
del temp_demo.txt
echo 脚本执行完成!
"""
                shell = "cmd"
            else:  # Unix-like
                script = """
echo "开始执行脚本..."
echo "当前时间: $(date)"
echo "正在创建临时文件..."
echo "Hello World" > temp_demo.txt
echo "文件内容:"
cat temp_demo.txt
rm temp_demo.txt
echo "脚本执行完成!"
"""
                shell = "bash"
            
            print("脚本内容:")
            for i, line in enumerate(script.strip().split('\n'), 1):
                print(f"  {i:2d}: {line}")
            
            print(f"\n执行脚本 (使用 {shell})...")
            result = await session.call_tool("execute_script", {
                "script": script,
                "shell": shell
            })
            
            output = result.content[0].text
            print("脚本输出:")
            for line in output.split('\n'):
                if line.strip():
                    print(f"  {line}")


async def demo_deployment_prompt():
    """演示部署提示生成。"""
    print_section("部署提示生成演示")
    
    server_params = StdioServerParameters(
        command="cli-executor-mcp",
        args=["--transport", "stdio"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("📋 演示：生成应用部署提示")
            
            result = await session.get_prompt("deploy_application", {
                "app_name": "我的Web应用",
                "target_dir": "/var/www/my-web-app",
                "repo_url": "https://github.com/user/my-web-app.git"
            })
            
            deploy_prompt = result.messages[0].content.text
            
            # 显示提示的前几行
            lines = deploy_prompt.split('\n')
            for i, line in enumerate(lines[:15]):
                print(f"  {line}")
            
            print(f"  ... (共 {len(lines)} 行)")


def demo_features():
    """演示功能特性。"""
    print_section("功能特性总览")
    
    features = [
        "🚀 FastMCP实现 - 基于FastMCP 2.11+框架",
        "🔧 命令执行 - 支持单个CLI命令执行，自动环境变量加载",
        "📜 脚本执行 - 支持多行脚本，跨平台shell兼容",
        "📁 目录操作 - 详细的文件和目录列表，支持隐藏文件",
        "🖥️ 系统信息 - 全面的系统和环境信息获取",
        "📋 部署模板 - 智能的应用部署指导提示",
        "⚡ 多种传输 - 支持stdio、HTTP、streamable-HTTP",
        "🛡️ 安全特性 - 命令超时、错误处理、输入验证",
        "🔍 跨平台 - Windows、macOS、Linux全平台支持",
        "🌐 中文支持 - 完整的中文界面和文档"
    ]
    
    for feature in features:
        print(f"  {feature}")
        time.sleep(0.1)  # 添加小延迟以增强演示效果


def demo_usage_examples():
    """演示使用示例。"""
    print_section("使用示例")
    
    examples = [
        ("启动服务器 (stdio)", "cli-executor-mcp"),
        ("启动HTTP服务器", "cli-executor-mcp --transport http --port 8000"),
        ("启动调试模式", "cli-executor-mcp --debug"),
        ("查看帮助", "cli-executor-mcp --help"),
        ("运行测试", "python tests/simple_test.py"),
        ("运行集成测试", "python tests/integration_test.py"),
    ]
    
    for desc, cmd in examples:
        print(f"  📌 {desc}:")
        print(f"     {cmd}\n")


async def main():
    """主演示函数。"""
    print_banner()
    
    print("🎬 开始CLI Executor MCP功能演示...")
    print("   按 Ctrl+C 可随时退出演示")
    
    try:
        # 功能特性演示
        demo_features()
        
        # 使用示例
        demo_usage_examples()
        
        # 等待用户确认
        input("\n按回车键继续实际功能演示...")
        
        # 基本命令演示
        await demo_basic_commands()
        
        # 脚本执行演示
        await demo_script_execution()
        
        # 部署提示演示
        await demo_deployment_prompt()
        
        # 演示结束
        print_section("演示完成")
        print("🎉 CLI Executor MCP演示成功完成！")
        print("\n📚 更多信息:")
        print("   - 查看 README.md 了解详细文档")
        print("   - 运行 python tests/simple_test.py 进行基本测试")
        print("   - 运行 python tests/integration_test.py 进行完整测试")
        print("   - 使用 cli-executor-mcp --help 查看所有选项")
        
        print("\n🚀 项目已完全就绪，可以开始使用了！")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())