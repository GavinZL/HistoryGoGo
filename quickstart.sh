#!/bin/bash

# HistoryGogo 项目快速开始脚本
# 用于快速设置开发环境和验证安装

echo "=================================================="
echo "  HistoryGogo - 历史时间轴学习App"
echo "  快速开始脚本"
echo "=================================================="
echo ""

# 检查Python版本
echo "📌 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python版本: $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
    echo "   ❌ 错误: 需要Python 3.9或更高版本"
    exit 1
fi
echo "   ✅ Python版本符合要求"
echo ""

# 检查是否已有虚拟环境
if [ -d "venv" ]; then
    echo "📌 发现已存在的虚拟环境"
    read -p "   是否重新创建虚拟环境? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   删除旧的虚拟环境..."
        rm -rf venv
        echo "   创建新的虚拟环境..."
        python3 -m venv venv
    fi
else
    echo "📌 创建Python虚拟环境..."
    python3 -m venv venv
fi

echo "   ✅ 虚拟环境准备完成"
echo ""

# 激活虚拟环境
echo "📌 激活虚拟环境..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "   ❌ 激活虚拟环境失败"
    exit 1
fi

echo "   ✅ 虚拟环境已激活"
echo ""

# 升级pip
echo "📌 升级pip到最新版本..."
pip install --upgrade pip -q

if [ $? -ne 0 ]; then
    echo "   ⚠️  pip升级失败，继续使用当前版本"
else
    echo "   ✅ pip升级完成"
fi
echo ""

# 安装依赖
echo "📌 安装项目依赖..."
echo "   这可能需要几分钟时间..."

pip install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "   ❌ 依赖安装失败"
    echo "   尝试使用国内镜像源..."
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    if [ $? -ne 0 ]; then
        echo "   ❌ 依赖安装失败，请手动安装"
        exit 1
    fi
fi

echo "   ✅ 依赖安装完成"
echo ""

# 创建必要的目录
echo "📌 创建必要的目录..."
mkdir -p crawler/data/logs
mkdir -p crawler/data/httpcache
mkdir -p crawler/data/jobs

echo "   ✅ 目录创建完成"
echo ""

# 运行测试
echo "📌 运行测试脚本..."
python crawler/test_crawler.py

if [ $? -ne 0 ]; then
    echo ""
    echo "   ⚠️  测试脚本运行有警告，但不影响继续"
else
    echo ""
    echo "   ✅ 测试通过！"
fi

echo ""
echo "=================================================="
echo "  🎉 环境配置完成！"
echo "=================================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 激活虚拟环境（如果未激活）："
echo "   source venv/bin/activate"
echo ""
echo "2. 运行测试脚本："
echo "   python crawler/test_crawler.py"
echo ""
echo "3. 运行爬虫（需要先完成数据库配置）："
echo "   scrapy crawl baidu_baike"
echo ""
echo "4. 查看项目文档："
echo "   - README.md - 项目说明"
echo "   - INSTALL.md - 安装指南"
echo "   - PROJECT_STATUS.md - 项目状态"
echo "   - .qoder/quests/historical-timeline-crawling.md - 完整设计文档"
echo ""
echo "=================================================="
