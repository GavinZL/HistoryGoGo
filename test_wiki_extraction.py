#!/usr/bin/env python3
"""
测试维基百科爬虫的信息提取功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bs4 import BeautifulSoup
from crawler.spiders.wikipedia_spider import WikipediaSpider
from crawler.utils.date_utils import DateParser, clean_text


def test_infobox_extraction():
    """测试infobox信息提取"""
    print("=" * 60)
    print("测试 Infobox 信息提取")
    print("=" * 60)
    
    # 读取测试HTML文件
    html_file = project_root / 'crawler' / 'spiders' / 'wiki' / 'infobox.html'
    
    if not html_file.exists():
        print(f"错误：找不到测试文件 {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 查找infobox
    infobox = soup.find('table', class_='infobox')
    
    if not infobox:
        print("未找到 infobox")
        return
    
    print("\n✓ 找到 infobox 表格")
    
    # 提取所有段落
    paragraphs = infobox.find_all('p')
    print(f"\n在 infobox 中找到 {len(paragraphs)} 个段落:")
    for i, p in enumerate(paragraphs, 1):
        p_text = clean_text(p.get_text())
        if p_text:
            print(f"  段落 {i}: {p_text[:100]}...")
    
    # 提取关键字段
    print("\n提取的关键信息:")
    
    # 出生
    birth_row = infobox.find('th', text=lambda t: t and '出生' in t)
    if birth_row and birth_row.find_next_sibling('td'):
        print(f"  出生: {birth_row.find_next_sibling('td').get_text(strip=True)[:100]}")
    
    # 逝世
    death_row = infobox.find('th', text=lambda t: t and '逝世' in t)
    if death_row and death_row.find_next_sibling('td'):
        print(f"  逝世: {death_row.find_next_sibling('td').get_text(strip=True)[:100]}")
    
    # 统治
    reign_row = infobox.find('th', text=lambda t: t and '统治' in t)
    if reign_row and reign_row.find_next_sibling('td'):
        print(f"  统治: {reign_row.find_next_sibling('td').get_text(strip=True)[:100]}")
    
    # 庙号
    temple_row = infobox.find('th', text=lambda t: t and '庙号' in t)
    if temple_row and temple_row.find_next_sibling('td'):
        print(f"  庙号: {temple_row.find_next_sibling('td').get_text(strip=True)[:100]}")
    
    # 谥号
    posthumous_row = infobox.find('th', text=lambda t: t and '谥号' in t)
    if posthumous_row and posthumous_row.find_next_sibling('td'):
        print(f"  谥号: {posthumous_row.find_next_sibling('td').get_text(strip=True)[:100]}")


def test_heading_extraction():
    """测试mw-heading提取"""
    print("\n" + "=" * 60)
    print("测试 mw-heading 章节提取")
    print("=" * 60)
    
    # 读取测试HTML文件
    html_file = project_root / 'crawler' / 'spiders' / 'wiki' / 'infobox.html'
    
    if not html_file.exists():
        print(f"错误：找不到测试文件 {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 查找所有mw-heading
    all_headings = soup.find_all('div', class_=lambda c: c and 'mw-heading' in c)
    print(f"\n找到 {len(all_headings)} 个 mw-heading 元素")
    
    # 查找mw-heading2
    heading2_list = soup.find_all('div', class_='mw-heading mw-heading2')
    print(f"找到 {len(heading2_list)} 个 mw-heading2 元素:")
    
    for i, heading in enumerate(heading2_list, 1):
        heading_text = heading.get_text(strip=True)
        print(f"  {i}. {heading_text}")
    
    # 测试提取第一个heading2到下一个heading2之间的内容
    if heading2_list:
        print("\n提取第一个 mw-heading2 章节的内容...")
        first_heading = heading2_list[0]
        
        html_parts = []
        html_parts.append(str(first_heading))
        
        current_elem = first_heading.find_next_sibling()
        element_count = 0
        
        while current_elem and element_count < 20:  # 限制数量避免过多输出
            # 如果遇到下一个heading2，停止
            if current_elem.name == 'div' and 'mw-heading' in current_elem.get('class', []) and 'mw-heading2' in current_elem.get('class', []):
                break
            
            html_parts.append(str(current_elem)[:200])  # 限制长度
            element_count += 1
            current_elem = current_elem.find_next_sibling()
        
        print(f"  提取了 {element_count} 个元素")
        print(f"  HTML内容预览（前500字符）:")
        content_preview = '\n'.join(html_parts)[:500]
        print(f"  {content_preview}...")


def test_link_preservation():
    """测试链接保留"""
    print("\n" + "=" * 60)
    print("测试 href 链接保留")
    print("=" * 60)
    
    # 读取测试HTML文件
    html_file = project_root / 'crawler' / 'spiders' / 'wiki' / 'infobox.html'
    
    if not html_file.exists():
        print(f"错误：找不到测试文件 {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 查找所有链接
    all_links = soup.find_all('a', href=True)
    print(f"\n在HTML中找到 {len(all_links)} 个链接")
    
    # 显示前10个链接
    print("\n前10个链接示例:")
    for i, link in enumerate(all_links[:10], 1):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        print(f"  {i}. {text[:30]:30s} -> {href}")


if __name__ == '__main__':
    print("\n维基百科爬虫信息提取测试\n")
    
    try:
        test_infobox_extraction()
        test_heading_extraction()
        test_link_preservation()
        
        print("\n" + "=" * 60)
        print("✓ 测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
