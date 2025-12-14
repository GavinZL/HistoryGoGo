#!/bin/bash
# Neo4j Docker 停止脚本

set -e

CONTAINER_NAME="historygogo-neo4j"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  HistoryGogo Neo4j 停止脚本${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 检查容器是否存在
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}容器 ${CONTAINER_NAME} 不存在${NC}"
    exit 0
fi

# 检查容器是否正在运行
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}正在停止 Neo4j 容器...${NC}"
    docker stop "$CONTAINER_NAME"
    echo -e "${GREEN}✓${NC} Neo4j 容器已停止"
else
    echo -e "${YELLOW}Neo4j 容器未在运行${NC}"
fi

echo ""
echo -e "${BLUE}常用命令:${NC}"
echo "  - 重新启动: ${GREEN}./start_neoj4.sh${NC}"
echo "  - 查看日志: ${YELLOW}docker logs ${CONTAINER_NAME}${NC}"
echo "  - 删除容器: ${YELLOW}docker rm ${CONTAINER_NAME}${NC}"
echo ""
