# 安装与运行指南

## 环境要求

- Python 3.9 或更高版本
- pip (Python包管理器)
- (可选) Neo4j 4.4+ (用于图数据库功能)

## 安装步骤

### 1. 克隆或下载项目

```bash
cd /Users/master/Documents/AI-Project/HistoryGogo
```

### 2. 创建虚拟环境（强烈推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 安装依赖包

```bash
# 确保pip是最新版本
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

依赖包列表：
- scrapy>=2.8.0 - 爬虫框架
- beautifulsoup4>=4.11.0 - HTML解析
- lxml>=4.9.0 - XML/HTML解析器
- requests>=2.28.0 - HTTP客户端
- python-dateutil>=2.8.0 - 日期处理
- pandas>=2.0.0 - 数据处理
- fastapi>=0.95.0 - API框架（后续使用）
- uvicorn>=0.21.0 - ASGI服务器（后续使用）
- pydantic>=1.10.0 - 数据验证（后续使用）
- sqlalchemy>=2.0.0 - ORM框架（后续使用）
- neo4j>=5.7.0 - Neo4j驱动（后续使用）
- python-dotenv>=1.0.0 - 环境变量管理
- loguru>=0.7.0 - 日志库
- fake-useragent>=1.4.0 - User-Agent生成

### 4. 验证安装

```bash
# 测试爬虫基础功能
python crawler/test_crawler.py
```

如果看到类似以下输出，说明安装成功：

```
==================================================
历史时间轴爬虫 - 功能测试
==================================================

==================================================
测试明朝基础数据
==================================================
朝代: 明朝
朝代ID: ming
...
```

## 运行爬虫

### 测试模式（推荐用于开发）

```bash
# 测试爬虫是否能正常工作
python crawler/test_crawler.py
```

### 正式运行爬虫

```bash
# 创建必要的目录
mkdir -p crawler/data/logs
mkdir -p crawler/data/httpcache
mkdir -p crawler/data/jobs

# 运行百度百科爬虫
scrapy crawl baidu_baike
```

### 爬虫配置说明

爬虫配置文件位于 `crawler/config/settings.py`，主要配置项：

- `DOWNLOAD_DELAY = 3` - 请求延迟3秒（避免被封）
- `CONCURRENT_REQUESTS = 8` - 并发请求数
- `RETRY_TIMES = 3` - 失败重试次数
- `DOWNLOAD_TIMEOUT = 30` - 超时时间30秒

## 常见问题

### 1. 安装依赖失败

**问题**: `pip install` 失败或超时

**解决方案**:
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 导入模块失败

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 确保虚拟环境已激活
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 重新安装依赖
pip install -r requirements.txt
```

### 3. Scrapy命令找不到

**问题**: `scrapy: command not found`

**解决方案**:
```bash
# 确保虚拟环境已激活，然后重新安装scrapy
pip install scrapy
```

### 4. 爬虫被封

**问题**: 爬虫请求被拒绝或返回403/429错误

**解决方案**:
- 增加请求延迟（修改 `DOWNLOAD_DELAY`）
- 减少并发请求数（修改 `CONCURRENT_REQUESTS`）
- 使用代理IP（可选）

## 项目开发进度

### ✅ 已完成（第1周）

1. 项目目录结构搭建
2. Python环境配置
3. 数据模型定义（Emperor, Event, Person）
4. 百度百科爬虫实现
5. 日期解析工具
6. 文本清洗工具
7. 测试脚本

### 🔄 进行中

- 数据持久化管道（SQLite + Neo4j）
- 数据清洗和验证逻辑

### 📋 待开发

- 维基百科爬虫
- FastAPI服务器
- iOS客户端

## 下一步操作

1. **测试爬虫功能**
   ```bash
   python crawler/test_crawler.py
   ```

2. **安装依赖后开始爬取数据**（需要先安装依赖）
   ```bash
   pip install -r requirements.txt
   scrapy crawl baidu_baike
   ```

3. **查看设计文档**
   - 完整设计文档: `.qoder/quests/historical-timeline-crawling.md`
   - 项目README: `README.md`

## 技术支持

如遇到问题，请检查：
1. Python版本是否 >= 3.9
2. 虚拟环境是否已激活
3. 依赖包是否全部安装成功
4. 网络连接是否正常

更多信息请参考 `README.md` 和设计文档。
