"""
CLI Executor MCP 示例客户端

这个示例展示了如何使用MCP客户端连接到CLI Executor MCP服务器并调用其工具。
"""

import asyncio
import os
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main():
    """
    示例客户端的主函数
    """
    print("连接到CLI Executor MCP服务器...")
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "cli_server.py")
    
    # 使用stdio传输连接到服务器
    async with stdio_client(
        StdioServerParameters(command="python", args=[server_path])
    ) as (read, write):
        # 创建客户端会话
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            print("已连接到服务器")
            
            # 列出可用工具
            tools = await session.list_tools()
            print(f"可用工具: {tools}")
            
            # 列出可用资源
            resources = await session.list_resources()
            print(f"可用资源: {resources}")
            
            # 列出可用提示
            prompts = await session.list_prompts()
            print(f"可用提示: {prompts}")
            
            # 获取系统信息
            print("\n获取系统信息...")
            content, mime_type = await session.read_resource("system://info")
            print(f"系统信息 (MIME类型: {mime_type}):")
            print(content)
            
            # 执行命令
            print("\n执行命令...")
            result = await session.call_tool("execute_command", {"command": "ls -la"})
            print("命令结果:")
            print(result)
            
            # 执行脚本
            print("\n执行脚本...")
            script = """
mkdir -p test_dir
cd test_dir
echo "Hello, World!" > test.txt
ls -la
"""
            result = await session.call_tool("execute_script", {"script": script})
            print("脚本结果:")
            print(result)
            
            # 列出目录
            print("\n列出目录...")
            result = await session.call_tool("list_directory", {"path": "."})
            print("目录内容:")
            print(result)
            
            # 获取提示
            print("\n获取部署应用提示...")
            prompt = await session.get_prompt("deploy_app", {"app_name": "测试应用", "target_dir": "/tmp/test_app"})
            print("提示内容:")
            print(prompt)


if __name__ == "__main__":
    asyncio.run(main()) 