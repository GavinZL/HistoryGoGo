# Crawler_new 项目总结

## 📋 项目概述

`crawler_new` 是基于 **Scrapy 框架** 和 **通义千问大模型** 的智能化历史数据爬虫，用于爬取明朝皇帝、事件、人物等历史信息。

### 核心创新点

1. **AI 驱动的数据提取**：使用千问大模型代替传统 BeautifulSoup 规则解析
2. **流程化处理**：HTML 下载 → 本地存储 → 大模型提取 → 数据库存储
3. **智能递归爬取**：自动提取页面中的链接并递归下载
4. **批量处理优化**：先批量下载 HTML，再统一调用大模型，提高效率

---

## 🏗️ 技术架构

### 数据处理流程

```
┌─────────────┐
│ Scrapy 爬取 │  爬取 Wikipedia/百度百科 HTML
└──────┬──────┘
       ↓
┌─────────────┐
│  HTML 存储  │  保存原始 HTML 到本地
└──────┬──────┘
       ↓
┌─────────────┐
│  千问提取   │  调用大模型提取结构化数据
└──────┬──────┘
       ↓
┌─────────────┐
│  数据验证   │  验证提取数据的完整性
└──────┬──────┘
       ↓
┌─────────────┐
│ 数据库存储  │  存入 SQLite + Neo4j
└──────┬──────┘
       ↓
┌─────────────┐
│  递归爬取   │  提取链接，触发新的爬取任务
└─────────────┘
```

### Pipeline 设计

| Pipeline | 优先级 | 功能 | 状态 |
|----------|--------|------|------|
| HtmlStoragePipeline | 100 | 存储原始 HTML | ✅ 已完成 |
| QwenExtractionPipeline | 200 | 千问大模型提取 | ✅ 已完成 |
| DataValidationPipeline | 300 | 数据验证 | ✅ 已完成 |
| SQLitePipeline | 400 | SQLite 存储 | ⏳ 待实现 |
| Neo4jPipeline | 500 | Neo4j 存储 | ⏳ 待实现 |
| RecursiveCrawlPipeline | 600 | 递归爬取 | ✅ 已完成 |

---

## 📁 目录结构

```
crawler_new/
├── config/                          # 配置文件
│   ├── __init__.py
│   ├── settings.py                  # Scrapy 配置
│   └── ming_data.py                 # 明朝皇帝种子数据
│
├── models/                          # 数据模型
│   ├── __init__.py
│   └── items.py                     # Scrapy Item 定义
│
├── spiders/                         # 爬虫
│   ├── __init__.py
│   └── ming_emperor_spider.py       # 明朝皇帝爬虫
│
├── pipelines/                       # 数据处理管道
│   ├── __init__.py
│   ├── html_storage_pipeline.py     # HTML 存储
│   ├── qwen_extraction_pipeline.py  # 千问大模型提取
│   ├── data_validation_pipeline.py  # 数据验证
│   ├── sqlite_pipeline.py           # SQLite 存储（待实现）
│   ├── neo4j_pipeline.py            # Neo4j 存储（待实现）
│   └── recursive_crawl_pipeline.py  # 递归爬取
│
├── utils/                           # 工具类
│   ├── __init__.py
│   └── qwen_extractor.py            # 千问 API 集成
│
├── data/                            # 数据存储目录（运行时生成）
│   ├── html/
│   │   ├── emperor/
│   │   ├── event/
│   │   └── person/
│   ├── logs/
│   └── httpcache/
│
├── middlewares.py                   # Scrapy 中间件
├── run_crawler.py                   # 运行脚本
├── scrapy.cfg                       # Scrapy 配置
│
├── README.md                        # 完整文档
├── QUICKSTART.md                    # 快速开始指南
├── PROJECT_SUMMARY.md               # 本文档
└── .gitignore                       # Git 忽略文件
```

---

## 🎯 核心功能实现

### 1. 爬虫 Spider

**文件**：`spiders/ming_emperor_spider.py`

**功能**：
- ✅ 爬取明朝16位皇帝的 Wikipedia/百度百科页面
- ✅ 支持测试模式（前3位）和全量模式（16位）
- ✅ 支持单源（wikipedia/baidu）和双源（both）爬取
- ✅ 生成 `HtmlPageItem` 并传递给 Pipeline

**关键方法**：
- `start_requests()`：生成起始请求
- `parse_emperor(response)`：解析皇帝页面
- `parse_event(response)`：解析事件页面
- `parse_person(response)`：解析人物页面

### 2. HTML 存储

**文件**：`pipelines/html_storage_pipeline.py`

**功能**：
- ✅ 保存原始 HTML 到 `data/html/{emperor|event|person}/`
- ✅ 保存元数据 JSON（包含 URL、爬取时间等）
- ✅ 自动创建目录结构

**存储格式**：
```
ming_emperor_001_wikipedia.html          # HTML 文件
ming_emperor_001_wikipedia_metadata.json # 元数据
```

### 3. 千问大模型提取

**文件**：
- `utils/qwen_extractor.py`：千问 API 集成
- `pipelines/qwen_extraction_pipeline.py`：提取 Pipeline

**功能**：
- ✅ 调用通义千问 API 提取结构化数据
- ✅ 皇帝信息提取（姓名、庙号、年号、画像、出生、去世、简介）
- ✅ 生平事迹提取（时间、事件、人物、地点、链接）
- ✅ 智能解析 JSON 返回结果
- ⏳ 人物信息提取（待实现）
- ⏳ 事件信息提取（待实现）

**提取示例**：

皇帝信息：
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

生平事迹：
```json
[
  {
    "时间": "1368年",
    "事件": "朱元璋在应天府称帝",
    "事件链接": "https://...",
    "人物": ["李善长", "刘基"],
    "人物链接": ["https://...", "https://..."],
    "地点": "应天府"
  }
]
```

### 4. 递归爬取

**文件**：`pipelines/recursive_crawl_pipeline.py`

**功能**：
- ✅ 从提取的数据中自动获取人物、事件链接
- ✅ 生成新的 Scrapy 请求并提交到调度器
- ✅ 支持递归深度控制（默认最大深度 2）
- ✅ URL 去重，避免重复爬取

**配置**：
```python
ENABLE_RECURSIVE_CRAWL = True  # 启用递归
MAX_RECURSIVE_DEPTH = 2        # 最大深度
```

### 5. 数据验证

**文件**：`pipelines/data_validation_pipeline.py`

**功能**：
- ✅ 验证必填字段是否存在
- ✅ 检查数据格式是否正确
- ✅ 输出验证结果日志

---

## 🚀 使用方法

### 基本使用

```bash
cd crawler_new

# 测试模式（前3位皇帝）
python run_crawler.py --source wikipedia --mode test

# 全量模式（16位皇帝）
python run_crawler.py --source wikipedia --mode full

# 爬取百度百科
python run_crawler.py --source baidu --mode test

# 同时爬取双源
python run_crawler.py --source both --mode test
```

### 配置 API Key

编辑 `config/settings.py`：

```python
QWEN_API_KEY = 'sk-your-api-key-here'
```

### 查看结果

```bash
# 查看 HTML 文件
ls data/html/emperor/

# 查看元数据
cat data/html/emperor/ming_emperor_001_wikipedia_metadata.json

# 查看日志
tail -f data/logs/crawler.log
```

---

## ✅ 已完成功能

- [x] Scrapy 爬虫框架搭建
- [x] HTML 下载与本地存储
- [x] 千问大模型集成
- [x] 皇帝信息结构化提取
- [x] 生平事迹结构化提取
- [x] 数据验证 Pipeline
- [x] 递归爬取逻辑
- [x] 双源爬取支持（Wikipedia + 百度百科）
- [x] 测试/全量模式切换
- [x] 运行脚本和文档

---

## 📝 待实现功能

### 高优先级

- [ ] **SQLite 存储逻辑**
  - 将提取的结构化数据存入 SQLite
  - 复用 `crawler/pipelines/sqlite_pipeline.py` 的逻辑
  
- [ ] **Neo4j 存储逻辑**
  - 创建节点：Emperor、Event、Person
  - 创建关系：RULED、PARTICIPATED、HAPPENED_IN
  - 复用 `crawler/pipelines/neo4j_pipeline.py` 的逻辑

- [ ] **人物信息提取**
  - 在 `qwen_extractor.py` 中实现 `extract_person_info()`
  - 提取人物的姓名、职位、出生、去世、简介等

- [ ] **事件信息提取**
  - 在 `qwen_extractor.py` 中实现 `extract_event_info()`
  - 提取事件的时间、地点、参与人物、结果等

### 中优先级

- [ ] **数据去重与合并**
  - Wikipedia 和百度百科数据合并策略
  - 相同实体的数据融合

- [ ] **错误重试机制**
  - 千问 API 调用失败重试
  - 网络请求失败重试优化

- [ ] **批量处理优化**
  - 先批量下载所有 HTML
  - 再统一调用大模型处理（提高效率）

### 低优先级

- [ ] **更多朝代支持**
  - 扩展到唐朝、宋朝、清朝等
  
- [ ] **数据可视化**
  - 生成统计报表
  - 爬取进度可视化

- [ ] **单元测试**
  - 编写测试用例
  - 覆盖核心功能

---

## 🔄 与 crawler 的对比

| 特性 | crawler（旧版） | crawler_new（新版） |
|------|----------------|-------------------|
| **HTML 解析** | BeautifulSoup + CSS 选择器 | 千问大模型智能提取 |
| **提取方式** | 手写解析规则 | 自然语言 Prompt |
| **扩展性** | 需修改代码 | 只需调整 Prompt |
| **准确性** | 依赖规则准确性 | AI 理解能力强 |
| **成本** | 无额外成本 | API 调用付费 |
| **维护成本** | 高（网站改版需修改规则） | 低（大模型自适应） |
| **数据源** | 单源（Wikipedia 或百度） | 双源互补 |

---

## 💡 设计亮点

### 1. 模块化设计

每个 Pipeline 职责单一，易于测试和维护：
- HTML 存储独立于提取
- 提取独立于数据库存储
- 递归爬取作为独立模块

### 2. 智能化提取

使用大模型代替规则，优势：
- 无需编写复杂的 CSS 选择器
- 自适应不同网站结构
- 提取更语义化的信息

### 3. 批量处理策略

先下载后处理，提高效率：
- 降低 API 调用频率
- 可离线重新提取数据
- 便于调试和验证

### 4. 递归爬取

自动发现并爬取关联页面：
- 从生平事迹中提取人物、事件链接
- 自动触发新的爬取任务
- 深度可控，避免过度爬取

---

## 🎓 学习收获

通过本项目，可以学习到：

1. **Scrapy 框架**：深度理解 Spider、Pipeline、Middleware 的设计
2. **大模型集成**：学会调用千问 API 进行数据提取
3. **数据工程**：HTML 存储、数据验证、批量处理等实践
4. **递归爬取**：实现复杂的爬取逻辑
5. **项目架构**：模块化、可扩展的代码设计

---

## 📞 联系与反馈

如有问题或建议，欢迎提 Issue 或 PR。

---

**创建时间**：2025-12-14  
**版本**：v1.0  
**作者**：HistoryGogo Team
