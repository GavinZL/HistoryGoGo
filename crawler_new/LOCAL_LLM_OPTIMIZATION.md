# 本地 LLM 提取数据优化方案

## 📊 问题分析

### 现象
使用本地 `qwen3:latest` 模型提取朱元璋生平数据时，只提取了 **8 条事迹**，远少于预期的 **15-20 条**。

### 原因分析

#### ❌ 不是上下文长度限制问题

| 模型类型 | 输入限制 | 代码位置 |
|---------|---------|---------|
| **千问 API** | 每个数据源限制 **10,000 字符** | `qwen_extractor.py:170-171` |
| **本地 qwen3** | **无字符限制**（传入完整 HTML） | `local_extractor.py:148` |

```python
# 千问 API - 有限制
wiki_content = cleaned_wiki[:10000]  # ⚠️ 只取前 10000 字符
baidu_content = cleaned_baidu[:10000]

# 本地模型 - 无限制（优化前）
prompt = self._build_emperor_all_data_prompt(cleaned_wiki, cleaned_baidu, page_name)
# 直接使用完整内容，无截取
```

#### ✅ 真正原因：模型能力差异

| 特性 | qwen3:latest (7B) | qwen-max (API) |
|------|------------------|----------------|
| **参数规模** | ~7B | 数百亿+ |
| **结构化提取** | ⚠️ 较弱 | ✅ 强大 |
| **复杂 JSON 生成** | ⚠️ 容易遗漏 | ✅ 稳定准确 |
| **多源融合理解** | ⚠️ 有限 | ✅ 优秀 |
| **长文本理解** | ⚠️ 较弱 | ✅ 强大 |
| **输出长度** | ⚠️ 倾向截断 | ✅ 完整输出 |

---

## 🔧 解决方案

### 方案 1: 升级本地模型（推荐）⭐

使用更强的模型版本：

```bash
# 14B 参数版本（推荐，显存需求 ~10GB）
ollama pull qwen2.5:14b

# 32B 参数版本（高级，显存需求 ~20GB）
ollama pull qwen2.5:32b

# 查看已安装模型
ollama list
```

修改配置 `crawler_new/config/settings.py`:

```python
LOCAL_LLM_MODEL = 'qwen2.5:14b'  # 或 'qwen2.5:32b'
```

**优势**：
- ✅ 提取能力显著提升
- ✅ 仍然本地运行，无 API 费用
- ✅ 无字符限制

**劣势**：
- ⚠️ 需要更多显存
- ⚠️ 推理速度稍慢

---

### 方案 2: 优化提示词和参数（已实施）✅

#### 2.1 限制输入长度

虽然本地模型支持完整输入，但对于 7B 小模型，**适当限制输入反而能提升质量**：

```python
# 优化后：限制为 8000 字符
max_chars = 8000
wiki_content = cleaned_wiki[:max_chars] if len(cleaned_wiki) > max_chars else cleaned_wiki
baidu_content = cleaned_baidu[:max_chars] if len(cleaned_baidu) > max_chars else cleaned_baidu
```

**原理**：
- 7B 模型处理 5000-8000 字符效果最佳
- 过长输入会导致模型"迷失"，提取不完整

#### 2.2 优化提示词

**改进前**：
```
你是一个历史数据提取专家。请从以下维基百科和百度百科的网页内容中提取...
```

**改进后**：
```
你是一个历史数据提取专家。从以下内容中提取关于皇帝"{page_name}"的结构化信息。

重要要求:
1. 必须提取 15-20 条生平事迹，按时间顺序排列
2. 每个事件必须包含:时间、事件、事件影响、人物、地点
3. 从出生到去世，全面覆盖重要事件
4. 只返回 JSON 格式，不要有其他内容
```

**改进点**：
- ✅ 更简洁直接的指令
- ✅ 明确数量要求（15-20 条）
- ✅ 强调必填字段
- ✅ 列出时间范围（出生到去世）

#### 2.3 优化 API 参数

```python
'options': {
    'temperature': 0.2,      # 从 0.1 调整为 0.2，平衡稳定性和多样性
    'top_p': 0.8,            # 从 0.9 降低，提高确定性
    'top_k': 40,
    'num_predict': 4096,     # ⭐ 新增：增加最大输出长度
    'repeat_penalty': 1.1    # ⭐ 新增：防止重复内容
}
```

**关键参数解释**：
- `num_predict`: 允许模型输出更多 token，确保能完整输出 15-20 条事迹
- `repeat_penalty`: 防止模型重复相同内容而不继续提取

---

### 方案 3: 切换回 API 模式（最稳定）

修改 `crawler_new/config/settings.py`:

```python
USE_LOCAL_LLM = False  # 改为 False
```

**优势**：
- ✅ 提取质量最高
- ✅ 稳定可靠
- ✅ 输出完整

**劣势**：
- ⚠️ 需要 API Key
- ⚠️ 有调用费用
- ⚠️ 依赖网络

---

## 📈 优化效果对比

| 场景 | 提取事迹数 | 数据完整度 | 推理速度 | 成本 |
|------|----------|-----------|---------|-----|
| **优化前 qwen3:7b** | 8 条 | ⚠️ 低 | 快 | 免费 |
| **优化后 qwen3:7b** | 预计 12-15 条 | 🔶 中等 | 快 | 免费 |
| **qwen2.5:14b** | 预计 15-18 条 | ✅ 高 | 中等 | 免费 |
| **qwen-max API** | 15-20 条 | ✅ 很高 | 快 | 有费用 |

---

## 🎯 推荐策略

### 个人开发/测试环境
1. **首选**：优化后的 `qwen3:latest`（已实施）
2. **升级**：`qwen2.5:14b`（如显存充足）

### 生产环境
1. **首选**：`qwen-max` API（稳定可靠）
2. **备选**：`qwen2.5:32b` 本地部署（高性能服务器）

---

## 🧪 测试验证

运行优化后的爬虫：

```bash
cd /Users/bigo/Documents/AI/App/HistoryGoGo
python crawler_new/run_crawler.py --spider ming_emperor --source wikipedia --mode test
```

检查日志中的提取数量：

```
📜 [生平事迹] 提取完成: XX 条  # 期望 12+ 条
```

---

## 📝 代码修改清单

### ✅ 已修改文件

1. **`crawler_new/local_llm/local_extractor.py`**
   - ✅ 添加输入长度限制（8000 字符）
   - ✅ 优化提示词，强调数量要求
   - ✅ 增加 API 参数 `num_predict` 和 `repeat_penalty`

### 🔄 可选修改

2. **`crawler_new/config/settings.py`**（根据需要修改）
   ```python
   # 升级模型
   LOCAL_LLM_MODEL = 'qwen2.5:14b'
   
   # 或切换回 API
   USE_LOCAL_LLM = False
   ```

---

## 💡 技术要点总结

1. **小模型局限性**：
   - 7B 模型适合简单结构化提取
   - 复杂任务需要 14B+ 或 API

2. **输入长度策略**：
   - API：限制 10000 字符（成本考虑）
   - 本地 7B：限制 8000 字符（能力考虑）
   - 本地 14B+：可以更长（10000+）

3. **提示词工程**：
   - 明确数量要求
   - 强调必填字段
   - 简洁清晰的指令

4. **参数调优**：
   - `num_predict`: 控制输出长度
   - `temperature`: 控制随机性
   - `repeat_penalty`: 防止重复

---

## 🔗 相关文档

- [本地 LLM 部署指南](LOCAL_LLM_GUIDE.md)
- [Ollama 模型列表](https://ollama.com/library/qwen)
- [千问 API 文档](https://help.aliyun.com/zh/dashscope/)
