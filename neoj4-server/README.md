# Neo4j 图数据库服务

本目录包含 HistoryGogo 项目的 Neo4j 图数据库相关脚本和数据。

## 📁 目录结构

```
neoj4-server/
├── start_neoj4.sh      # Neo4j 启动脚本
├── stop_neo4j.sh       # Neo4j 停止脚本
├── data/               # Neo4j 数据持久化目录
├── logs/               # Neo4j 日志目录
├── import/             # 数据导入目录
└── README.md          # 本文档
```

## 🚀 快速开始

### 1. 启动 Neo4j 服务

```bash
cd neoj4-server
./start_neoj4.sh
```

脚本会自动：
- 检查 Docker 环境
- 创建必要的数据目录
- 启动 Neo4j 容器
- 等待服务就绪

### 2. 访问 Neo4j

启动成功后，可以通过以下方式访问：

- **Web 界面**: http://localhost:7474
- **Bolt 连接**: bolt://localhost:7687

**默认账户信息：**
- 用户名: `neo4j`
- 密码: `password`

### 3. 停止 Neo4j 服务

```bash
./stop_neo4j.sh
```

## 🔧 配置说明

### 容器配置

- **容器名称**: `historygogo-neo4j`
- **Neo4j 版本**: `5.15.0`
- **HTTP 端口**: `7474`
- **Bolt 端口**: `7687`

### 内存配置

- **Page Cache**: 512M
- **Heap Initial Size**: 512M
- **Heap Max Size**: 1G

如需调整内存配置，请编辑 `start_neoj4.sh` 中的相关环境变量。

### 数据持久化

所有数据都持久化到本地目录：
- `data/` - 数据库文件
- `logs/` - 日志文件
- `import/` - CSV 导入文件

## 📊 常用操作

### 查看容器状态

```bash
docker ps | grep historygogo-neo4j
```

### 查看日志

```bash
docker logs historygogo-neo4j
docker logs -f historygogo-neo4j  # 实时查看
```

### 重启服务

```bash
docker restart historygogo-neo4j
```

### 进入容器

```bash
docker exec -it historygogo-neo4j bash
```

### 删除容器和数据

```bash
# 停止并删除容器
docker rm -f historygogo-neo4j

# 删除数据（谨慎！）
rm -rf data/ logs/
```

## 🔗 与爬虫集成

Neo4j 启动后，爬虫会自动将数据保存到图数据库中。

### 运行爬虫测试

```bash
cd ..
scrapy crawl baidu_baike -s ROBOTSTXT_OBEY=False -a crawl_mode=test -a test_emperor_count=1
```

### 查看保存的数据

在 Neo4j Browser (http://localhost:7474) 中执行：

```cypher
// 查看所有节点
MATCH (n) RETURN n LIMIT 25

// 查看皇帝节点
MATCH (e:Emperor) RETURN e

// 查看关系
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50

// 统计节点数量
MATCH (n) RETURN labels(n) as NodeType, count(n) as Count
```

## 🛠️ 故障排查

### 问题 1: Docker 未运行

**错误信息**: `Docker 服务未运行`

**解决方案**: 启动 Docker Desktop

### 问题 2: 端口被占用

**错误信息**: `Bind for 0.0.0.0:7474 failed: port is already allocated`

**解决方案**:
```bash
# 查看占用端口的进程
lsof -i :7474
lsof -i :7687

# 停止占用端口的容器
docker stop <container_id>
```

### 问题 3: 服务启动超时

**解决方案**:
```bash
# 查看日志
docker logs historygogo-neo4j

# 重启容器
docker restart historygogo-neo4j
```

### 问题 4: 爬虫连接失败

**检查清单**:
1. Neo4j 容器是否运行：`docker ps | grep neo4j`
2. 端口是否正确：`7687`
3. 密码是否匹配：检查 `crawler/config/settings.py`

## 📚 参考资料

- [Neo4j 官方文档](https://neo4j.com/docs/)
- [Neo4j Docker 镜像](https://hub.docker.com/_/neo4j)
- [Cypher 查询语言](https://neo4j.com/developer/cypher/)

## 💡 提示

1. **首次启动**可能需要几秒到几十秒，请耐心等待
2. **数据持久化**在 `data/` 目录，重启容器不会丢失数据
3. **修改密码**后需要同步更新 `crawler/config/settings.py`
4. **生产环境**建议修改默认密码并启用 SSL
