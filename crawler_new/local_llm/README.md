# 本地大模型部署方案

## 系统配置
- CPU: 6核 Intel Core i7 (3.2 GHz)
- 内存: 32 GB DDR4
- 系统: macOS Sequoia 15.4.1

## 推荐方案：Ollama + Qwen2.5-7B

### 为什么选择这个方案？
1. **内存友好**：7B模型量化后占用约4-6GB内存，适合32GB系统
2. **性能优秀**：Qwen2.5系列在中文理解和结构化提取上表现优异
3. **部署简单**：Ollama提供一键安装，无需复杂配置
4. **速度快**：CPU推理优化，响应时间可接受
5. **无字符限制**：本地部署无API调用限制

### 替代方案
- **Qwen2.5-3B**：更轻量，速度更快，但提取质量略低
- **Llama-3.1-8B**：通用能力强，中文稍弱
- **Gemma-7B**：Google开源，性能均衡

## 安装步骤

### 1. 安装 Ollama
```bash
# 方式1：使用官方安装脚本（推荐）
curl -fsSL https://ollama.com/install.sh | sh

# 方式2：使用 Homebrew
brew install ollama
```

### 2. 启动 Ollama 服务
```bash
ollama serve
```

### 3. 下载模型
```bash
# 推荐：Qwen2.5-7B (中文优秀)
ollama pull qwen2.5:7b

# 备选：轻量级版本
ollama pull qwen2.5:3b

# 备选：Llama 3.1 (通用能力强)
ollama pull llama3.1:8b
```

### 4. 测试模型
```bash
ollama run qwen2.5:7b
```

## 使用方法

### Python集成
```python
from crawler_new.local_llm.local_extractor import LocalLLMExtractor

# 初始化
extractor = LocalLLMExtractor(
    model_name="qwen2.5:7b",
    base_url="http://localhost:11434"
)

# 提取数据
result = extractor.extract_emperor_all_data(
    html_content_wiki=wiki_html,
    html_content_baidu=baidu_html,
    page_name="朱元璋"
)
```

### 配置切换
在 `config/settings.py` 中切换：
```python
# 使用本地大模型
USE_LOCAL_LLM = True
LOCAL_LLM_MODEL = "qwen2.5:7b"
LOCAL_LLM_BASE_URL = "http://localhost:11434"

# 或继续使用API（保留）
USE_LOCAL_LLM = False
QWEN_API_KEY = "your_api_key"
```

## 性能对比

| 方案 | 内存占用 | 处理速度 | 字符限制 | 成本 |
|------|---------|---------|---------|------|
| 通义千问API | ~0 MB | 快 | 有限制 | 按量付费 |
| 本地Qwen2.5-7B | ~6 GB | 中等 | 无限制 | 免费 |
| 本地Qwen2.5-3B | ~3 GB | 快 | 无限制 | 免费 |

## 预期效果
- **完整HTML处理**：无字符截断，完整处理维基+百度HTML
- **响应时间**：单次提取约15-30秒（取决于HTML大小）
- **准确率**：结构化提取准确率 85-90%
- **并发能力**：建议单线程处理，避免内存溢出

## 后续优化方向
1. **模型微调**：基于历史数据微调，提升准确率
2. **GPU加速**：如有外置GPU，可大幅提速
3. **模型量化**：使用4bit量化，进一步降低内存占用
4. **批处理优化**：合理调度请求，提升吞吐量
