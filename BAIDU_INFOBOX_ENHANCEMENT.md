# 百度百科爬虫 Infobox 表格提取增强

## 概述

本次更新为百度百科爬虫添加了完整的 **Infobox 表格 `<tr>` 标签解析** 功能，并在整个爬取流程中添加了详细的日志记录，提升了数据提取的完整性和可调试性。

---

## 主要改进

### 1. ✅ 新增 `_extract_infobox_table` 方法

#### 功能说明
- 专门解析百度百科的基础信息表格（`.basic-info`）
- 按照 `<tr>` 标签逐行提取字段
- 支持多种选择器，兼容不同版本的百度百科页面结构

#### 提取的字段

**自动识别并提取：**
- ✓ 出生日期（出生日期、出生时间、出生、生于）
- ✓ 去世日期（逝世日期、逝世时间、逝世、卒于、去世）
- ✓ 在位时间（在位时间、在位、统治时间）
- ✓ 庙号
- ✓ 谥号
- ✓ 年号
- ✓ 陵寝（陵墓、陵寝）
- ✓ 皇后
- ✓ 画像URL（从表格中的 `<img>` 标签提取）

**通用字段：**
- 所有 `<tr>` 行的字段都会被提取并存储到 `infobox_data` 字典中
- 便于后续扩展和分析

#### 代码位置
`crawler/spiders/baidu_baike_spider.py` 第 363-498 行

#### 核心逻辑
```python
# 1. 查找基础信息表格
selectors = ['.basic-info', '.basicInfo-block table', 'table.infobox', '.lemma-table']

# 2. 遍历所有 <tr> 行
for row in rows:
    th = row.find(['th', 'dt'])  # 表头
    td = row.find(['td', 'dd'])  # 表数据
    
    field_name = clean_text(th.get_text())
    field_value = clean_text(td.get_text())
    
    # 3. 存储到 infobox_data
    data['infobox_data'][field_name] = field_value
    
    # 4. 根据字段名智能识别并解析
    if '出生' in field_name:
        data['birth_date'] = self.date_parser.parse_chinese_date(field_value)
```

---

### 2. ✅ 完善的日志系统

#### 日志层级

**INFO 级别：** 关键流程节点
- 🚀 爬虫启动/关闭信息
- 👑 皇帝页面解析开始/结束
- 📖 事件页面解析开始/结束
- 👤 人物页面解析开始/结束
- ✅ 数据提取成功信息
- 📊 提取结果统计

**DEBUG 级别：** 详细执行步骤
- 🔍 各个提取方法的执行过程
- ✓ 每个字段的提取结果
- 📌 Infobox 每一行的解析详情

**ERROR 级别：** 错误信息
- ❌ 解析失败
- 堆栈跟踪信息

#### 日志示例

```log
================================================================================
👑 开始解析皇帝: 明太祖
   URL: https://baike.baidu.com/item/明太祖
   状态码: 200
================================================================================
  📋 开始提取皇帝详细信息...
  🔍 尝试从JSON提取数据...
  → JSON提取未成功，使用传统DOM解析方式
    🔍 开始DOM解析...
    ✓ 找到基础信息框
    ✓ 提取出生日期: 1328年10月29日
    ✓ 提取去世日期: 1398年6月24日
    ✓ 提取了 3 段简介
    ✓ 简介总长度: 456 字符
  🔍 提取infobox表格数据...
    ✓ 找到表格: .basic-info
    📊 找到 10 行数据
    📌 [1] 中文名: 明太祖...
    📌 [2] 庙号: 太祖...
    ✓ 从表格提取庙号: 太祖
    📌 [3] 年号: 洪武...
    ✓ 从表格提取年号: 洪武
    ✓ Infobox表格提取完成，共 15 个字段
  📊 提取结果统计:
     - 出生日期: ✓
     - 去世日期: ✓
     - 简介长度: 456 字符
     - 成就长度: 0 字符
     - 画像URL: ✓
     - Infobox字段: 15 项
  🔨 创建Emperor实体: ming_emperor_001
  ✓ Emperor实体创建成功
✅ 成功提取皇帝数据: 明太祖
```

---

### 3. ✅ 数据模型更新

#### Emperor 实体增加字段
```python
html_content: Optional[str] = None  # 存储生平HTML原始内容
source_url: Optional[str] = None    # 来源URL
```

#### Person 和 Event 实体同步更新
- 添加 `source_url` 字段记录数据来源
- 便于数据追溯和更新

---

### 4. ✅ 错误处理增强

**每个提取方法都添加了：**
- `try-except` 异常捕获
- 详细的错误日志
- 堆栈跟踪信息（DEBUG级别）
- 错误计数统计

**示例：**
```python
try:
    # 提取逻辑
    ...
except Exception as e:
    self.logger.error(f"❌ 提取失败: {str(e)}")
    import traceback
    self.logger.debug(f"错误堆栈: {traceback.format_exc()}")
```

---

## 测试验证

### 测试脚本
`test_baidu_infobox.py`

### 测试结果
```
📈 测试通过率: 10/10 (100%)

验证项目：
  ✓ 庙号             : 通过
  ✓ 年号             : 通过
  ✓ 出生日期           : 通过
  ✓ 去世日期           : 通过
  ✓ 画像URL          : 通过
  ✓ Infobox字段数     : 通过
  ✓ 在位时间           : 通过
  ✓ 谥号             : 通过
  ✓ 陵寝             : 通过
  ✓ 皇后             : 通过
```

---

## 使用方法

### 运行爬虫

```bash
# 测试模式（爬取1位皇帝）
scrapy crawl baidu_baike -a crawl_mode=test -a test_emperor_count=1

# 全量模式（爬取所有皇帝）
scrapy crawl baidu_baike -a crawl_mode=full

# 自定义测试数量
scrapy crawl baidu_baike -a crawl_mode=test -a test_emperor_count=3
```

### 查看日志

```bash
# 实时查看日志
tail -f crawler/data/logs/crawler.log

# 查看最近的日志
tail -100 crawler/data/logs/crawler.log
```

### 测试提取功能

```bash
python3 test_baidu_infobox.py
```

---

## 提取数据示例

### Infobox 字段示例

```python
{
    'name': '明太祖',
    'temple_name': '太祖',
    'reign_title': '洪武',
    'birth_date': date(1328, 10, 29),
    'death_date': date(1398, 6, 24),
    'portrait_url': 'https://example.com/image.jpg',
    'infobox_data': {
        '中文名': '明太祖',
        '别名': '朱元璋、洪武帝',
        '庙号': '太祖',
        'temple_name': '太祖',
        '谥号': '高皇帝',
        'posthumous_name': '高皇帝',
        '年号': '洪武',
        'era_name': '洪武',
        '出生日期': '1328年10月29日',
        '逝世日期': '1398年6月24日',
        '在位时间': '1368年1月23日－1398年6月24日',
        'reign_period': '1368年1月23日－1398年6月24日',
        '陵寝': '明孝陵',
        'tomb': '明孝陵',
        '皇后': '孝慈高皇后马氏',
        'empress': '孝慈高皇后马氏',
        'portrait_url': 'https://example.com/image.jpg'
    }
}
```

---

## 技术亮点

1. **智能字段识别**
   - 通过关键词匹配自动识别字段类型
   - 支持多种字段名称变体（如：出生日期、出生时间、生于）

2. **多选择器兼容**
   - 支持 `.basic-info`、`.basicInfo-block table`、`table.infobox` 等多种选择器
   - 提高对不同版本百度百科页面的兼容性

3. **完整的数据保留**
   - 所有字段都存储在 `infobox_data` 中
   - 既有结构化字段，也保留原始文本

4. **图片URL处理**
   - 自动处理相对路径（`//`、`/`）
   - 转换为完整的HTTPS URL

5. **日志emoji标识**
   - 使用emoji使日志更直观
   - 便于快速定位问题

---

## 注意事项

1. **百度百科反爬**
   - 已设置下载延迟：5秒
   - 随机化延迟：开启
   - 并发请求：4个

2. **字段名称变化**
   - 百度百科可能会更新页面结构
   - 已使用关键词匹配增强鲁棒性

3. **日期解析**
   - 使用 `DateParser` 解析中文日期
   - 支持多种日期格式

---

## 文件清单

### 修改的文件
- ✅ `crawler/spiders/baidu_baike_spider.py`
  - 新增 `_extract_infobox_table` 方法
  - 增强所有解析方法的日志
  - 更新实体创建方法添加 `source_url`

### 新增的文件
- ✅ `test_baidu_infobox.py` - 测试脚本
- ✅ `BAIDU_INFOBOX_ENHANCEMENT.md` - 本文档

---

## 后续优化建议

1. **HTML内容存储**
   - 保存整个页面HTML供后续LLM分析
   - 类似维基百科爬虫的实现

2. **增量更新**
   - 检测已爬取的数据
   - 只更新有变化的内容

3. **字段扩展**
   - 根据实际需求添加更多字段识别规则
   - 如：子女、前任、继任等

4. **数据验证**
   - 添加字段完整性验证
   - 标记缺失字段

---

## 总结

本次更新完成了：

1. ✅ **完整的 `<tr>` 标签解析** - 提取所有infobox表格字段
2. ✅ **智能字段识别** - 自动识别10+种关键字段
3. ✅ **详细的日志系统** - 覆盖整个爬取流程
4. ✅ **错误处理增强** - 完善的异常捕获和日志记录
5. ✅ **测试验证** - 100%通过率

所有功能已测试验证，可以直接用于生产环境的数据爬取。
