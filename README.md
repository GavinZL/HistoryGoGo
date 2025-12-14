# HistoryGogo - 历史时间轴学习App

## 项目概述

这是一个以时间轴为主线的中国历史学习App项目，通过结构化数据呈现明朝历代皇帝的世系、重大事件及关键人物，实现历史脉络的可视化学习。

## 项目结构

```
HistoryGogo/
├── crawler/                    # 数据爬取脚本目录
│   ├── spiders/               # 爬虫实现
│   │   └── baidu_baike_spider.py  # 百度百科爬虫
│   ├── pipelines/             # 数据处理管道
│   ├── models/                # 数据模型定义
│   │   └── entities.py        # 实体类定义（Emperor, Event, Person等）
│   ├── utils/                 # 工具函数
│   │   └── date_utils.py      # 日期解析和文本清洗工具
│   ├── config/                # 爬虫配置
│   │   ├── settings.py        # Scrapy配置
│   │   └── ming_data.py       # 明朝基础数据
│   └── test_crawler.py        # 爬虫测试脚本
├── server/                    # FastAPI服务器目录（待开发）
├── ios-app/                   # iOS客户端目录（待开发）
└── resources/                 # 资源文件目录
```

## 技术栈

### 数据爬取
- Python 3.9+
- Scrapy 2.8+
- BeautifulSoup4
- python-dateutil

### 数据存储
- SQLite（结构化数据）
- Neo4j（图数据库，人物关系网络）

### API服务
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy

### iOS客户端
- Swift 5.0+
- SwiftUI
- MVVM架构

## 快速开始

### 1. 环境准备

#### 安装Python依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 测试爬虫功能

运行测试脚本验证爬虫基础功能：

```bash
python crawler/test_crawler.py
```

### 3. 运行爬虫

```bash
# 进入项目根目录
cd /path/to/HistoryGogo

# 运行百度百科爬虫
scrapy crawl baidu_baike -s JOBDIR=crawler/data/jobs/baidu
```

## 开发进度

### 阶段一：数据爬取与存储（第1周已完成）

- [x] 创建项目目录结构
- [x] 配置Python环境和依赖
- [x] 实现数据模型定义（Emperor, Event, Person实体类）
- [x] 实现百度百科爬虫核心功能
  - [x] URL生成
  - [x] HTML解析
  - [x] 数据提取（皇帝、事件、人物）
  - [x] 日期解析工具
  - [x] 文本清洗工具
- [x] 创建测试脚本

### 接下来的任务

#### 第2周：维基百科爬虫与数据清洗
- [ ] 实现维基百科爬虫
- [ ] 实现数据清洗管道
- [ ] 实现数据验证管道
- [ ] 实现数据合并策略

#### 第3周：数据库设计与实现
- [ ] 设计SQLite数据库表结构
- [ ] 设计Neo4j图数据库结构
- [ ] 实现数据库初始化脚本
- [ ] 实现数据持久化管道

#### 第4周：数据持久化与全量爬取
- [ ] 完善SQLite和Neo4j持久化管道
- [ ] 执行明朝数据全量爬取
- [ ] 数据质量验证和修正
- [ ] 生成数据统计报告

## 数据模型

### 皇帝（Emperor）
- emperor_id: 皇帝ID
- name: 姓名
- temple_name: 庙号
- reign_title: 年号
- birth_date: 出生日期
- death_date: 去世日期
- reign_start: 在位开始
- reign_end: 在位结束
- dynasty_order: 朝代顺序
- biography: 生平简介
- achievements: 主要成就

### 事件（Event）
- event_id: 事件ID
- title: 事件名称
- event_type: 事件类型（政治/军事/文化/经济/外交等）
- start_date: 开始日期
- end_date: 结束日期
- location: 发生地点
- description: 事件描述
- significance: 历史意义
- related_persons: 相关人物列表

### 人物（Person）
- person_id: 人物ID
- name: 姓名
- alias: 别名列表
- person_type: 人物类型（文臣/武将/文学家/艺术家等）
- birth_date: 出生日期
- death_date: 去世日期
- position: 主要职位
- biography: 生平简介
- style: 风格特点
- works: 作品列表
- contributions: 主要贡献

## 明朝数据范围

- **皇帝信息**: 16位皇帝完整信息（朱元璋至朱由检）
- **重大事件**: 200-300条政治、军事、文化事件
- **重要人物**: 500-800人（文臣、武将、文学家、艺术家等）
- **宗室成员**: 300-500人（皇子、皇后、妃嫔）

## 注意事项

1. **爬虫使用规范**
   - 遵守robots.txt协议
   - 设置合理的请求延迟（3-5秒）
   - 仅用于学习和非商业用途
   - 标注数据来源

2. **数据质量保证**
   - 多源数据验证（百度百科+维基百科）
   - 自动数据清洗和验证
   - 人工审核关键数据

3. **性能优化**
   - 使用HTTP缓存减少重复请求
   - 批量处理数据库操作
   - 合理设置并发请求数

## 设计文档

完整的设计文档位于：`.qoder/quests/historical-timeline-crawling.md`

## 许可证

本项目仅用于学习和研究目的。

## 联系方式

如有问题或建议，请联系项目团队。
