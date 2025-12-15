# Crawler_new 更新总结

## 🎯 本次更新内容

### 1. **双源融合提取**

#### 更新前
- 单独处理 Wikipedia 或百度百科的 HTML
- 两个数据源的数据相互独立

#### 更新后 ✅
- **同时传入**两个数据源的 HTML 给千问大模型
- 大模型将两份资料**互为补充**，形成更完整准确的数据
- Pipeline 自动缓存 HTML，等待双源都爬取完毕后统一处理

**核心改动**：
```python
# 旧版：单源提取
extract_emperor_info(html_content, page_name, data_source)

# 新版：双源融合
extract_emperor_info(html_content_wiki, html_content_baidu, page_name)
```

---

### 2. **生平事迹数据格式优化**

#### 更新前
```json
{
  "时间": "1368年",
  "事件": "朱元璋在应天府称帝",
  "事件链接": "https://...",
  "人物": ["李善长", "刘基"],
  "人物链接": ["https://...", "https://..."],
  "地点": "应天府"
}
```

#### 更新后 ✅
```json
{
  "时间": "1328年10月29日（元天历元年九月十八日）",
  "事件": "出生于贫农家庭，原名朱重八，后改名朱兴宗。出身寒微为其日后重农、严惩贪腐埋下思想基础。",
  "事件影响": "塑造了朱元璋的平民意识和反腐决心",
  "人物": [
    {"姓名": "朱五四", "关系": "父", "链接": "https://..."},
    {"姓名": "陈氏", "关系": "母", "链接": "https://..."}
  ],
  "地点": "濠州钟离县东乡（今安徽省凤阳县小溪河镇燃灯寺村）"
}
```

**改进点**：
1. ✅ **时间格式**：精确到年月日 + 古代年号
2. ✅ **事件描述**：更详细（200字内）
3. ✅ **新增字段**：`事件影响`（简述历史影响）
4. ✅ **人物结构**：对象数组，包含`姓名`、`关系`、`链接`
5. ✅ **地点格式**：古代地名 + 今属地名

---

## 📁 修改的文件

### 1. [`utils/qwen_extractor.py`](file:///Users/master/Documents/AI-Project/HistoryGogo/crawler_new/utils/qwen_extractor.py)

**主要改动**：
- ✅ `extract_emperor_info()`: 参数改为双源 HTML
- ✅ `extract_emperor_events()`: 参数改为双源 HTML
- ✅ 新增 `_build_emperor_prompt_dual_source()`: 双源融合 prompt
- ✅ 新增 `_build_events_prompt_dual_source()`: 双源事迹提取 prompt
- ✅ 优化事迹数据格式的 prompt

### 2. [`pipelines/qwen_extraction_pipeline.py`](file:///Users/master/Documents/AI-Project/HistoryGogo/crawler_new/pipelines/qwen_extraction_pipeline.py)

**主要改动**：
- ✅ 新增 `html_cache` 缓存机制
- ✅ `process_item()`: 等待双源都完成后再调用大模型
- ✅ `_extract_emperor_dual_source()`: 双源融合提取方法
- ✅ `_extract_links_from_events()`: 适配新的人物数据结构
- ✅ 新增 `_detect_source_from_url()`: 自动检测链接来源

### 3. [`README.md`](file:///Users/master/Documents/AI-Project/HistoryGogo/crawler_new/README.md)

**更新内容**：
- ✅ 更新核心特性说明
- ✅ 更新数据提取示例

### 4. [`QUICKSTART.md`](file:///Users/master/Documents/AI-Project/HistoryGogo/crawler_new/QUICKSTART.md)

**更新内容**：
- ✅ 强调双源融合的推荐使用方式
- ✅ 说明双源融合的优势

---

## 🚀 使用方法

### 推荐用法：双源融合

```bash
cd crawler_new
python run_crawler.py --source both --mode test
```

**执行流程**：
1. 爬取朱元璋的 Wikipedia 页面 → 保存 HTML → 缓存
2. 爬取朱元璋的百度百科页面 → 保存 HTML → 缓存
3. **两个数据源都完成后**，调用千问大模型融合处理
4. 提取结构化数据（皇帝信息 + 生平事迹）
5. 递归爬取关联的人物、事件页面

---

## 📊 数据对比

### 单源 vs 双源融合

| 特性 | 单源提取 | 双源融合 ✅ |
|------|---------|------------|
| **数据来源** | Wikipedia 或百度百科 | Wikipedia + 百度百科 |
| **数据完整性** | 受限于单一来源 | 互为补充，更完整 |
| **准确性** | 依赖单一来源 | 交叉验证，更准确 |
| **处理方式** | 单独处理 | 统一融合处理 |
| **API 调用次数** | 2次（每个源1次） | 1次（融合后处理） |

### 数据格式对比

| 字段 | 旧格式 | 新格式 ✅ |
|------|--------|----------|
| **时间** | "1368年" | "1368年1月23日（洪武元年正月初四）" |
| **事件影响** | ❌ 无 | ✅ "确立了明朝的政治制度" |
| **人物结构** | 数组 `["李善长"]` | 对象 `[{"姓名":"李善长", "关系":"大臣", "链接":"..."}]` |
| **地点** | "应天府" | "应天府（今南京市）" |

---

## 🎓 技术亮点

### 1. HTML 缓存机制

```python
# 使用字典缓存双源 HTML
self.html_cache = {
    "emperor_朱元璋": {
        "wikipedia": "<html>...</html>",
        "baidu": "<html>...</html>"
    }
}
```

**优势**：
- 等待双源都完成后再处理
- 避免重复调用 API
- 提高数据融合效果

### 2. 智能链接提取

```python
# 自动检测链接来源
def _detect_source_from_url(self, url: str) -> str:
    if 'wikipedia' in url:
        return 'wikipedia'
    elif 'baidu' in url:
        return 'baidu'
```

**优势**：
- 自动识别人物、事件链接的来源
- 递归爬取时使用对应的数据源

### 3. Prompt 优化

```
=== 维基百科内容 ===
{cleaned_wiki[:3500]}

=== 百度百科内容 ===
{cleaned_baidu[:3500]}

请将两份资料互为补充，形成更完整准确的数据...
```

**优势**：
- 明确指示大模型融合两份资料
- 限制长度避免超出 token 限制
- 提高提取准确性

---

## ⚠️ 注意事项

1. **运行模式**：建议使用 `--source both` 获得最佳效果
2. **API 调用**：双源融合会减少 API 调用次数（1次 vs 2次）
3. **处理时间**：等待双源都完成后再处理，可能稍慢
4. **数据质量**：融合后的数据更完整，但依赖大模型理解能力

---

## 📝 后续计划

- [ ] 完善人物信息提取（`extract_person_info`）
- [ ] 完善事件信息提取（`extract_event_info`）
- [ ] 实现 SQLite 和 Neo4j 存储逻辑
- [ ] 添加数据去重与合并策略
- [ ] 优化 Prompt，提高提取准确性

---

**更新时间**：2025-12-14  
**更新版本**：v1.1  
**更新内容**：双源融合 + 数据格式优化
