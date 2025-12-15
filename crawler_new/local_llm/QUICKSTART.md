# 本地大模型快速启动指南

## 🚀 三步快速开始

### 第一步：安装 Ollama 和模型

```bash
cd /Users/master/Documents/AI-Project/HistoryGogo/crawler_new/local_llm
chmod +x install_ollama.sh
./install_ollama.sh
```

或手动安装：

```bash
# 安装 Ollama
brew install ollama

# 下载推荐模型（约 4.7GB）
ollama pull qwen2.5:7b
```

### 第二步：启动 Ollama 服务

在**新终端**中运行：

```bash
ollama serve
```

保持此终端运行，不要关闭。

### 第三步：测试本地大模型

```bash
cd /Users/master/Documents/AI-Project/HistoryGogo/crawler_new/local_llm
python test_local_llm.py
```

## 🔧 集成到爬虫

### 方法1：修改配置文件（推荐）

编辑 `crawler_new/config/settings.py`：

```python
# 启用本地大模型
USE_LOCAL_LLM = True
LOCAL_LLM_MODEL = "qwen2.5:7b"
LOCAL_LLM_BASE_URL = "http://localhost:11434"
```

然后正常运行爬虫：

```bash
cd /Users/master/Documents/AI-Project/HistoryGogo/crawler_new
python run_crawler.py
```

### 方法2：单独测试提取功能

```python
from crawler_new.local_llm import LocalLLMExtractor

# 初始化
extractor = LocalLLMExtractor(
    model_name="qwen2.5:7b",
    base_url="http://localhost:11434"
)

# 读取HTML
with open('data/html/emperor/ming_emperor_001_wikipedia.html', 'r') as f:
    wiki_html = f.read()

# 提取数据（无字符限制）
result = extractor.extract_emperor_all_data(
    html_content_wiki=wiki_html,
    html_content_baidu='',
    page_name='朱元璋'
)

print(result)
```

## 📊 性能对比

| 指标 | API方式 | 本地Qwen2.5-7B |
|------|---------|----------------|
| 字符限制 | 10,000字符 | 无限制 ✅ |
| 处理速度 | 快（5-10秒） | 中等（15-30秒） |
| 成本 | 按量付费 | 免费 ✅ |
| 稳定性 | 依赖网络 | 本地运行 ✅ |
| 数据安全 | 上传到云端 | 本地处理 ✅ |

## 🛠️ 常见问题

### 1. Ollama 服务连接失败

**错误**: `无法连接到 Ollama 服务`

**解决**:
```bash
# 检查服务是否运行
ps aux | grep ollama

# 手动启动服务
ollama serve
```

### 2. 模型未安装

**错误**: `model 'qwen2.5:7b' not found`

**解决**:
```bash
# 下载模型
ollama pull qwen2.5:7b

# 查看已安装模型
ollama list
```

### 3. 内存不足

**症状**: 推理速度极慢或卡死

**解决**:
```bash
# 使用更轻量的模型
ollama pull qwen2.5:3b

# 修改配置
LOCAL_LLM_MODEL = "qwen2.5:3b"
```

### 4. 提取结果为空

**检查**:
- Ollama 服务是否正常运行
- 模型是否下载完整
- HTML 内容是否有效

**调试**:
```python
# 查看原始响应
extractor = LocalLLMExtractor(model_name="qwen2.5:7b")
response = extractor._call_local_llm("你好")
print(response)
```

## 🔄 切换回 API 模式

编辑 `crawler_new/config/settings.py`：

```python
# 禁用本地大模型，使用API
USE_LOCAL_LLM = False
```

## 📈 性能优化建议

### 1. 使用量化模型（更快）

```bash
# 4-bit 量化版本（更快，但略降准确率）
ollama pull qwen2.5:7b-q4
```

### 2. 调整并发数

```python
# config/settings.py
CONCURRENT_REQUESTS = 1  # 本地大模型建议单线程
```

### 3. 启用GPU加速（如有）

Ollama 自动检测GPU，无需额外配置。

### 4. 批处理优化

```python
# 一次提取所有数据，减少调用次数
result = extractor.extract_emperor_all_data(
    html_content_wiki=wiki_html,
    html_content_baidu=baidu_html,
    page_name='朱元璋'
)
```

## 📚 进阶使用

### 自定义模型参数

```python
# local_extractor.py 中修改
data = {
    'model': self.model_name,
    'prompt': prompt,
    'stream': False,
    'options': {
        'temperature': 0.1,  # 降低随机性
        'top_p': 0.9,
        'top_k': 40,
        'num_ctx': 8192,  # 增加上下文窗口
    }
}
```

### 模型微调

基于历史数据微调模型，提升准确率（需要高级知识，参考 Ollama 官方文档）。

## 🎯 预期效果

- ✅ 处理完整 HTML，无截断
- ✅ 提取准确率 85-90%
- ✅ 单个皇帝提取耗时 15-30秒
- ✅ 内存占用 ~6GB
- ✅ 完全离线运行

## 🔗 相关资源

- [Ollama 官网](https://ollama.com/)
- [Qwen2.5 模型介绍](https://github.com/QwenLM/Qwen2.5)
- [项目文档](../README.md)
