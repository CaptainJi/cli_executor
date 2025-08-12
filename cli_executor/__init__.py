"""
CLI Executor MCP - 用于执行CLI命令的MCP服务器

这个包提供了一个模型上下文协议(MCP)服务器，使大语言模型能够
执行CLI命令进行系统部署和管理任务。
"""

__version__ = "1.0.0"
__author__ = "CaptainJi"
__email__ = "jiqing19861123@163.com"

from .server import mcp

__all__ = ["mcp"]