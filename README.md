# CLI Executor MCP

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.11+-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

基于FastMCP构建的模型上下文协议(MCP)服务器，使大语言模型能够执行CLI命令进行系统部署和管理任务。

## ✨ 功能特性

- 🚀 **FastMCP实现** - 基于FastMCP框架构建
- 🔧 **命令执行** - 执行单个CLI命令，支持环境变量加载
- 📜 **脚本执行** - 运行多行脚本，支持超时控制
- 📁 **目录操作** - 列出目录内容，显示详细文件信息
- 🖥️ **系统信息** - 全面的系统和环境详情
- 📋 **部署模板** - 即用型部署提示模板
- ⚡ **多种传输方式** - 支持stdio和streamable-HTTP
- 🛡️ **安全特性** - 超时处理和错误管理
- 🔍 **跨平台** - 支持Linux、macOS和Windows

## 📦 安装

```bash
pip install cli-executor-mcp
```

## 🚀 快速开始

### 启动服务器

#### Stdio传输（默认）
```bash
cli-executor-mcp
```

#### Streamable HTTP传输
```bash
cli-executor-mcp --port 8000
```

#### 指定主机和端口
```bash
cli-executor-mcp --host 0.0.0.0 --port 8000
```

#### 调试模式
```bash
cli-executor-mcp --debug
```

### 与MCP客户端配合使用

服务器提供的工具、资源和提示可以被任何兼容MCP的客户端使用：

```python
import fastmcp

# 连接到服务器
client = fastmcp.Client("stdio", command="cli-executor-mcp")

# 执行命令
result = await client.call_tool("execute_command", {"command": "ls -la"})
print(result)
```

## 🛠️ 可用工具

### `execute_command`
执行单个CLI命令，支持环境变量加载。

**参数：**
- `command` (str): 要执行的命令
- `working_dir` (str, 可选): 执行目录
- `timeout` (int, 可选): 命令超时时间（秒，默认：30）

**示例：**
```python
await client.call_tool("execute_command", {
    "command": "python --version",
    "working_dir": "/home/user/project"
})
```

### `execute_script`
执行多行脚本，支持适当的shell处理。

**参数：**
- `script` (str): 要执行的脚本内容
- `working_dir` (str, 可选): 执行目录
- `shell` (str, 可选): 使用的shell（默认："bash"）
- `timeout` (int, 可选): 脚本超时时间（秒，默认：60）

**示例：**
```python
await client.call_tool("execute_script", {
    "script": """
    #!/bin/bash
    echo "开始部署..."
    npm install
    npm run build
    echo "部署完成！"
    """,
    "working_dir": "/var/www/myapp"
})
```

### `list_directory`
列出目录内容，显示详细文件信息。

**参数：**
- `path` (str, 可选): 要列出的目录路径（默认为当前目录）
- `show_hidden` (bool, 可选): 是否显示隐藏文件（默认：false）

**示例：**
```python
await client.call_tool("list_directory", {
    "path": "/home/user",
    "show_hidden": true
})
```

## 📚 资源

### `system://info`
获取全面的系统信息，包括操作系统详情、Python版本、环境变量和当前工作目录。

**示例：**
```python
info = await client.read_resource("system://info")
print(info)
```

## 📝 提示

### `deploy_application`
为应用程序生成部署指令。

**参数：**
- `app_name` (str): 要部署的应用程序名称
- `target_dir` (str): 部署目标目录
- `repo_url` (str, 可选): Git仓库URL

**示例：**
```python
prompt = await client.get_prompt("deploy_application", {
    "app_name": "my-web-app",
    "target_dir": "/var/www/my-web-app",
    "repo_url": "https://github.com/user/my-web-app.git"
})
```

## ⚙️ 配置

### 命令行选项

```bash
cli-executor-mcp --help
```

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--transport` | 传输协议 (stdio, streamable-http) | streamable-http |
| `--host` | HTTP服务器绑定主机 | 127.0.0.1 |
| `--port` | HTTP服务器端口 | 8000 |
| `--debug` | 启用调试日志 | false |

### 环境变量

您也可以使用环境变量配置服务器：

- `CLI_EXECUTOR_HOST`: HTTP服务器主机
- `CLI_EXECUTOR_PORT`: HTTP服务器端口
- `CLI_EXECUTOR_TRANSPORT`: 传输类型
- `CLI_EXECUTOR_DEBUG`: 启用调试模式

## 🔒 安全注意事项

- ⚠️ **危险命令**: 运行破坏性命令如`rm -rf`前请务必确认
- ⏱️ **长时间运行的命令**: 对于长时间运行的进程使用`nohup`，并用`tail -f`监控
- 🔐 **权限**: 服务器以启动用户的权限运行
- 🌐 **网络访问**: 使用HTTP传输时，请确保网络安全
- 📁 **文件访问**: 服务器可以访问用户有权限的任何文件

## 🏗️ 开发

### 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/CaptainJi/cli_executor.git
cd cli_executor

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 以开发模式安装
pip install -e .

# 安装开发依赖
pip install fastmcp[dev]
```

### 运行测试

```bash
# 以调试模式运行服务器
cli-executor-mcp --debug

# 使用MCP客户端测试
python -c "
import asyncio
import fastmcp

async def test():
    client = fastmcp.Client('stdio', command='cli-executor-mcp')
    result = await client.call_tool('execute_command', {'command': 'echo Hello, World!'})
    print(result)

asyncio.run(test())
"
```

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 🤝 贡献

欢迎贡献！请随时提交Pull Request。

## 📞 支持

如果您遇到任何问题或有疑问，请在GitHub上[提交issue](https://github.com/CaptainJi/cli_executor/issues)。