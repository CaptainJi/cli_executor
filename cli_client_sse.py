"""
CLI Executor MCP Client (SSE)

这个脚本用于通过SSE连接CLI Executor MCP服务器并测试其功能。
"""

import asyncio
import os
import traceback
from mcp import ClientSession
from mcp.client.sse import sse_client

# SSE服务器URL
SSE_URL = "http://localhost:8000/sse"

async def run():
    print(f"正在通过SSE连接到CLI Executor MCP服务器 ({SSE_URL})...")
    try:
        # 添加超时设置
        print("尝试建立SSE连接...")
        try:
            async with sse_client(SSE_URL) as (read, write):
                print("SSE连接已建立，正在创建客户端会话...")
                try:
                    async with ClientSession(read, write) as session:
                        # 初始化连接
                        print("正在初始化会话...")
                        await session.initialize()
                        print("连接成功！")

                        # 列出可用工具
                        print("正在获取工具列表...")
                        tools = await session.list_tools()
                        print("\n可用工具:")
                        if hasattr(tools, 'tools'):
                            for tool in tools.tools:
                                print(f"- {tool.name}: {tool.description}")
                        else:
                            print("无法获取工具列表")

                        # 列出可用资源
                        print("\n正在获取资源列表...")
                        resources = await session.list_resources()
                        print("\n可用资源:")
                        if hasattr(resources, 'resources'):
                            for resource in resources.resources:
                                print(f"- {resource}")
                        else:
                            print("无法获取资源列表")

                        # 列出可用提示
                        print("\n正在获取提示列表...")
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
                            print(f"错误详情: {traceback.format_exc()}")

                        # 测试资源
                        print("\n测试 system://info 资源...")
                        try:
                            content, mime_type = await session.read_resource("system://info")
                            print(f"MIME类型: {mime_type}")
                            print(content[:200] + "..." if len(content) > 200 else content)
                        except Exception as e:
                            print(f"读取资源时出错: {e}")
                            print(f"错误详情: {traceback.format_exc()}")

                        print("\n测试完成！")
                except Exception as e:
                    print(f"创建客户端会话时出错: {e}")
                    print(f"错误详情: {traceback.format_exc()}")
        except Exception as e:
            print(f"建立SSE连接时出错: {e}")
            print(f"错误详情: {traceback.format_exc()}")
    except Exception as e:
        print(f"连接到SSE服务器时出错: {e}")
        print(f"错误详情: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(run()) 