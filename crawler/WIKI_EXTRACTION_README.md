# 维基百科爬虫信息提取功能说明

## 功能概述

本次更新为维基百科爬虫添加了以下新功能：

### 1. Infobox 信息框完整提取

在 `wikipedia_spider.py` 中的 `_extract_emperor_data` 和 `_extract_person_data` 方法中，现在可以提取：

#### 皇帝信息提取
- **基本字段**：出生日期、去世日期、在位时间、庙号、谥号、年号
- **Infobox段落**：提取infobox内所有`<p>`标签的文本内容
- **结构化数据**：将提取的信息存储在 `infobox_data` 字典中

#### 人物信息提取
- **基本字段**：别名、出生、去世、职位/官职
- **Infobox段落**：提取infobox内所有`<p>`标签的文本内容
- **结构化数据**：将提取的信息存储在 `infobox_data` 字典中

### 2. 生平章节HTML内容提取

通过新增的 `_extract_biography_section` 方法实现：

**提取范围**：
- 从第一个 `class="mw-heading mw-heading2"` 的div元素开始
- 到下一个相同类名的div元素之间
- 保留所有HTML标签和属性，包括 `<a href="">` 链接

**保存内容**：
- 原始HTML结构，便于后续用LLM进行结构化分析
- 保留所有href链接，方便进一步爬取关联信息

### 3. HTML内容存储Pipeline

新增 `HtmlStoragePipeline` 类：

**存储目录结构**：
```
crawler/data/html/
├── person/          # 人物生平HTML
├── emperor/         # 皇帝生平HTML
└── event/           # 事件HTML
```

**文件命名**：
- HTML文件：`{人物名}_{ID}.html`
- 元数据文件：`{人物名}_{ID}_metadata.json`

**元数据包含**：
- item_id：实体ID
- name：名称
- data_source：数据来源（wikipedia）
- crawl_time：爬取时间
- url：原始URL

### 4. 数据模型更新

为 `Emperor`、`Person`、`Event` 实体类添加了两个新字段：

```python
html_content: Optional[str] = None  # 存储生平HTML原始内容
source_url: Optional[str] = None    # 来源URL
```

## 使用示例

### 运行测试脚本

```bash
python3 test_wiki_extraction.py
```

### 运行爬虫

```bash
# 测试模式（只爬取前3位皇帝）
scrapy crawl wikipedia -s CRAWL_MODE=test

# 全量模式
scrapy crawl wikipedia -s CRAWL_MODE=full
```

### 查看保存的HTML文件

爬取完成后，可以在以下目录查看保存的HTML内容：

```bash
# 查看皇帝生平HTML
ls -lh crawler/data/html/emperor/

# 查看人物生平HTML
ls -lh crawler/data/html/person/
```

## 技术细节

### Infobox提取策略

1. **查找Infobox**：使用 `soup.find('table', class_='infobox')`
2. **段落提取**：遍历所有`<p>`标签
3. **字段提取**：使用正则表达式匹配特定字段的`<th>`标签
4. **数据清洗**：使用 `clean_text` 函数清理文本

### 生平章节提取策略

1. **定位起始点**：查找第一个 `mw-heading mw-heading2`
2. **遍历兄弟元素**：使用 `find_next_sibling()` 遍历
3. **终止条件**：遇到下一个 `mw-heading2` 时停止
4. **保留HTML**：将元素转换为字符串保留原始HTML

### Pipeline处理流程

```
数据爬取 → 数据清洗 → 数据验证 → HTML存储 → SQLite存储 → Neo4j存储
         (100)      (200)      (250)       (300)        (400)
```

## 后续优化方向

1. **LLM结构化处理**
   - 使用大语言模型分析HTML内容
   - 提取结构化的人物事迹、成就等信息

2. **链接追踪**
   - 解析HTML中的href链接
   - 自动爬取相关人物、事件信息

3. **多语言支持**
   - 支持英文维基百科
   - 实现中英文信息互补

4. **增量更新**
   - 检测已爬取的内容
   - 只更新变更的部分

## 注意事项

1. **爬取频率**：已设置下载延迟为2-3秒，避免对维基百科服务器造成压力
2. **HTML存储空间**：HTML文件可能较大，注意磁盘空间
3. **字符编码**：所有文件以UTF-8编码保存
4. **文件名安全**：自动移除文件系统不允许的特殊字符

## 相关文件

- `crawler/spiders/wikipedia_spider.py` - 维基百科爬虫主文件
- `crawler/pipelines/html_storage_pipeline.py` - HTML存储Pipeline
- `crawler/models/entities.py` - 数据实体模型
- `crawler/config/settings.py` - Scrapy配置文件
- `test_wiki_extraction.py` - 提取功能测试脚本
