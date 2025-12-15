# Crawler_new - 基于千问大模型的智能化爬虫

## 项目简介

`crawler_new` 是基于 Scrapy 框架和通义千问大模型的智能化历史数据爬虫，用于爬取和结构化提取明朝皇帝、事件、人物等历史信息。

### 核心特性

1. **双源融合提取**：同时使用 Wikipedia 和百度百科的 HTML，让大模型将两份资料互为补充，形成更准确完整的数据
2. **智能化提取**：使用通义千问大模型代替传统规则解析，自动从 HTML 中提取结构化数据
3. **递归爬取**：自动提取页面中的人物、事件链接并递归爬取
4. **批量处理**：先批量下载 HTML，再统一调用大模型处理，提高效率
5. **模块化设计**：Pipeline 清晰分离，便于扩展和维护

## 技术架构

### 数据流程

```
Scrapy 爬取 HTML 
  ↓
本地存储 (HtmlStoragePipeline)
  ↓
千问大模型提取 (QwenExtractionPipeline)
  ↓
数据验证 (DataValidationPipeline)
  ↓
存储到数据库 (SQLitePipeline + Neo4jPipeline)
  ↓
递归爬取链接 (RecursiveCrawlPipeline)
```

### 目录结构

```
crawler_new/
├── config/                 # 配置文件
│   ├── settings.py        # Scrapy 配置
│   └── ming_data.py       # 明朝皇帝基础数据
├── models/                 # 数据模型
│   └── items.py           # Scrapy Item 定义
├── spiders/                # 爬虫
│   └── ming_emperor_spider.py
├── pipelines/              # 数据处理管道
│   ├── html_storage_pipeline.py       # HTML 存储
│   ├── qwen_extraction_pipeline.py    # 千问提取
│   ├── data_validation_pipeline.py    # 数据验证
│   ├── sqlite_pipeline.py             # SQLite 存储
│   ├── neo4j_pipeline.py              # Neo4j 存储
│   └── recursive_crawl_pipeline.py    # 递归爬取
├── utils/                  # 工具类
│   └── qwen_extractor.py  # 千问大模型集成
├── data/                   # 数据存储目录
│   ├── html/              # HTML 文件
│   │   ├── emperor/
│   │   ├── event/
│   │   └── person/
│   ├── logs/              # 日志文件
│   └── httpcache/         # HTTP 缓存
├── middlewares.py          # Scrapy 中间件
├── run_crawler.py          # 运行脚本
├── LOGGING_GUIDE.md        # 日志指南（新增）
└── README.md               # 本文档
```

## 快速开始

### 1. 环境准备

确保已安装项目依赖（参考根目录 `requirements.txt`）：

```bash
pip install -r requirements.txt
```

### 2. 配置千问 API Key

编辑 `crawler_new/config/settings.py`，填入你的通义千问 API Key：

```python
# 千问大模型配置
QWEN_API_KEY = 'sk-xxxxxxxxxxxxxxxx'  # 填入你的 API Key
QWEN_MODEL = 'qwen-max'  # 或 qwen-turbo
```

**获取 API Key**：
1. 访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/)
2. 注册并创建 API Key
3. 复制 API Key 并填入配置文件

### 3. 运行爬虫

#### 方法一：使用便捷脚本（推荐）

```bash
# 进入 crawler_new 目录
cd crawler_new

# 测试模式 - 只爬取前3位皇帝（Wikipedia）
python run_crawler.py --source wikipedia --mode test

# 测试模式 - 爬取百度百科
python run_crawler.py --source baidu --mode test

# 测试模式 - 同时爬取两个数据源
python run_crawler.py --source both --mode test

# 全量模式 - 爬取所有16位皇帝
python run_crawler.py --source wikipedia --mode full
```

#### 方法二：使用 Scrapy 命令

```bash
# 进入项目根目录
cd /Users/master/Documents/AI-Project/HistoryGogo

# 运行爬虫
scrapy crawl ming_emperor -s CRAWL_MODE=test
```

### 4. 查看结果

爬取完成后，查看以下位置的数据：

- **HTML 文件**：`crawler_new/data/html/emperor/`
- **元数据**：`crawler_new/data/html/emperor/*_metadata.json`
- **日志文件**：`crawler_new/data/logs/crawler.log`（查看详细执行日志）
- **数据库**：（待实现）`server/database/historygogo.db`

### 5. 查看日志

爬虫运行时会输出详细的关键日志，方便追踪每个环节的执行状态：

```bash
# 实时查看日志
tail -f crawler_new/data/logs/crawler.log

# 只查看错误日志
grep "❌" crawler_new/data/logs/crawler.log

# 查看某个皇帝的日志
grep "朱元璋" crawler_new/data/logs/crawler.log
```

📖 **详细日志说明**: 参考 [LOGGING_GUIDE.md](LOGGING_GUIDE.md)

## 配置说明

### 爬取模式

在 `config/settings.py` 中配置：

```python
# 爬取模式配置
CRAWL_MODE = 'test'  # 'test' 或 'full'
TEST_EMPEROR_COUNT = 3  # 测试模式下爬取的皇帝数量

# 递归爬取配置
ENABLE_RECURSIVE_CRAWL = True  # 是否启用递归爬取人物、事件链接
MAX_RECURSIVE_DEPTH = 2  # 最大递归深度
```

### 数据源选择

运行爬虫时通过参数指定：

- `--source wikipedia`：只爬取维基百科
- `--source baidu`：只爬取百度百科
- `--source both`：同时爬取两个数据源

## 数据提取格式

### 皇帝信息

千问大模型提取的皇帝信息格式：

```json
{
  "皇帝": "朱元璋",
  "庙号": "明太祖",
  "年号": "洪武",
  "画像url": "https://...",
  "出生": "1328年10月21日",
  "去世": "1398年6月24日",
  "简介": "明朝开国皇帝..."
}
```

### 生平事迹

```json
[
  {
    "时间": "1328年10月29日（元天历元年九月十八日）",
    "事件": "出生于贫农家庭，原名朱重八，后改名朱兴宗...",
    "事件影响": "塑造了朱元璋的平民意识和反腐决心",
    "人物": [
      {"姓名": "朱五四", "关系": "父", "链接": "https://..."},
      {"姓名": "陈氏", "关系": "母", "链接": "https://..."}
    ],
    "地点": "濠州钟离县东乡（今安徽省凤阳县小溪河镇燃灯寺村）"
  }
]
```

## 性能优化建议

1. **批量下载**：先批量下载 HTML，再统一处理
2. **API 限流**：注意千问 API 的调用频率限制
3. **缓存机制**：Scrapy 自动缓存 HTTP 响应（24小时）
4. **递归深度**：合理设置递归深度，避免过度爬取

## 待完成功能

- [ ] 人物信息提取（`extract_person_info`）
- [ ] 事件信息提取（`extract_event_info`）
- [ ] SQLite 数据库存储逻辑
- [ ] Neo4j 图数据库存储逻辑
- [ ] 数据去重与合并策略
- [ ] 错误重试机制优化

## 与 crawler 的区别

| 特性 | crawler（旧版） | crawler_new（新版） |
|------|----------------|-------------------|
| HTML 解析 | BeautifulSoup + 规则 | 千问大模型智能提取 |
| 提取方式 | 基于 CSS 选择器 | 自然语言处理 |
| 扩展性 | 需修改规则代码 | 只需调整 Prompt |
| 准确性 | 依赖规则准确性 | AI 理解能力强 |
| 成本 | 无额外成本 | 需调用 API（付费） |

## 常见问题

### Q1: 千问 API 调用失败怎么办？

检查以下内容：
1. API Key 是否正确
2. 账户余额是否充足
3. 网络连接是否正常
4. API 限流是否触发

### Q2: 如何只下载 HTML 不调用大模型？

编辑 `config/settings.py`，将 `QWEN_API_KEY` 留空：

```python
QWEN_API_KEY = ''  # 留空则跳过千问提取
```

### Q3: 递归爬取太多链接怎么办？

调整递归深度和启用状态：

```python
ENABLE_RECURSIVE_CRAWL = False  # 禁用递归
MAX_RECURSIVE_DEPTH = 1  # 或降低深度
```

## 参考资料

- [Scrapy 官方文档](https://docs.scrapy.org/)
- [通义千问 API 文档](https://help.aliyun.com/zh/dashscope/)
- [项目整体架构](../README.md)

## 许可证

MIT License
