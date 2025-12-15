# 更新日志 - 关键日志添加

## 📅 更新时间
2025-12-14

## 🎯 更新目标
在整个数据获取流程中添加关键日志，确保每个环节都有清晰的日志输出，方便追踪和调试。

## ✅ 已完成的工作

### 1. **Spider 日志增强** (`spiders/ming_emperor_spider.py`)

#### 爬虫启动阶段
```
🚀 [爬虫启动] Spider: ming_emperor
   数据源: wikipedia
   爬取模式: test
📋 [爬取范围] 测试模式：只爬取前 3 位皇帝
📊 [统计] 待爬取皇帝: 3 位
   1. 朱元璋 (明太祖) - 洪武
   2. 朱允炆 (明惠帝) - 建文
   3. 朱棣 (明成祖) - 永乐
✅ [请求生成] 共生成 3 个爬取请求
```

#### HTTP 请求创建
```
👑 [请求创建] 皇帝: 朱元璋 (wikipedia)
   URL: https://zh.wikipedia.org/wiki/朱元璋
   朝代顺序: 1
   庙号: 明太祖
   年号: 洪武
```

#### HTTP 响应处理
```
✅ [HTTP响应] 成功获取HTML
   皇帝: 朱元璋
   数据源: wikipedia
   状态码: 200
   HTML大小: 413635 字符
📦 [Item创建] 生成 HtmlPageItem
   page_id: ming_emperor_001_wikipedia
   page_type: emperor
   page_name: 朱元璋
➡️  [Pipeline] 提交 HtmlPageItem 到 Pipeline 处理链
```

#### 递归爬取
```
📰 [事件爬取] 成功获取事件HTML
   事件: 胡惟庸案
   数据源: wikipedia
   递归深度: 1
   状态码: 200
   HTML大小: 156234 字符

👤 [人物爬取] 成功获取人物HTML
   人物: 汤和
   数据源: wikipedia
   递归深度: 1
   状态码: 200
   HTML大小: 142567 字符
```

---

### 2. **Pipeline-1: HTML 存储日志** (`pipelines/html_storage_pipeline.py`)

#### Pipeline 启动
```
📁 [Pipeline-1] HtmlStoragePipeline 启动
   存储路径: crawler_new/data/html
   ✅ 目录已就绪: crawler_new/data/html/emperor
   ✅ 目录已就绪: crawler_new/data/html/event
   ✅ 目录已就绪: crawler_new/data/html/person
```

#### 处理 Item
```
💾 [Pipeline-1] HTML存储开始
   page_id: ming_emperor_001_wikipedia
   page_name: 朱元璋
   data_source: wikipedia
   HTML大小: 413635 字符
   ✅ HTML文件: crawler_new/data/html/emperor/ming_emperor_001_wikipedia.html
   ✅ 元数据文件: crawler_new/data/html/emperor/ming_emperor_001_wikipedia_metadata.json
✅ [Pipeline-1] HTML存储完成
```

#### 错误处理
```
❌ [Pipeline-1] HTML存储失败
   page_id: ming_emperor_001_wikipedia
   错误: Permission denied
```

---

### 3. **Pipeline-2: 千问提取日志** (`pipelines/qwen_extraction_pipeline.py`)

#### Pipeline 启动
```
🤖 [Pipeline-2] QwenExtractionPipeline 启动
   ✅ 千问大模型已初始化
   模型: qwen-max
   API Key: sk-1234567...
```

#### 缓存 HTML（等待双源）
```
🤖 [Pipeline-2] 千问提取开始
   page_id: ming_emperor_001_wikipedia
   page_name: 朱元璋
   data_source: wikipedia
   💾 缓存HTML: 朱元璋 (wikipedia)
   📋 数据源状态: Wikipedia=✅, Baidu=❌
   ⏳ 等待另一个数据源完成...
   已有: wikipedia
```

#### 双源完成，开始提取
```
🤖 [Pipeline-2] 千问提取开始
   page_id: ming_emperor_001_baidu
   page_name: 朱元璋
   data_source: baidu
   💾 缓存HTML: 朱元璋 (baidu)
   📋 数据源状态: Wikipedia=✅, Baidu=✅
   ✅ 双源已完成，开始融合提取
```

#### 大模型提取详细过程
```
🤖 [大模型提取] 开始提取皇帝信息
   皇帝: 朱元璋
   Wikipedia HTML: 413635 字符
   Baidu HTML: 387542 字符

📑 [Step 1] 调用大模型提取皇帝基本信息...
   ✅ 皇帝信息提取完成
   皇帝: 朱元璋
   庙号: 明太祖
   年号: 洪武
   出生: 1328年10月21日（元天历元年九月十八日）
   去世: 1398年6月24日（洪武三十一年闰五月初十）

📜 [Step 2] 调用大模型提取生平事迹...
   ✅ 生平事迹提取完成: 18 条
      1. 1328年10月29日（元天历元年九月十八日） - 出生于贫农家庭，原名朱重八...
      2. 1344年（至正四年） - 淮北大旱，父母兄长相继去世...
      3. 1352年 - 受儿时好友汤和邀请投奔郭子兴...
      ... 还有 15 条事迹

🔗 [Step 3] 提取链接信息...
   ✅ 链接提取完成
   事件链接: 5 个
   人物链接: 12 个

📦 [Step 4] 创建 ExtractedDataItem
   ✅ ExtractedDataItem 创建完成

✅ [Pipeline-2] 千问提取完成: 朱元璋
```

#### 错误处理
```
❌ [Pipeline-2] 千问提取失败
   page_id: ming_emperor_001
   错误: API rate limit exceeded
```

---

## 📊 日志符号说明

| 符号 | 含义 | 使用场景 |
|------|------|----------|
| 🚀 | 启动 | 爬虫启动 |
| 👑 | 皇帝 | 皇帝相关操作 |
| 📰 | 事件 | 事件相关操作 |
| 👤 | 人物 | 人物相关操作 |
| 📁 | 文件 | 文件存储 |
| 💾 | 缓存 | HTML 缓存 |
| 🤖 | AI | 大模型提取 |
| 🔗 | 链接 | 链接提取/递归爬取 |
| ✅ | 成功 | 操作成功 |
| ❌ | 失败 | 操作失败 |
| ⚠️ | 警告 | 警告信息 |
| ⏳ | 等待 | 等待其他资源 |
| 📋 | 统计 | 统计信息 |
| 📊 | 数据 | 数据统计 |
| 📦 | 打包 | Item 创建 |
| ➡️ | 流转 | 数据流转 |
| 📑 | 文档 | 基本信息 |
| 📜 | 卷轴 | 事迹信息 |

---

## 🔍 日志级别

- **INFO**: 正常流程日志（默认显示）
- **WARNING**: 警告信息（跳过、缺失配置等）
- **ERROR**: 错误信息（失败、异常等）
- **DEBUG**: 调试详细信息（需手动启用）

---

## 📂 相关文件

### 修改的文件
1. `spiders/ming_emperor_spider.py` - 添加 Spider 日志
2. `pipelines/html_storage_pipeline.py` - 添加 HTML 存储日志
3. `pipelines/qwen_extraction_pipeline.py` - 添加千问提取日志

### 新建的文件
1. `LOGGING_GUIDE.md` - 日志完整指南（375行）
2. `CHANGELOG_LOGGING.md` - 本更新日志

### 更新的文件
1. `README.md` - 添加日志查看说明

---

## 📝 使用示例

### 查看实时日志
```bash
tail -f crawler_new/data/logs/crawler.log
```

### 只查看错误日志
```bash
grep "❌" crawler_new/data/logs/crawler.log
```

### 查看某个皇帝的日志
```bash
grep "朱元璋" crawler_new/data/logs/crawler.log
```

### 查看 Pipeline 执行流程
```bash
grep "Pipeline" crawler_new/data/logs/crawler.log
```

### 监控双源融合状态
```bash
grep "数据源状态" crawler_new/data/logs/crawler.log
```

---

## 🎯 日志特点

1. **结构化清晰**: 使用分隔线和缩进，层次分明
2. **符号标识**: 使用 emoji 符号快速识别日志类型
3. **关键信息突出**: page_id、page_name、数据源等关键字段
4. **进度追踪**: 显示统计信息、数据源状态、处理步骤
5. **错误详细**: 失败时输出详细错误信息和堆栈跟踪
6. **性能监控**: 显示 HTML 大小、事迹条数、链接数量等

---

## 💡 调试技巧

1. **追踪完整流程**: 通过 page_id 追踪单个页面的完整处理链路
2. **监控双源状态**: 确认双源是否都成功爬取
3. **检查大模型调用**: 查看提取步骤和返回结果
4. **性能分析**: 通过日志时间戳计算各环节耗时
5. **错误定位**: 错误日志包含足够的上下文信息

---

## 📖 更多信息

详细的日志使用说明请参考：[LOGGING_GUIDE.md](LOGGING_GUIDE.md)

---

**更新者**: Qoder AI Assistant  
**版本**: v1.2  
**新增行数**: 约 200 行日志代码 + 375 行文档
