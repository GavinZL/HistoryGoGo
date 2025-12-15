# Crawler_new 快速开始指南

## 🚀 5分钟快速上手

### 第一步：配置千问 API Key

编辑 `crawler_new/config/settings.py`：

```python
# 千问大模型配置
QWEN_API_KEY = 'sk-your-api-key-here'  # 👈 填入你的 API Key
```

> 💡 获取 API Key：访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/)

### 第二步：创建数据目录

```bash
mkdir -p crawler_new/data/html/{emperor,event,person}
mkdir -p crawler_new/data/logs
```

### 第三步：运行测试

```bash
cd crawler_new
python run_crawler.py --source wikipedia --mode test
```

这将：
- ✅ 爬取前3位明朝皇帝的 Wikipedia **和**百度百科页面
- ✅ 保存 HTML 到 `data/html/emperor/`
- ✅ 调用千问大模型**融合双源HTML**提取结构化数据
- ✅ 输出日志到控制台

### 预期结果

运行完成后，你会看到：

```
crawler_new/data/html/emperor/
├── ming_emperor_001_wikipedia.html
├── ming_emperor_001_wikipedia_metadata.json
├── ming_emperor_002_wikipedia.html
├── ming_emperor_002_wikipedia_metadata.json
├── ming_emperor_003_wikipedia.html
└── ming_emperor_003_wikipedia_metadata.json
```

## 📊 进阶使用

### 爬取百度百科

```bash
python run_crawler.py --source baidu --mode test
```

### 🌟 双源融合爬取（推荐）

```bash
python run_crawler.py --source both --mode test
```

**双源融合的优势：**
- ✅ 同时下载 Wikipedia 和百度百科的 HTML
- ✅ 千问大模型将两份资料互为补充，形成更完整的数据
- ✅ 提高数据准确性和完整性

### 全量爬取（16位皇帝）

```bash
python run_crawler.py --source wikipedia --mode full
```

### 禁用递归爬取

编辑 `config/settings.py`：

```python
ENABLE_RECURSIVE_CRAWL = False
```

## 🔍 查看提取结果

打开 `data/html/emperor/ming_emperor_001_wikipedia_metadata.json`，你会看到：

```json
{
  "page_type": "emperor",
  "page_id": "ming_emperor_001_wikipedia",
  "page_name": "朱元璋",
  "data_source": "wikipedia",
  "source_url": "https://zh.wikipedia.org/wiki/朱元璋",
  "crawl_time": "2025-12-14T22:45:00",
  "metadata": {
    "temple_name": "明太祖",
    "reign_title": "洪武",
    "dynasty_order": 1
  }
}
```

## ⚠️ 注意事项

1. **API 限流**：千问 API 有调用频率限制，建议测试模式先行
2. **费用**：千问 API 按调用次数收费，注意控制成本
3. **网络**：确保能访问 Wikipedia 和百度百科
4. **依赖**：运行前确保已安装所有依赖：`pip install -r requirements.txt`

## 🐛 常见问题

### Q: API Key 错误

```
❌ 调用千问API失败: 401 Unauthorized
```

**解决**：检查 `QWEN_API_KEY` 是否正确，账户是否有余额。

### Q: 网络连接失败

```
❌ 成功获取 HTML 失败: Connection timeout
```

**解决**：检查网络连接，或使用代理。

### Q: 只想下载 HTML，不调用大模型

**解决**：将 `QWEN_API_KEY` 设为空字符串：

```python
QWEN_API_KEY = ''
```

## 📚 下一步

- 查看完整文档：[README.md](README.md)
- 了解数据流程：查看各个 Pipeline 的代码
- 扩展功能：实现人物、事件的提取逻辑
- 数据库存储：完善 SQLite 和 Neo4j Pipeline

## 🎯 快速测试命令汇总

```bash
# 测试模式 - Wikipedia
python run_crawler.py --source wikipedia --mode test

# 测试模式 - 百度百科
python run_crawler.py --source baidu --mode test

# 测试模式 - 双源
python run_crawler.py --source both --mode test

# 全量模式
python run_crawler.py --source wikipedia --mode full

# 使用 Scrapy 命令
scrapy crawl ming_emperor -s CRAWL_MODE=test
```

祝你使用愉快！🎉
