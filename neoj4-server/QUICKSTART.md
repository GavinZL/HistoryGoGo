# Neo4j 快速使用指南

## 📋 前置要求

1. ✅ 安装 Docker Desktop
2. ✅ 启动 Docker 服务

## 🚀 一键启动

```bash
cd /Users/master/Documents/AI-Project/HistoryGogo/neoj4-server
./start_neoj4.sh
```

## 🌐 访问 Neo4j

启动成功后，在浏览器访问：http://localhost:7474

**登录信息：**
- 用户名: `neo4j`
- 密码: `password`

## 🛑 停止服务

```bash
./stop_neo4j.sh
```

## 📊 验证数据

在 Neo4j Browser 中运行：

```cypher
// 查看所有节点
MATCH (n) RETURN n LIMIT 25

// 查看皇帝
MATCH (e:Emperor) RETURN e

// 查看关系图
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50
```

## 🔗 运行爬虫

```bash
cd /Users/master/Documents/AI-Project/HistoryGogo
scrapy crawl baidu_baike -s ROBOTSTXT_OBEY=False -a crawl_mode=test -a test_emperor_count=1
```

## 💡 常见问题

### Q: Docker 服务未运行？
A: 启动 Docker Desktop 应用

### Q: 端口被占用？
A: 运行 `docker stop historygogo-neo4j`

### Q: 忘记密码？
A: 默认密码是 `password`，配置在 `crawler/config/settings.py`

## 📚 更多信息

查看完整文档：[README.md](./README.md)
