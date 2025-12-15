"""
测试HTML清理器功能
"""
import os
import sys

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'local_llm'))

from html_cleaner import HTMLCleanerFactory


def test_html_cleaner():
    """测试HTML清理器"""
    
    # 查找一个HTML文件进行测试
    html_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data', 'html'
    )
    
    # 查找朱元璋的HTML文件
    html_file = None
    for root, dirs, files in os.walk(html_dir):
        for file in files:
            if '朱元璋' in file and file.endswith('.html'):
                html_file = os.path.join(root, file)
                break
        if html_file:
            break
    
    if not html_file:
        print("❌ 未找到测试用的HTML文件")
        return
    
    print(f"📄 使用测试文件: {html_file}")
    
    # 读取HTML内容
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"📊 原始HTML大小: {len(html_content)} 字符")
    
    # 创建清理器
    cleaner = HTMLCleanerFactory.create_cleaner('wikipedia')
    
    # 清理HTML
    print("\n🔧 开始清理HTML...")
    cleaned_content = cleaner.clean(html_content)
    
    # 输出结果
    print("\n" + "="*60)
    print("📝 清理后的文本")
    print("="*60)
    print(f"文本大小: {len(cleaned_content.text)} 字符")
    print(f"\n前500字符:\n{cleaned_content.text[:500]}")
    
    print("\n" + "="*60)
    print("📑 目录结构")
    print("="*60)
    print(f"目录条目数: {len(cleaned_content.toc)}")
    for i, item in enumerate(cleaned_content.toc[:10], 1):
        print(f"{i}. [H{item['level']}] {item['title']} (id: {item['id']})")
    if len(cleaned_content.toc) > 10:
        print(f"... 还有 {len(cleaned_content.toc) - 10} 个条目")
    
    print("\n" + "="*60)
    print("🔗 链接数据")
    print("="*60)
    print(f"链接总数: {len(cleaned_content.links)}")
    
    # 统计链接类型
    link_stats = {}
    for link in cleaned_content.links:
        link_type = link['type']
        link_stats[link_type] = link_stats.get(link_type, 0) + 1
    
    print(f"\n链接分类统计:")
    for link_type, count in sorted(link_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {link_type}: {count}")
    
    print(f"\n前10个链接示例:")
    for i, link in enumerate(cleaned_content.links[:10], 1):
        print(f"{i}. [{link['type']}] {link['text']} -> {link['href']}")
    
    print("\n✅ 测试完成！")


if __name__ == '__main__':
    test_html_cleaner()
