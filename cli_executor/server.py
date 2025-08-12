"""
基于FastMCP的CLI执行器MCP服务器

一个模型上下文协议服务器，使大语言模型能够执行CLI命令
进行系统部署和管理任务。
"""

import asyncio
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

try:
    import pwd
except ImportError:
    # Windows doesn't have pwd module
    pwd = None

import fastmcp

# 创建FastMCP服务器实例
mcp = fastmcp.FastMCP(
    "CLI Executor",
    version="1.0.0"
)


@mcp.tool()
async def execute_command(
    command: str,
    working_dir: Optional[str] = None,
    timeout: int = 30
) -> str:
    """
    执行CLI命令并返回结果。
    
    参数:
        command: 要执行的命令
        working_dir: 命令执行的工作目录（可选）
        timeout: 命令超时时间（秒，默认：30）
    
    返回:
        命令输出，包括stdout和stderr
        
    注意:
        - 对于危险命令如'rm -rf'，请在执行前确认
        - 对于长时间运行的命令，使用'nohup'并用'tail -f'监控
    """
    # 尝试导入loguru用于调试日志
    try:
        from loguru import logger
        debug_enabled = True
    except ImportError:
        debug_enabled = False
    
    if debug_enabled:
        logger.debug(f"🔧 开始执行命令: {command}")
        logger.debug(f"📁 工作目录: {working_dir or '当前目录'}")
        logger.debug(f"⏱️ 超时时间: {timeout}秒")
    
    try:
        # 设置工作目录
        cwd = Path(working_dir) if working_dir else Path.cwd()
        if not cwd.exists():
            return f"错误：工作目录 '{cwd}' 不存在"
        
        # 获取用户默认shell并构建环境加载命令
        try:
            if pwd and hasattr(os, 'getuid'):
                # Unix-like系统
                current_user = pwd.getpwuid(os.getuid()).pw_name
                shell_info = subprocess.run(
                    ['getent', 'passwd', current_user], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                shell = shell_info.stdout.split(':')[-1].strip()
            else:
                # Windows系统
                shell = os.environ.get('COMSPEC', 'cmd.exe')
        except Exception:
            # 回退到环境变量
            if platform.system() == "Windows":
                shell = os.environ.get('COMSPEC', 'cmd.exe')
            else:
                shell = os.environ.get('SHELL', '/bin/bash')
        
        # 根据shell类型构建环境加载命令
        if platform.system() == "Windows":
            # Windows系统直接执行命令
            env_cmd = command
        elif 'zsh' in shell:
            env_cmd = f'source /etc/zsh/zshenv 2>/dev/null; source ~/.zshenv 2>/dev/null; source ~/.zshrc 2>/dev/null; {command}'
        elif 'bash' in shell:
            env_cmd = f'source /etc/profile 2>/dev/null; source ~/.bashrc 2>/dev/null; {command}'
        elif 'sh' in shell:
            env_cmd = f'. /etc/profile 2>/dev/null; . ~/.profile 2>/dev/null; {command}'
        else:
            env_cmd = command
        
        if debug_enabled:
            logger.debug(f"🚀 执行命令: {env_cmd}")
            logger.debug(f"📂 工作目录: {cwd}")
        
        # 执行命令并设置超时
        process = await asyncio.create_subprocess_shell(
            env_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd),
            env=os.environ.copy()
        )
        
        if debug_enabled:
            logger.debug(f"⏳ 等待命令执行完成，超时时间: {timeout}秒")
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            if debug_enabled:
                logger.debug(f"✅ 命令执行完成，退出码: {process.returncode}")
                if stdout:
                    logger.debug(f"📤 标准输出长度: {len(stdout)} 字节")
                if stderr:
                    logger.debug(f"📤 错误输出长度: {len(stderr)} 字节")
                    
        except asyncio.TimeoutError:
            if debug_enabled:
                logger.warning(f"⏰ 命令执行超时 ({timeout}秒)，强制终止进程")
            process.kill()
            await process.wait()
            return f"命令在 {timeout} 秒后超时。对于长时间运行的命令，请考虑使用 'nohup'。"
        
        # 格式化输出
        output_parts = []
        if stdout:
            if debug_enabled:
                logger.debug(f"🔍 开始解码标准输出，原始长度: {len(stdout)} 字节")
            
            # 尝试多种编码方式
            decoded_stdout = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                try:
                    decoded_stdout = stdout.decode(encoding).strip()
                    if debug_enabled:
                        logger.debug(f"✅ 使用编码 {encoding} 成功解码标准输出")
                    break
                except UnicodeDecodeError:
                    if debug_enabled:
                        logger.debug(f"❌ 编码 {encoding} 解码失败，尝试下一个")
                    continue
            
            if decoded_stdout is None:
                decoded_stdout = stdout.decode('utf-8', errors='replace').strip()
                if debug_enabled:
                    logger.warning(f"⚠️ 所有编码都失败，使用replace模式解码")
            
            if decoded_stdout:
                if debug_enabled:
                    logger.debug(f"📝 标准输出内容: {decoded_stdout[:100]}{'...' if len(decoded_stdout) > 100 else ''}")
                output_parts.append(f"标准输出:\n{decoded_stdout}")
        
        if stderr:
            if debug_enabled:
                logger.debug(f"🔍 开始解码错误输出，原始长度: {len(stderr)} 字节")
            
            # 尝试多种编码方式
            decoded_stderr = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                try:
                    decoded_stderr = stderr.decode(encoding).strip()
                    if debug_enabled:
                        logger.debug(f"✅ 使用编码 {encoding} 成功解码错误输出")
                    break
                except UnicodeDecodeError:
                    if debug_enabled:
                        logger.debug(f"❌ 编码 {encoding} 解码失败，尝试下一个")
                    continue
            
            if decoded_stderr is None:
                decoded_stderr = stderr.decode('utf-8', errors='replace').strip()
                if debug_enabled:
                    logger.warning(f"⚠️ 所有编码都失败，使用replace模式解码")
            
            if decoded_stderr:
                if debug_enabled:
                    logger.debug(f"📝 错误输出内容: {decoded_stderr[:100]}{'...' if len(decoded_stderr) > 100 else ''}")
                output_parts.append(f"错误输出:\n{decoded_stderr}")
        
        if not output_parts:
            if debug_enabled:
                logger.debug(f"✅ 命令执行成功，无输出内容，退出码: {process.returncode}")
            return f"命令执行成功 (退出码: {process.returncode})"
        
        result = "\n\n".join(output_parts)
        if process.returncode != 0:
            result = f"命令执行失败 (退出码: {process.returncode})\n\n{result}"
        
        if debug_enabled:
            logger.debug(f"🎯 命令执行完成，返回结果长度: {len(result)} 字符")
        
        return result
        
    except Exception as e:
        return f"执行命令时出错: {str(e)}"


@mcp.tool()
async def execute_script(
    script: str,
    working_dir: Optional[str] = None,
    shell: str = "bash",
    timeout: int = 60
) -> str:
    """
    执行多行脚本并返回结果。
    
    参数:
        script: 要执行的脚本内容
        working_dir: 脚本执行的工作目录（可选）
        shell: 使用的shell（bash, sh, zsh等）
        timeout: 脚本超时时间（秒，默认：60）
    
    返回:
        脚本执行输出
    """
    # 尝试导入loguru用于调试日志
    try:
        from loguru import logger
        debug_enabled = True
    except ImportError:
        debug_enabled = False
    
    if debug_enabled:
        logger.debug(f"🔧 开始执行脚本")
        logger.debug(f"📁 工作目录: {working_dir or '当前目录'}")
        logger.debug(f"🐚 使用shell: {shell}")
        logger.debug(f"⏱️ 超时时间: {timeout}秒")
        logger.debug(f"📝 脚本内容: {script[:100]}{'...' if len(script) > 100 else ''}")
    
    try:
        # 设置工作目录
        cwd = Path(working_dir) if working_dir else Path.cwd()
        if not cwd.exists():
            return f"错误：工作目录 '{cwd}' 不存在"
        
        # 确定脚本扩展名和头部
        is_windows = platform.system() == "Windows"
        if is_windows:
            script_ext = ".bat"
            script_header = "@echo off\n"
        else:
            script_ext = ".sh"
            script_header = f"#!/bin/{shell}\nset -e\n"
        
        # 创建临时脚本文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=script_ext,
            dir=str(cwd),
            delete=False
        ) as temp_file:
            temp_file.write(script_header + script)
            script_path = temp_file.name
        
        try:
            # 在类Unix系统上设置执行权限
            if not is_windows:
                os.chmod(script_path, 0o755)
            
            # 执行脚本
            if is_windows:
                cmd = script_path
            else:
                cmd = f"{shell} {script_path}"
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return f"脚本在 {timeout} 秒后超时"
            
            # 格式化输出
            output_parts = []
            if stdout:
                # 尝试多种编码方式
                decoded_stdout = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                    try:
                        decoded_stdout = stdout.decode(encoding).strip()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if decoded_stdout is None:
                    decoded_stdout = stdout.decode('utf-8', errors='replace').strip()
                
                if decoded_stdout:
                    output_parts.append(f"标准输出:\n{decoded_stdout}")
            
            if stderr:
                # 尝试多种编码方式
                decoded_stderr = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                    try:
                        decoded_stderr = stderr.decode(encoding).strip()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if decoded_stderr is None:
                    decoded_stderr = stderr.decode('utf-8', errors='replace').strip()
                
                if decoded_stderr:
                    output_parts.append(f"错误输出:\n{decoded_stderr}")
            
            if not output_parts:
                status = "成功" if process.returncode == 0 else "失败"
                return f"脚本执行{status} (退出码: {process.returncode})"
            
            result = "\n\n".join(output_parts)
            if process.returncode != 0:
                result = f"脚本执行失败 (退出码: {process.returncode})\n\n{result}"
            else:
                result = f"脚本执行成功\n\n{result}"
            
            return result
            
        finally:
            # 清理临时脚本文件
            try:
                os.unlink(script_path)
            except Exception:
                pass  # 忽略清理错误
                
    except Exception as e:
        return f"执行脚本时出错: {str(e)}"


@mcp.tool()
def list_directory(path: Optional[str] = None, show_hidden: bool = False) -> str:
    """
    列出目录内容，区分文件和文件夹。
    
    参数:
        path: 要列出的目录路径（默认为当前目录）
        show_hidden: 是否显示隐藏文件和目录
    
    返回:
        格式化的目录列表
    """
    # 尝试导入loguru用于调试日志
    try:
        from loguru import logger
        debug_enabled = True
    except ImportError:
        debug_enabled = False
    
    if debug_enabled:
        logger.debug(f"🔧 开始列出目录")
        logger.debug(f"📁 目录路径: {path or '当前目录'}")
        logger.debug(f"👁️ 显示隐藏文件: {show_hidden}")
    
    try:
        # 设置目录路径
        dir_path = Path(path) if path else Path.cwd()
        
        if not dir_path.exists():
            return f"错误：目录 '{dir_path}' 不存在"
        
        if not dir_path.is_dir():
            return f"错误：'{dir_path}' 不是一个目录"
        
        # 获取目录内容
        try:
            items = list(dir_path.iterdir())
        except PermissionError:
            return f"错误：访问 '{dir_path}' 权限被拒绝"
        
        # 如果需要，过滤隐藏文件
        if not show_hidden:
            items = [item for item in items if not item.name.startswith('.')]
        
        # 排序：目录在前，然后是文件
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        # 格式化输出
        result = f"目录 '{dir_path}' 的内容 ({len(items)} 项):\n\n"
        
        if not items:
            result += "目录为空"
            return result
        
        for item in items:
            try:
                if item.is_dir():
                    result += f"📁 [目录]  {item.name}/\n"
                elif item.is_file():
                    size = item.stat().st_size
                    size_str = _format_file_size(size)
                    result += f"📄 [文件] {item.name} ({size_str})\n"
                elif item.is_symlink():
                    target = item.readlink()
                    result += f"🔗 [链接] {item.name} -> {target}\n"
                else:
                    result += f"❓ [其他] {item.name}\n"
            except (OSError, PermissionError):
                result += f"❌ [错误] {item.name} (权限被拒绝)\n"
        
        return result
        
    except Exception as e:
        return f"列出目录时出错: {str(e)}"


def _format_file_size(size_bytes: int) -> str:
    """将文件大小格式化为人类可读的格式。"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


@mcp.resource("system://info")
def get_system_info() -> str:
    """获取全面的系统信息。"""
    try:
        info_parts = []
        
        # 基本系统信息
        info_parts.append("=== 系统信息 ===")
        info_parts.append(f"系统: {platform.system()}")
        info_parts.append(f"主机名: {platform.node()}")
        info_parts.append(f"发行版: {platform.release()}")
        info_parts.append(f"版本: {platform.version()}")
        info_parts.append(f"架构: {platform.machine()}")
        info_parts.append(f"处理器: {platform.processor()}")
        
        # Python信息
        info_parts.append("\n=== PYTHON信息 ===")
        info_parts.append(f"Python版本: {sys.version}")
        info_parts.append(f"Python可执行文件: {sys.executable}")
        
        # 当前工作环境
        info_parts.append(f"\n=== 当前环境 ===")
        info_parts.append(f"工作目录: {os.getcwd()}")
        info_parts.append(f"用户: {os.environ.get('USER', '未知')}")
        info_parts.append(f"主目录: {os.environ.get('HOME', '未知')}")
        info_parts.append(f"Shell: {os.environ.get('SHELL', '未知')}")
        
        # 关键环境变量
        info_parts.append("\n=== 关键环境变量 ===")
        key_vars = ['PATH', 'PYTHONPATH', 'LANG', 'LC_ALL', 'TERM']
        for var in key_vars:
            value = os.environ.get(var, '未设置')
            info_parts.append(f"{var}: {value}")
        
        return "\n".join(info_parts)
        
    except Exception as e:
        return f"获取系统信息时出错: {str(e)}"


@mcp.prompt()
def deploy_application(app_name: str, target_dir: str, repo_url: Optional[str] = None) -> str:
    """
    为应用程序生成部署提示。
    
    参数:
        app_name: 要部署的应用程序名称
        target_dir: 部署目标目录
        repo_url: Git仓库URL（可选）
    
    返回:
        部署指令提示
    """
    prompt = f"""
# 应用程序部署指南: {app_name}

我需要将应用程序 **{app_name}** 部署到目录 `{target_dir}`。

## 部署步骤:

1. **准备目标目录**
   - 检查 `{target_dir}` 是否存在
   - 如果不存在则创建目录
   - 设置适当的权限

2. **源代码管理**"""
    
    if repo_url:
        prompt += f"""
   - 从以下地址克隆仓库: `{repo_url}`
   - 如需要，切换到适当的分支"""
    else:
        prompt += """
   - 将源代码复制到目标目录
   - 或从仓库克隆（请提供URL）"""
    
    prompt += f"""

3. **依赖安装**
   - 检查包管理器文件 (package.json, requirements.txt, Gemfile等)
   - 使用适当的包管理器安装依赖
   - 如需要，处理虚拟环境

4. **配置**
   - 复制/创建配置文件
   - 设置环境变量
   - 如需要，配置数据库连接

5. **应用程序设置**
   - 如需要，运行构建过程
   - 设置数据库迁移
   - 创建必要的目录和文件

6. **服务管理**
   - 启动应用程序
   - 配置进程管理 (systemd, pm2等)
   - 设置监控和日志记录

## 安全注意事项:
- ⚠️  运行破坏性命令如 `rm -rf` 前请务必确认
- ⏱️  对于长时间运行的命令，使用 `nohup` 并用 `tail -f` 监控
- 🔒  部署后验证权限和所有权
- 📋  标记完成前测试部署

请使用可用的CLI工具执行这些步骤，并在进行下一步之前确认每一步。
"""
    
    return prompt


def main():
    """CLI Executor MCP服务器的主入口点。"""
    import argparse
    import sys  # 确保sys模块始终可用
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="CLI Executor MCP服务器 - 通过MCP执行CLI命令",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 使用streamable-http传输运行
  %(prog)s --transport stdio        # 使用stdio传输运行
  %(prog)s --port 9000              # 在端口9000运行streamable-http服务器
  %(prog)s --debug                  # 启用调试日志运行
        """
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="streamable-http",
        help="使用的传输协议 (默认: streamable-http)"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP服务器绑定的主机 (默认: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP服务器端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试日志"
    )
    
    args = parser.parse_args()
    
    # 配置日志
    if args.debug:
        try:
            from loguru import logger
            import sys
            import os
            
            # 移除默认的日志处理器
            logger.remove()
            
            # 添加自定义的日志处理器，支持中文和转义字符
            logger.add(
                sys.stderr,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                level="DEBUG",
                colorize=True,
                backtrace=True,
                diagnose=True,
                enqueue=True,
                catch=True
            )
            
            # 设置环境变量以确保正确的编码
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            
            # 只使用loguru，不替换标准logging，避免与uvicorn冲突
            logger.info("🔧 调试模式已启用，使用loguru进行日志记录")
            logger.info("📝 日志将显示可读的中文字符和正确格式")
            logger.info("🎨 支持彩色输出和结构化日志")
            
        except ImportError:
            # 如果loguru不可用，回退到标准logging
            import logging
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            print("⚠️  loguru未安装，使用标准logging。建议安装loguru: pip install loguru", file=sys.stderr)
    
    # 运行服务器
    try:
        if args.transport == "stdio":
            print("正在启动CLI Executor MCP服务器，使用stdio传输...", file=sys.stderr)
            mcp.run(transport="stdio")
        else:
            print(f"正在启动CLI Executor MCP服务器，地址: {args.host}:{args.port}...", file=sys.stderr)
            mcp.run(
                transport=args.transport,
                host=args.host,
                port=args.port
            )
    except KeyboardInterrupt:
        print("\n服务器被用户停止", file=sys.stderr)
    except Exception as e:
        print(f"启动服务器时出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()