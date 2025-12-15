"""
本地大模型测试脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from local_extractor import LocalLLMExtractor


def test_connection():
    """测试 Ollama 连接"""
    print("\n" + "="*80)
    print("🧪 测试 1: 测试 Ollama 服务连接")
    print("="*80)
    
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama 服务连接成功")
            print(f"📋 已安装模型: {len(models)} 个")
            for model in models:
                print(f"   - {model.get('name')} ({model.get('size', 0) / 1024 / 1024 / 1024:.2f} GB)")
            return True
        else:
            print(f"❌ Ollama 服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到 Ollama 服务: {str(e)}")
        print(f"\n💡 请先启动 Ollama 服务:")
        print(f"   ollama serve")
        return False


def test_simple_extraction():
    """测试简单提取"""
    print("\n" + "="*80)
    print("🧪 测试 2: 测试简单文本提取")
    print("="*80)
    
    try:
        extractor = LocalLLMExtractor(model_name='qwen2.5:7b')
        
        # 构建测试 prompt
        test_prompt = """请从以下内容中提取结构化信息，返回 JSON 格式：

朱元璋（1328年10月21日－1398年6月24日），濠州钟离县（今安徽凤阳）人，汉族，明朝开国皇帝，庙号太祖，年号洪武。

请返回：
{
  "姓名": "朱元璋",
  "出生": "1328年10月21日",
  "去世": "1398年6月24日",
  "籍贯": "濠州钟离县",
  "朝代": "明朝",
  "庙号": "太祖",
  "年号": "洪武"
}
"""
        
        print("📤 发送测试请求...")
        response = extractor._call_local_llm(test_prompt)
        
        print("📥 收到响应:")
        print(response[:500])
        
        # 尝试解析 JSON
        json_str = extractor._extract_json(response)
        import json
        result = json.loads(json_str)
        
        print("\n✅ JSON 解析成功:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def test_emperor_extraction():
    """测试皇帝信息提取"""
    print("\n" + "="*80)
    print("🧪 测试 3: 测试皇帝信息提取（使用真实HTML）")
    print("="*80)
    
    try:
        # 读取已保存的 HTML 文件
        html_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data/html/emperor/ming_emperor_001_wikipedia.html'
        )
        
        if not os.path.exists(html_file):
            print(f"⚠️  HTML 文件不存在，跳过此测试: {html_file}")
            return False
        
        print(f"📂 读取 HTML: {html_file}")
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"📏 HTML 大小: {len(html_content)} 字符")
        
        # 初始化提取器
        extractor = LocalLLMExtractor(model_name='qwen2.5:7b')
        
        # 提取皇帝基本信息
        print("\n📤 开始提取皇帝信息...")
        emperor_info = extractor.extract_emperor_info(
            html_content_wiki=html_content,
            html_content_baidu='',  # 暂时只用维基
            page_name='朱元璋'
        )
        
        print("\n✅ 提取成功:")
        import json
        print(json.dumps(emperor_info, ensure_ascii=False, indent=2))
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🚀 本地大模型测试套件")
    print("="*80)
    
    results = []
    
    # 测试 1: 连接测试
    results.append(("Ollama 服务连接", test_connection()))
    
    if results[0][1]:
        # 测试 2: 简单提取
        results.append(("简单文本提取", test_simple_extraction()))
        
        # 测试 3: 皇帝信息提取
        results.append(("皇帝信息提取", test_emperor_extraction()))
    
    # 输出测试结果
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！本地大模型已就绪。")
    else:
        print("\n⚠️  部分测试失败，请检查配置。")


if __name__ == '__main__':
    main()
