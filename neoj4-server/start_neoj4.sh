#!/bin/bash
# Neo4j Docker 启动脚本
# 用于启动 HistoryGogo 项目的 Neo4j 图数据库服务

set -e  # 遇到错误立即退出

# 配置变量
CONTAINER_NAME="historygogo-neo4j"
NEO4J_VERSION="5.15.0"  # 使用稳定版本
NEO4J_USER="neo4j"
NEO4J_PASSWORD="Ls_gavin_08"  # 与 crawler/config/settings.py 中的密码一致
HTTP_PORT="7474"
BOLT_PORT="7687"

# 数据持久化目录（相对于项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${PROJECT_ROOT}/neoj4-server/data"
LOGS_DIR="${PROJECT_ROOT}/neoj4-server/logs"
IMPORT_DIR="${PROJECT_ROOT}/neoj4-server/import"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  HistoryGogo Neo4j 启动脚本${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装或未在 PATH 中${NC}"
    echo "请先安装 Docker: https://www.docker.com/get-started"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo -e "${RED}错误: Docker 服务未运行${NC}"
    echo "请启动 Docker Desktop 或 Docker 服务"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker 已就绪"

# 创建必要的目录
echo -e "${YELLOW}创建数据持久化目录...${NC}"
mkdir -p "$DATA_DIR" "$LOGS_DIR" "$IMPORT_DIR"
echo -e "${GREEN}✓${NC} 目录创建完成"
echo "  - 数据目录: $DATA_DIR"
echo "  - 日志目录: $LOGS_DIR"
echo "  - 导入目录: $IMPORT_DIR"
echo ""

# 检查容器是否已存在
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}检测到已存在的 Neo4j 容器...${NC}"
    
    # 检查容器是否正在运行
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${GREEN}Neo4j 容器已在运行中${NC}"
        echo ""
        echo -e "${BLUE}访问信息:${NC}"
        echo "  - Web 界面: http://localhost:${HTTP_PORT}"
        echo "  - Bolt 连接: bolt://localhost:${BOLT_PORT}"
        echo "  - 用户名: ${NEO4J_USER}"
        echo "  - 密码: ${NEO4J_PASSWORD}"
        echo ""
        echo "如需重启容器，请运行: docker restart ${CONTAINER_NAME}"
        exit 0
    else
        echo -e "${YELLOW}启动已存在的容器...${NC}"
        docker start "$CONTAINER_NAME"
        echo -e "${GREEN}✓${NC} 容器已启动"
    fi
else
    echo -e "${YELLOW}创建并启动新的 Neo4j 容器...${NC}"
    
    # 运行 Neo4j 容器
    docker run \
        --name "$CONTAINER_NAME" \
        -p "${HTTP_PORT}:7474" \
        -p "${BOLT_PORT}:7687" \
        -d \
        -v "${DATA_DIR}:/data" \
        -v "${LOGS_DIR}:/logs" \
        -v "${IMPORT_DIR}:/var/lib/neo4j/import" \
        -e NEO4J_AUTH="${NEO4J_USER}/${NEO4J_PASSWORD}" \
        -e NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
        -e NEO4J_dbms_memory_pagecache_size=512M \
        -e NEO4J_dbms_memory_heap_initial__size=512M \
        -e NEO4J_dbms_memory_heap_max__size=1G \
        --restart unless-stopped \
        neo4j:"${NEO4J_VERSION}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Neo4j 容器创建成功"
    else
        echo -e "${RED}✗${NC} 容器创建失败"
        exit 1
    fi
fi

# 等待 Neo4j 启动
echo ""
echo -e "${YELLOW}等待 Neo4j 服务启动...${NC}"
MAX_WAIT=60
WAIT_TIME=0

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if curl -s http://localhost:${HTTP_PORT} > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Neo4j 服务已就绪！"
        break
    fi
    echo -n "."
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo -e "\n${RED}警告: Neo4j 启动超时${NC}"
    echo "请检查日志: docker logs ${CONTAINER_NAME}"
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Neo4j 启动完成！${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}访问信息:${NC}"
echo "  - Web 界面: ${GREEN}http://localhost:${HTTP_PORT}${NC}"
echo "  - Bolt 连接: ${GREEN}bolt://localhost:${BOLT_PORT}${NC}"
echo "  - 用户名: ${GREEN}${NEO4J_USER}${NC}"
echo "  - 密码: ${GREEN}${NEO4J_PASSWORD}${NC}"
echo ""
echo -e "${BLUE}常用命令:${NC}"
echo "  - 查看日志: ${YELLOW}docker logs ${CONTAINER_NAME}${NC}"
echo "  - 停止服务: ${YELLOW}docker stop ${CONTAINER_NAME}${NC}"
echo "  - 重启服务: ${YELLOW}docker restart ${CONTAINER_NAME}${NC}"
echo "  - 删除容器: ${YELLOW}docker rm -f ${CONTAINER_NAME}${NC}"
echo ""
echo -e "${BLUE}下一步:${NC}"
echo "  1. 访问 http://localhost:${HTTP_PORT} 使用 Web 界面"
echo "  2. 运行爬虫测试: ${YELLOW}cd .. && scrapy crawl baidu_baike -s ROBOTSTXT_OBEY=False -a crawl_mode=test -a test_emperor_count=1${NC}"
echo ""
