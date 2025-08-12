#!/usr/bin/env python3
"""
使用FastMCP客户端的CLI Executor MCP服务器示例。

这个示例演示了如何使用FastMCP客户端库以编程方式
连接和使用CLI Executor MCP服务器。
"""

import asyncio
import fastmcp


async def main():
    """演示CLI Executor MCP使用的主示例函数。"""
    
    # 创建到CLI Executor MCP服务器的客户端连接
    # 使用stdio传输和cli-executor-mcp命令
    client = fastmcp.Client(
        transport="stdio",
        command="cli-executor-mcp",
        args=["--transport", "stdio"]
    )
    
    try:
        # 初始化客户端连接
        await client.initialize()
        
        print("🚀 已连接到CLI Executor MCP服务器！")
        print("=" * 50)
        
        # 示例1：执行简单命令
        print("\n📋 示例1：执行简单命令")
        result = await client.call_tool("execute_command", {
            "command": "echo 'Hello from CLI Executor MCP!'"
        })
        print(f"结果: {result}")
        
        # 示例2：列出目录内容
        print("\n📁 示例2：列出目录内容")
        result = await client.call_tool("list_directory", {
            "path": ".",
            "show_hidden": False
        })
        print(f"目录列表:\n{result}")
        
        # 示例3：执行多行脚本
        print("\n📜 示例3：执行多行脚本")
        script = """
        echo "正在创建测试目录..."
        mkdir -p /tmp/mcp_test
        cd /tmp/mcp_test
        echo "Hello World!" > test.txt
        echo "文件已创建:"
        ls -la test.txt
        cat test.txt
        """
        
        result = await client.call_tool("execute_script", {
            "script": script,
            "shell": "bash",
            "timeout": 30
        })
        print(f"脚本结果:\n{result}")
        
        # 示例4：获取系统信息
        print("\n🖥️ 示例4：获取系统信息")
        system_info = await client.read_resource("system://info")
        print(f"系统信息:\n{system_info}")
        
        # 示例5：生成部署提示
        print("\n📋 示例5：生成部署提示")
        prompt = await client.get_prompt("deploy_application", {
            "app_name": "my-web-app",
            "target_dir": "/var/www/my-web-app",
            "repo_url": "https://github.com/user/my-web-app.git"
        })
        print(f"部署提示:\n{prompt}")
        
        # 示例6：执行Python命令
        print("\n🐍 示例6：执行Python命令")
        result = await client.call_tool("execute_command", {
            "command": "python3 -c \"import sys; print(f'Python version: {sys.version}')\"",
            "timeout": 10
        })
        print(f"Python版本: {result}")
        
        print("\n✅ 所有示例都成功完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    finally:
        # 清理客户端连接
        await client.close()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())