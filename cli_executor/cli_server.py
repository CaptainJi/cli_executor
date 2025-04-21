"""
CLI Executor MCP Server

这个MCP服务器提供了执行CLI命令的工具，用于系统部署和管理。
"""

import asyncio
import subprocess
import os
import sys
import argparse
import time
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP

# 定义工具、资源和提示函数，稍后将它们注册到FastMCP实例
async def execute_command_tool(command: str, working_dir: Optional[str] = None) -> str:
    """执行CLI命令并返回结果
       如果命令比较危险例如rm -rf，请先进行确认
       如果命令因处理时间过长而超时，请使用nohup运行命令，并使用tail -f nohup.out查看结果直至命令执行完毕
    """
    try:
        # 设置工作目录
        cwd = working_dir if working_dir else os.getcwd()
        
        # 获取当前用户的默认shell
        import pwd
        import subprocess
        current_user = pwd.getpwuid(os.getuid()).pw_name
        shell_info = subprocess.run(['getent', 'passwd', current_user], capture_output=True, text=True)
        shell = shell_info.stdout.split(':')[-1].strip()
        
        # 构建加载环境变量的命令
        if 'zsh' in shell:
            env_cmd = f'source /etc/zsh/zshenv; source ~/.zshenv; source ~/.zshrc; {command}'
        elif 'bash' in shell:
            env_cmd = f'source /etc/profile; source ~/.bashrc; {command}'
        elif 'sh' in shell:
            env_cmd = f'. /etc/profile; . ~/.profile; {command}'
        else:
            env_cmd = command
        
        # 使用asyncio创建子进程
        process = await asyncio.create_subprocess_shell(
            env_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            shell=True,
            env=os.environ.copy()  # 确保继承当前环境变量
        )
        
        # 获取输出
        stdout, stderr = await process.communicate()
        
        # 直接返回原始输出，包括stdout和stderr
        output = ""
        if stdout:
            output += stdout.decode('utf-8', errors='replace')
        if stderr:
            output += stderr.decode('utf-8', errors='replace')
            
        return output if output else "命令执行完成，但没有任何输出"
            
    except Exception as e:
        return f"执行命令时出错: {str(e)}"

async def execute_script_tool(script: str, working_dir: Optional[str] = None) -> str:
    """执行一个多行脚本并返回结果"""
    try:
        import platform
        
        # 设置工作目录
        cwd = working_dir if working_dir else os.getcwd()
        
        # 根据操作系统创建临时脚本文件
        is_windows = platform.system() == "Windows"
        if is_windows:
            script_path = os.path.join(cwd, "temp_script.bat")
            with open(script_path, "w") as f:
                f.write("@echo off\n")  # Windows批处理文件头
                f.write(script)
        else:
            script_path = os.path.join(cwd, "temp_script.sh")
            with open(script_path, "w") as f:
                f.write("#!/bin/bash\nset -e\n")  # 添加shebang和错误时退出
                f.write(script)
        
        # 设置执行权限（仅在非Windows系统上需要）
        if not is_windows:
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
        try:
            os.remove(script_path)
        except Exception:
            pass  # 忽略删除临时文件的错误
        
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
        import platform
        
        # 获取系统信息
        result = "系统信息:\n"
        
        # 使用platform模块获取系统信息（跨平台兼容）
        result += f"系统名称: {platform.system()}\n"
        result += f"主机名: {platform.node()}\n"
        result += f"发行版本: {platform.release()}\n"
        result += f"版本: {platform.version()}\n"
        result += f"机器类型: {platform.machine()}\n"
        
        # 如果是类Unix系统，尝试获取更详细的信息
        if platform.system() != "Windows":
            try:
                uname = os.uname()
                result += f"系统详细信息: {uname.version}\n"
            except AttributeError:
                pass
        
        # 获取Python版本
        python_version = sys.version
        result += f"Python版本: {python_version}\n"
        
        # 获取环境变量
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("_")}
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
如果命令比较危险例如rm -rf，请先进行确认
如果命令因处理时间过长而超时，请使用nohup运行命令，并使用tail -f nohup.out查看结果直至命令执行完毕
"""

def create_mcp_server(server_settings=None):
    """创建并配置MCP服务器实例"""
    # 创建MCP服务器实例
    settings = {
        "initialization_timeout": 60.0,  # 增加初始化超时时间到60秒
        "request_queue_size": 100,  # 增加请求队列大小
        "session_timeout": 300.0,  # 会话超时时间设置为5分钟
        "host": "0.0.0.0",  # 默认监听所有网络接口
        "port": 8000,  # 默认端口
        "transport": "sse",  # 默认使用SSE传输
    }
    if server_settings:
        settings.update(server_settings)
    
    mcp_server = FastMCP("CLI Executor", **settings)
    
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

async def wait_for_initialization(mcp_server, timeout=60):
    """等待服务器初始化完成"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if hasattr(mcp_server, "_initialized") and mcp_server._initialized:
            return True
        await asyncio.sleep(0.5)
    return False

def run_with_initialization_check(mcp_server, transport="sse", timeout=60):
    """运行服务器并等待初始化完成"""
    # 创建一个事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 创建一个任务来运行服务器
    server_task = loop.create_task(mcp_server.run(transport=transport))
    
    # 创建一个任务来等待初始化
    init_task = loop.create_task(wait_for_initialization(mcp_server, timeout))
    
    try:
        # 运行直到初始化完成或超时
        init_result = loop.run_until_complete(init_task)
        if not init_result:
            print(f"警告: 服务器初始化超时 ({timeout}秒)，但将继续运行")
        
        # 继续运行服务器任务
        loop.run_until_complete(server_task)
    except KeyboardInterrupt:
        print("接收到中断信号，正在关闭服务器...")
    finally:
        # 清理任务
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True))
        loop.close()

def main():
    # 从环境变量获取默认值
    default_port = int(os.environ.get("CLI_EXECUTOR_PORT", "8000"))
    default_host = os.environ.get("CLI_EXECUTOR_HOST", "0.0.0.0")
    default_transport = os.environ.get("CLI_EXECUTOR_TRANSPORT", "sse")
    default_debug = os.environ.get("CLI_EXECUTOR_DEBUG", "").lower() in ("true", "1", "yes")
    default_max_retries = int(os.environ.get("CLI_EXECUTOR_MAX_RETRIES", "3"))
    
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
    parser.add_argument("--max-retries", type=int, default=default_max_retries,
                        help=f"服务器启动失败时的最大重试次数 (默认: {default_max_retries})")
    
    args = parser.parse_args()
    
    # 设置调试模式
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # 运行MCP服务器
    retry_count = 0
    while retry_count < args.max_retries:
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
                
                # 运行服务器
                run_with_initialization_check(mcp_server, transport="sse")
            else:
                print("启动stdio服务器...")
                # 创建并配置MCP服务器（使用默认设置）
                mcp_server = create_mcp_server()
                run_with_initialization_check(mcp_server, transport="stdio")
            break  # 如果成功启动，跳出循环
        except Exception as e:
            retry_count += 1
            print(f"启动服务器时出错 (尝试 {retry_count}/{args.max_retries}): {e}")
            if retry_count >= args.max_retries:
                print("达到最大重试次数，服务器启动失败")
                sys.exit(1)
            time.sleep(1)  # 等待1秒后重试

if __name__ == "__main__":
    main() 