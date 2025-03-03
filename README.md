# CLI Executor MCP

<div align="center">

**基于MCP的CLI命令执行服务，用于系统部署和管理**

</div>

## 概述

CLI Executor MCP是一个基于[Model Context Protocol (MCP)](https://modelcontextprotocol.io)的服务，它提供了执行Linux CLI命令的工具，使LLM（如Cursor、Claude）能够执行Linux系统命令、部署应用程序和管理系统。

主要功能：

- 执行单个CLI命令
- 执行多行脚本
- 列出目录内容
- 获取系统信息
- 提供部署应用的提示模板

## 安装

### 从源代码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/cli-executor-mcp.git
cd cli-executor-mcp

# 安装
pip install -e .
```

### 使用pip安装

```bash
pip install cli-executor-mcp
```

## 使用方法

### 作为命令行工具运行

```bash
# 使用sse传输（默认）
cli-executor-mcp

# 使用stdio传输
cli-executor-mcp --transport stdio

# 启用调试模式
cli-executor-mcp --debug

# 指定端口号
cli-executor-mcp --port 9000

# 指定主机地址
cli-executor-mcp --host 127.0.0.1

# 同时指定主机地址和端口号
cli-executor-mcp --host 127.0.0.1 --port 9000
```

### 环境变量配置

您也可以通过环境变量来配置CLI Executor MCP：

- `CLI_EXECUTOR_PORT`: 设置SSE服务器端口号（默认：8000）
- `CLI_EXECUTOR_HOST`: 设置SSE服务器主机地址（默认：0.0.0.0）
- `CLI_EXECUTOR_TRANSPORT`: 设置传输类型，可选值为"stdio"或"sse"（默认："sse"）
- `CLI_EXECUTOR_DEBUG`: 启用调试模式，可选值为"true"、"1"或"yes"（默认：禁用）

例如：

```bash
# 设置环境变量
export CLI_EXECUTOR_PORT=9000
export CLI_EXECUTOR_HOST=127.0.0.1
export CLI_EXECUTOR_DEBUG=true

# 运行服务器（将使用上面设置的环境变量）
cli-executor-mcp
```

### 在Claude Desktop中安装

使用MCP CLI工具安装：

```bash
mcp install cli-executor-mcp
```

或者从源代码安装：

```bash
cd cli-executor-mcp
mcp install .
```

## 工具和资源

### 工具

CLI Executor MCP提供以下工具：

1. **execute_command** - 执行单个CLI命令
   - 参数：
     - `command`: 要执行的命令
     - `working_dir`: (可选) 执行命令的工作目录

2. **execute_script** - 执行多行脚本
   - 参数：
     - `script`: 要执行的脚本内容（多行命令）
     - `working_dir`: (可选) 执行脚本的工作目录

3. **list_directory** - 列出指定目录的内容
   - 参数：
     - `path`: (可选) 要列出内容的目录路径

### 资源

1. **system://info** - 获取系统信息

### 提示

1. **deploy_app** - 创建一个部署应用的提示
   - 参数：
     - `app_name`: 应用名称
     - `target_dir`: 目标目录

## 示例

### 执行命令

```python
# 使用MCP客户端调用工具
result = await session.call_tool("execute_command", {"command": "ls -la"})
print(result)
```

### 执行脚本

```python
# 使用MCP客户端调用工具
script = """
mkdir -p test_dir
cd test_dir
echo "Hello, World!" > test.txt
ls -la
"""
result = await session.call_tool("execute_script", {"script": script})
print(result)
```

### 获取系统信息

```python
# 使用MCP客户端读取资源
content, mime_type = await session.read_resource("system://info")
print(content)
```

## 安全注意事项

CLI Executor MCP允许执行任意系统命令，这可能带来安全风险。在生产环境中使用时，请确保：

1. 限制服务器的访问权限
2. 在受限环境中运行服务器（如容器或沙箱）
3. 实施命令白名单或其他安全措施

## 许可证

MIT 
