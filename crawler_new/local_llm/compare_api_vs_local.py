"""
API vs 本地大模型对比测试
"""

import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.qwen_extractor import QwenExtractor
from local_extractor import LocalLLMExtractor


def load_test_html():
    """加载测试HTML"""
    html_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data/html/emperor/ming_emperor_001_wikipedia.html'
    )
    
    if not os.path.exists(html_file):
        print(f"❌ HTML 文件不存在: {html_file}")
        return None
    
    with open(html_file, 'r', encoding='utf-8') as f:
        return f.read()


def test_api(html_content, api_key):
    """测试 API 方式"""
    print("\n" + "="*80)
    print("🌐 测试 API 方式（通义千问）")
    print("="*80)
    
    try:
        extractor = QwenExtractor(api_key=api_key, model='qwen-max')
        
        # 记录开始时间
        start_time = time.time()
        
        # 提取数据
        result = extractor.extract_emperor_all_data(
            html_content_wiki=html_content,
            html_content_baidu='',
            page_name='朱元璋'
        )
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ API 提取成功")
        print(f"⏱️  耗时: {elapsed_time:.2f} 秒")
        print(f"📏 HTML 输入: {len(html_content)} 字符")
        print(f"📏 实际传输: ~10000 字符（截断）")
        print(f"📊 提取结果:")
        print(f"   - 皇帝信息: {len(result.get('emperor_info', {}))} 个字段")
        print(f"   - 生平事迹: {len(result.get('events', []))} 条")
        
        return {
            'success': True,
            'elapsed_time': elapsed_time,
            'result': result,
            'input_chars': len(html_content),
            'truncated': True
        }
    except Exception as e:
        print(f"❌ API 提取失败: {str(e)}")
        return {'success': False, 'error': str(e)}


def test_local(html_content, model_name='qwen2.5:7b'):
    """测试本地大模型"""
    print("\n" + "="*80)
    print("💻 测试本地大模型")
    print("="*80)
    
    try:
        extractor = LocalLLMExtractor(model_name=model_name)
        
        # 记录开始时间
        start_time = time.time()
        
        # 提取数据
        result = extractor.extract_emperor_all_data(
            html_content_wiki=html_content,
            html_content_baidu='',
            page_name='朱元璋'
        )
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ 本地提取成功")
        print(f"⏱️  耗时: {elapsed_time:.2f} 秒")
        print(f"📏 HTML 输入: {len(html_content)} 字符")
        print(f"📏 实际传输: {len(html_content)} 字符（完整）")
        print(f"📊 提取结果:")
        print(f"   - 皇帝信息: {len(result.get('emperor_info', {}))} 个字段")
        print(f"   - 生平事迹: {len(result.get('events', []))} 条")
        
        return {
            'success': True,
            'elapsed_time': elapsed_time,
            'result': result,
            'input_chars': len(html_content),
            'truncated': False
        }
    except Exception as e:
        print(f"❌ 本地提取失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {'success': False, 'error': str(e)}


def compare_results(api_result, local_result):
    """对比两种方式的结果"""
    print("\n" + "="*80)
    print("📊 对比分析")
    print("="*80)
    
    if not api_result.get('success') or not local_result.get('success'):
        print("⚠️  部分测试失败，无法对比")
        return
    
    # 对比表格
    print("\n┌─────────────────┬─────────────┬─────────────┐")
    print("│     指标        │   API方式   │  本地方式   │")
    print("├─────────────────┼─────────────┼─────────────┤")
    print(f"│ 耗时（秒）      │ {api_result['elapsed_time']:>10.2f}  │ {local_result['elapsed_time']:>10.2f}  │")
    print(f"│ 输入字符数      │ {api_result['input_chars']:>10,}  │ {local_result['input_chars']:>10,}  │")
    print(f"│ 是否截断        │ {'是' if api_result['truncated'] else '否':>11} │ {'是' if local_result['truncated'] else '否':>11} │")
    
    api_events = len(api_result['result'].get('events', []))
    local_events = len(local_result['result'].get('events', []))
    print(f"│ 提取事迹数      │ {api_events:>11} │ {local_events:>11} │")
    
    api_fields = len(api_result['result'].get('emperor_info', {}))
    local_fields = len(local_result['result'].get('emperor_info', {}))
    print(f"│ 皇帝信息字段    │ {api_fields:>11} │ {local_fields:>11} │")
    print("└─────────────────┴─────────────┴─────────────┘")
    
    # 质量对比
    print("\n📈 质量对比:")
    if local_events > api_events:
        print(f"   ✅ 本地方式提取了更多事迹 (+{local_events - api_events} 条)")
    elif api_events > local_events:
        print(f"   ⚠️  API 方式提取了更多事迹 (+{api_events - local_events} 条)")
    else:
        print(f"   ✅ 两种方式提取的事迹数量相同")
    
    # 速度对比
    print("\n⚡ 速度对比:")
    speed_ratio = local_result['elapsed_time'] / api_result['elapsed_time']
    if speed_ratio > 2:
        print(f"   ⚠️  本地方式慢 {speed_ratio:.1f}x，但无字符限制")
    elif speed_ratio > 1.5:
        print(f"   ✅ 本地方式略慢 {speed_ratio:.1f}x，但完整处理HTML")
    else:
        print(f"   ✅ 本地方式速度接近API方式")
    
    # 优势总结
    print("\n💡 建议:")
    print("   - API方式: 速度快，适合小规模数据")
    print("   - 本地方式: 无字符限制，适合大规模/敏感数据")
    print("   - 本项目推荐: 本地方式（避免HTML截断）")


def main():
    """主测试流程"""
    print("\n" + "="*80)
    print("🚀 API vs 本地大模型对比测试")
    print("="*80)
    
    # 检查配置
    api_key = 'sk-c5fffea7ea6b4b4ba3e7abca37a2edc0'  # 从 settings.py 读取
    
    # 加载测试 HTML
    print("\n📂 加载测试数据...")
    html_content = load_test_html()
    
    if not html_content:
        print("❌ 无法加载测试HTML，测试终止")
        return
    
    print(f"✅ 加载成功: {len(html_content)} 字符")
    
    # 测试 API（如果配置了API Key）
    api_result = None
    if api_key and api_key != '':
        api_result = test_api(html_content, api_key)
    else:
        print("\n⚠️  跳过 API 测试（未配置 API Key）")
    
    # 测试本地大模型
    local_result = test_local(html_content)
    
    # 对比结果
    if api_result and local_result:
        compare_results(api_result, local_result)
    
    # 总结
    print("\n" + "="*80)
    print("✅ 对比测试完成")
    print("="*80)


if __name__ == '__main__':
    main()
