#!/usr/bin/env python3
"""
快速测试维基百科爬虫的完整流程
使用Scrapy的测试工具直接测试爬虫
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from crawler.spiders.wikipedia_spider import WikipediaSpider
from crawler.config.settings import *


def test_emperor_extraction():
    """测试皇帝信息提取完整流程"""
    print("=" * 70)
    print("测试皇帝信息提取完整流程")
    print("=" * 70)
    
    # 读取测试HTML
    html_file = project_root / 'crawler' / 'spiders' / 'wiki' / 'infobox.html'
    
    if not html_file.exists():
        print(f"错误：找不到测试文件 {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 创建scrapy settings
    from scrapy.settings import Settings
    settings = Settings()
    settings.set('CRAWL_MODE', 'test')
    settings.set('TEST_EMPEROR_COUNT', 1)
    
    # 创建爬虫实例
    spider = WikipediaSpider()
    spider.settings = settings
    spider.crawl_mode = 'test'
    spider.test_emperor_count = 1
    
    # 模拟response
    url = "https://zh.wikipedia.org/wiki/明太祖"
    
    # 准备emperor_info
    emperor_info = {
        'name': '明太祖',
        'temple_name': '太祖',
        'reign_title': '洪武',
        'dynasty_order': 1,
        'reign_years': '1368-1398'
    }
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 测试提取
    emperor_data = spider._extract_emperor_data(soup, emperor_info)
    
    if emperor_data:
        print("\n✓ 成功提取皇帝数据")
        print(f"\n皇帝名称: {emperor_data.get('name')}")
        print(f"庙号: {emperor_data.get('temple_name')}")
        print(f"年号: {emperor_data.get('reign_title')}")
        
        # 显示infobox数据
        infobox_data = emperor_data.get('infobox_data', {})
        print(f"\n提取的Infobox字段数: {len(infobox_data)}")
        for key, value in infobox_data.items():
            if key == 'paragraphs':
                print(f"  {key}: {len(value)} 个段落")
            else:
                value_preview = str(value)[:80]
                print(f"  {key}: {value_preview}...")
        
        # 显示生平HTML
        biography_html = emperor_data.get('biography_html', '')
        if biography_html:
            print(f"\n✓ 提取了生平HTML内容（长度: {len(biography_html)} 字符）")
            print(f"  预览（前200字符）:\n  {biography_html[:200]}...")
        else:
            print("\n⚠ 未找到生平HTML内容（可能HTML文件中没有mw-heading2标签）")
        
        # 测试创建Emperor实体
        print("\n测试创建Emperor实体...")
        emperor = spider._create_emperor_entity(emperor_data, emperor_info)
        print(f"✓ Emperor实体创建成功")
        print(f"  emperor_id: {emperor.emperor_id}")
        print(f"  name: {emperor.name}")
        print(f"  source_url: {emperor.source_url}")
        print(f"  html_content长度: {len(emperor.html_content or '')} 字符")
        
    else:
        print("✗ 提取皇帝数据失败")


def test_infobox_detailed():
    """详细测试Infobox各个字段的提取"""
    print("\n" + "=" * 70)
    print("详细测试Infobox字段提取")
    print("=" * 70)
    
    # 读取测试HTML
    html_file = project_root / 'crawler' / 'spiders' / 'wiki' / 'infobox.html'
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'lxml')
    infobox = soup.find('table', class_='infobox')
    
    if not infobox:
        print("✗ 未找到infobox")
        return
    
    print("\n✓ 找到infobox表格")
    
    # 测试各个字段的提取
    fields_to_test = [
        ('出生', '出生'),
        ('逝世', '逝世'),
        ('统治', '统治'),
        ('庙号', '庙号'),
        ('谥号', '谥号'),
        ('年号', '年号'),
    ]
    
    print("\n字段提取测试结果:")
    for field_name, pattern in fields_to_test:
        import re
        row = infobox.find('th', string=re.compile(pattern))
        if row and row.find_next_sibling('td'):
            value = row.find_next_sibling('td').get_text(strip=True)[:80]
            print(f"  ✓ {field_name:6s}: {value}...")
        else:
            print(f"  ✗ {field_name:6s}: 未找到")
    
    # 测试图片提取
    portrait = infobox.find('img')
    if portrait and portrait.get('src'):
        img_url = portrait['src']
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        print(f"\n  ✓ 画像URL: {img_url[:80]}...")
    else:
        print("\n  ✗ 画像: 未找到")


if __name__ == '__main__':
    print("\n维基百科爬虫完整流程测试\n")
    
    try:
        test_emperor_extraction()
        test_infobox_detailed()
        
        print("\n" + "=" * 70)
        print("✓ 所有测试完成")
        print("=" * 70)
        print("\n提示：如需测试实际爬取，请运行:")
        print("  scrapy crawl wikipedia -s CRAWL_MODE=test -s TEST_EMPEROR_COUNT=1")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
