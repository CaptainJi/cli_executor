#!/bin/bash
# CLI Executor MCP 快速安装和测试脚本

set -e

echo "🚀 CLI Executor MCP - 安装和测试脚本"
echo "=================================="

# 检查Python版本
echo "📋 检查Python版本..."
python3 --version || {
    echo "❌ 需要Python 3但未找到"
    exit 1
}

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告：不在虚拟环境中"
    echo "   建议运行：python3 -m venv .venv && source .venv/bin/activate"
    read -p "   仍要继续吗？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 以开发模式安装包
echo "📦 以开发模式安装CLI Executor MCP..."
pip install -e .

# 安装FastMCP（如果尚未安装）
echo "📦 安装FastMCP..."
pip install "fastmcp>=2.11.0"

# 测试安装
echo "🧪 测试安装..."

# 测试1：检查命令是否可用
echo "   测试命令可用性..."
cli-executor-mcp --help > /dev/null || {
    echo "❌ 未找到cli-executor-mcp命令"
    exit 1
}

# 测试2：运行基本功能测试
echo "   测试基本功能..."
timeout 10s cli-executor-mcp --transport stdio <<EOF || {
    echo "❌ 基本功能测试失败"
    exit 1
}
EOF

echo "✅ 安装成功完成！"
echo ""
echo "🎉 下一步："
echo "   1. 运行服务器：cli-executor-mcp"
echo "   2. 或使用HTTP传输：cli-executor-mcp --transport http --port 8000"
echo "   3. 运行测试：python tests/test_server.py"
echo "   4. 尝试示例：python examples/usage_example.py"
echo ""
echo "📚 更多信息请参见README.md"