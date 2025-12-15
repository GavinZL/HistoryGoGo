# 本地大模型部署与使用指南

## 🎯 概述

本地大模型模块已成功部署在 `crawler_new/local_llm/` 目录，用于解决通义千问API字符限制问题。

## 📦 部署内容

### 目录结构
```
crawler_new/local_llm/
├── local_extractor.py           # 核心提取器（与API接口一致）
├── __init__.py                  # 模块初始化
├── README.md                    # 技术方案说明
├── QUICKSTART.md                # 快速启动指南
├── DEPLOYMENT_SUMMARY.md        # 部署总结
├── install_ollama.sh            # 一键安装脚本
├── test_local_llm.py            # 测试套件
├── compare_api_vs_local.py      # 性能对比工具
└── requirements.txt             # 依赖清单
```

## 🚀 三步快速启动

### 1️⃣ 安装 Ollama 和模型

```bash
cd crawler_new/local_llm
chmod +x install_ollama.sh
./install_ollama.sh
```

或手动安装：
```bash
brew install ollama
ollama pull qwen2.5:7b
```

### 2️⃣ 启动 Ollama 服务

在**新终端**窗口运行（保持运行）：
```bash
ollama serve
```

### 3️⃣ 配置并使用

编辑 `crawler_new/config/settings.py`:
```python
USE_LOCAL_LLM = True  # 启用本地大模型
LOCAL_LLM_MODEL = "qwen2.5:7b"
LOCAL_LLM_BASE_URL = "http://localhost:11434"
```

然后正常运行爬虫：
```bash
cd crawler_new
python run_crawler.py
```

## 🧪 测试验证

### 基础测试
```bash
cd crawler_new/local_llm
python test_local_llm.py
```

### 性能对比测试
```bash
python compare_api_vs_local.py
```

## ⚙️ 技术规格

### 推荐配置
- **模型**: Qwen2.5-7B (中文优秀，约4.7GB)
- **内存**: 需要6GB左右（您的32GB完全满足）
- **速度**: 15-30秒/次（取决于HTML大小）
- **优势**: 无字符限制，完整处理HTML

### 替代模型
如需更快速度，可选择轻量版：
```bash
ollama pull qwen2.5:3b
# 修改配置: LOCAL_LLM_MODEL = "qwen2.5:3b"
```

## 📊 核心优势

| 特性 | API方式 | 本地方式 |
|------|---------|---------|
| 字符限制 | 10,000字符 | ✅ 无限制 |
| HTML处理 | 截断 | ✅ 完整 |
| 成本 | 按量付费 | ✅ 免费 |
| 数据安全 | 上传云端 | ✅ 本地处理 |
| 网络依赖 | 需要 | ✅ 离线运行 |

## 🔄 切换模式

### 使用本地大模型
```python
# config/settings.py
USE_LOCAL_LLM = True
```

### 切换回API
```python
# config/settings.py
USE_LOCAL_LLM = False
```

两种模式可随时切换，不影响其他代码。

## 📚 详细文档

- [快速启动](crawler_new/local_llm/QUICKSTART.md)
- [技术方案](crawler_new/local_llm/README.md)
- [部署总结](crawler_new/local_llm/DEPLOYMENT_SUMMARY.md)

## ⚠️ 注意事项

1. **Ollama 必须运行**: 确保 `ollama serve` 在后台运行
2. **模型已下载**: 运行前确认模型已下载完成
3. **单线程推荐**: 本地大模型建议单线程运行，避免内存压力
4. **首次较慢**: 首次加载模型需要时间，后续速度正常

## 🆘 故障排除

### 连接失败
```bash
# 检查服务是否运行
ps aux | grep ollama

# 重启服务
ollama serve
```

### 模型未找到
```bash
# 查看已安装模型
ollama list

# 重新下载
ollama pull qwen2.5:7b
```

### 提取失败
检查测试套件输出：
```bash
cd crawler_new/local_llm
python test_local_llm.py
```

## 🎉 总结

本地大模型已成功集成，核心优势：
- ✅ **解决字符限制**: 完整处理维基+百度HTML
- ✅ **零成本**: 免费使用，无API费用
- ✅ **数据安全**: 敏感数据本地处理
- ✅ **无缝切换**: 一键切换API/本地模式

---

**部署日期**: 2025-12-14  
**版本**: v1.0  
**状态**: ✅ 生产就绪
