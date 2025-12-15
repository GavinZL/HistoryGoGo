#!/bin/bash
# Ollama 安装和模型下载脚本

set -e

echo "========================================"
echo "  Ollama 本地大模型安装脚本"
echo "========================================"
echo ""

# 检查是否已安装 Ollama
if command -v ollama &> /dev/null; then
    echo "✅ Ollama 已安装"
    ollama --version
else
    echo "📦 正在安装 Ollama..."
    
    # 检查是否安装了 Homebrew
    if command -v brew &> /dev/null; then
        echo "   使用 Homebrew 安装..."
        brew install ollama
    else
        echo "   使用官方脚本安装..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    
    echo "✅ Ollama 安装完成"
fi

echo ""
echo "========================================"
echo "  启动 Ollama 服务"
echo "========================================"
echo ""
echo "请在新终端中运行以下命令启动服务："
echo "  ollama serve"
echo ""
echo "然后按回车继续下载模型..."
read -p ""

echo ""
echo "========================================"
echo "  下载推荐模型"
echo "========================================"
echo ""

# 选择模型
echo "请选择要下载的模型："
echo "  1) Qwen2.5-7B (推荐，中文优秀，约 4.7GB)"
echo "  2) Qwen2.5-3B (轻量级，速度快，约 2.0GB)"
echo "  3) Llama-3.1-8B (通用能力强，约 4.7GB)"
echo "  4) 跳过下载，手动安装"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo "📥 下载 Qwen2.5-7B..."
        ollama pull qwen2.5:7b
        echo "✅ Qwen2.5-7B 下载完成"
        MODEL="qwen2.5:7b"
        ;;
    2)
        echo "📥 下载 Qwen2.5-3B..."
        ollama pull qwen2.5:3b
        echo "✅ Qwen2.5-3B 下载完成"
        MODEL="qwen2.5:3b"
        ;;
    3)
        echo "📥 下载 Llama-3.1-8B..."
        ollama pull llama3.1:8b
        echo "✅ Llama-3.1-8B 下载完成"
        MODEL="llama3.1:8b"
        ;;
    4)
        echo "⏭️  跳过下载"
        MODEL="qwen2.5:7b"
        ;;
    *)
        echo "❌ 无效选项，使用默认模型 Qwen2.5-7B"
        ollama pull qwen2.5:7b
        MODEL="qwen2.5:7b"
        ;;
esac

echo ""
echo "========================================"
echo "  测试模型"
echo "========================================"
echo ""

echo "🧪 测试模型响应..."
echo "测试提示词: '你好，请用一句话介绍自己'"

ollama run $MODEL "你好，请用一句话介绍自己" 2>&1 | head -n 10

echo ""
echo "========================================"
echo "  安装完成"
echo "========================================"
echo ""
echo "✅ 安装成功！"
echo ""
echo "📝 下一步操作："
echo "  1. 确保 Ollama 服务在后台运行: ollama serve"
echo "  2. 在 config/settings.py 中配置:"
echo "     USE_LOCAL_LLM = True"
echo "     LOCAL_LLM_MODEL = \"$MODEL\""
echo "  3. 运行测试: python test_local_llm.py"
echo ""
echo "📚 查看文档: crawler_new/local_llm/README.md"
echo ""
