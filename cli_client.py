"""
CLI Executor MCP Client

这个脚本用于连接CLI Executor MCP服务器并测试其功能。
"""

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 创建服务器参数
server_params = StdioServerParameters(
    command="python",  # 可执行文件
    args=["cli_server.py"],  # 命令行参数
    env=None  # 环境变量
)

async def run():
    print("正在连接到CLI Executor MCP服务器...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            print("连接成功！")

            # 列出可用工具
            tools = await session.list_tools()
            print("\n可用工具:")
            if hasattr(tools, 'tools'):
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description}")
            else:
                print("无法获取工具列表")

            # 列出可用资源
            resources = await session.list_resources()
            print("\n可用资源:")
            if hasattr(resources, 'resources'):
                for resource in resources.resources:
                    print(f"- {resource}")
            else:
                print("无法获取资源列表")

            # 列出可用提示
            prompts = await session.list_prompts()
            print("\n可用提示:")
            if hasattr(prompts, 'prompts'):
                for prompt in prompts.prompts:
                    print(f"- {prompt.name}: {prompt.description}")
            else:
                print("无法获取提示列表")

            # 测试工具
            print("\n测试 list_directory 工具...")
            try:
                result = await session.call_tool("list_directory", {"path": os.getcwd()})
                print(result)
            except Exception as e:
                print(f"调用工具时出错: {e}")

            # 测试资源
            print("\n测试 system://info 资源...")
            try:
                content, mime_type = await session.read_resource("system://info")
                print(f"MIME类型: {mime_type}")
                print(content[:200] + "..." if len(content) > 200 else content)
            except Exception as e:
                print(f"读取资源时出错: {e}")

            print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(run()) 