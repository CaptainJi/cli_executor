"""
CLI Executor MCP Server

这个MCP服务器提供了执行CLI命令的工具，用于系统部署和管理。
"""

import asyncio
import subprocess
import os
import sys
import argparse
from typing import Optional
from mcp.server.fastmcp import FastMCP

# 定义工具、资源和提示函数，稍后将它们注册到FastMCP实例
async def execute_command_tool(command: str, working_dir: Optional[str] = None) -> str:
    """执行CLI命令并返回结果"""
    try:
        # 设置工作目录
        cwd = working_dir if working_dir else os.getcwd()
        
        # 使用asyncio创建子进程
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            shell=True
        )
        
        # 获取输出
        stdout, stderr = await process.communicate()
        
        # 返回结果
        if process.returncode == 0:
            return f"命令执行成功:\n{stdout.decode('utf-8', errors='replace')}"
        else:
            return f"命令执行失败 (返回码: {process.returncode}):\n{stderr.decode('utf-8', errors='replace')}"
    except Exception as e:
        return f"执行命令时出错: {str(e)}"

async def execute_script_tool(script: str, working_dir: Optional[str] = None) -> str:
    """执行一个多行脚本并返回结果"""
    try:
        # 设置工作目录
        cwd = working_dir if working_dir else os.getcwd()
        
        # 创建临时脚本文件
        script_path = os.path.join(cwd, "temp_script.sh")
        with open(script_path, "w") as f:
            f.write("#!/bin/bash\nset -e\n")  # 添加shebang和错误时退出
            f.write(script)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        # 执行脚本
        process = await asyncio.create_subprocess_shell(
            script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            shell=True
        )
        
        # 获取输出
        stdout, stderr = await process.communicate()
        
        # 删除临时脚本
        os.remove(script_path)
        
        # 返回结果
        if process.returncode == 0:
            return f"脚本执行成功:\n{stdout.decode('utf-8', errors='replace')}"
        else:
            return f"脚本执行失败 (返回码: {process.returncode}):\n{stderr.decode('utf-8', errors='replace')}"
    except Exception as e:
        return f"执行脚本时出错: {str(e)}"

def list_directory_tool(path: Optional[str] = None) -> str:
    """列出指定目录的内容"""
    try:
        # 设置目录路径
        dir_path = path if path else os.getcwd()
        
        # 获取目录内容
        items = os.listdir(dir_path)
        
        # 格式化输出
        result = f"目录 {dir_path} 的内容:\n"
        for item in items:
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                result += f"[目录] {item}\n"
            else:
                size = os.path.getsize(item_path)
                result += f"[文件] {item} ({size} 字节)\n"
        
        return result
    except Exception as e:
        return f"列出目录内容时出错: {str(e)}"

def get_system_info_resource() -> str:
    """获取系统信息"""
    try:
        # 获取系统信息
        uname = os.uname()
        
        # 获取Python版本
        python_version = sys.version
        
        # 获取环境变量
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("_")}
        
        # 格式化输出
        result = "系统信息:\n"
        result += f"系统名称: {uname.sysname}\n"
        result += f"主机名: {uname.nodename}\n"
        result += f"发行版本: {uname.release}\n"
        result += f"版本: {uname.version}\n"
        result += f"机器类型: {uname.machine}\n"
        result += f"Python版本: {python_version}\n"
        result += "\n环境变量:\n"
        for k, v in env_vars.items():
            result += f"{k}={v}\n"
        
        return result
    except Exception as e:
        return f"获取系统信息时出错: {str(e)}"

def deploy_app_prompt(app_name: str, target_dir: str) -> str:
    """创建一个部署应用的提示"""
    return f"""
我需要部署应用 {app_name} 到 {target_dir} 目录。

请帮我完成以下任务：
1. 检查目标目录是否存在，如果不存在则创建
2. 克隆应用代码库
3. 安装依赖
4. 配置应用
5. 启动应用

请使用CLI命令执行这些任务。
"""

def create_mcp_server(server_settings=None):
    """创建并配置MCP服务器实例"""
    # 创建MCP服务器实例
    mcp_server = FastMCP("CLI Executor", **(server_settings or {}))
    
    # 注册工具
    mcp_server.add_tool(execute_command_tool, name="execute_command", 
                        description="执行CLI命令并返回结果")
    mcp_server.add_tool(execute_script_tool, name="execute_script", 
                        description="执行一个多行脚本并返回结果")
    mcp_server.add_tool(list_directory_tool, name="list_directory", 
                        description="列出指定目录的内容")
    
    # 注册资源
    mcp_server.resource("system://info")(get_system_info_resource)
    
    # 注册提示
    mcp_server.prompt()(deploy_app_prompt)
    
    return mcp_server

def main():
    # 从环境变量获取默认值
    default_port = int(os.environ.get("CLI_EXECUTOR_PORT", "8000"))
    default_host = os.environ.get("CLI_EXECUTOR_HOST", "0.0.0.0")
    default_transport = os.environ.get("CLI_EXECUTOR_TRANSPORT", "sse")
    default_debug = os.environ.get("CLI_EXECUTOR_DEBUG", "").lower() in ("true", "1", "yes")
    
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="CLI Executor MCP Server")
    parser.add_argument("--transport", type=str, default=default_transport, choices=["stdio", "sse"], 
                        help=f"传输类型: stdio 或 sse (默认: {default_transport})")
    parser.add_argument("--debug", action="store_true", default=default_debug,
                        help="启用调试模式")
    parser.add_argument("--port", type=int, default=default_port,
                        help=f"SSE服务器端口号 (默认: {default_port})")
    parser.add_argument("--host", type=str, default=default_host,
                        help=f"SSE服务器主机地址 (默认: {default_host})")
    
    args = parser.parse_args()
    
    # 设置调试模式
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # 运行MCP服务器
    try:
        if args.transport == "sse":
            print(f"启动SSE服务器，监听地址: {args.host}:{args.port}...")
            # 创建带有自定义设置的FastMCP实例
            server_settings = {
                "host": args.host,
                "port": args.port,
                "debug": args.debug,
                "log_level": "DEBUG" if args.debug else "INFO"
            }
            # 创建并配置MCP服务器
            mcp_server = create_mcp_server(server_settings)
            
            # 启动SSE服务器
            mcp_server.run(transport="sse")
        else:
            print("启动stdio服务器...")
            # 创建并配置MCP服务器（使用默认设置）
            mcp_server = create_mcp_server()
            mcp_server.run(transport="stdio")
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 