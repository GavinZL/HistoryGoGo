"""调试日期解析"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.utils.date_utils import DateParser
import re

parser = DateParser()

# 测试用例
test_cases = [
    "洪武元年",
    "永乐三年正月初一",
    "1368年1月23日",
    "崇祯十七年",
]

for text in test_cases:
    print(f"\n{'='*60}")
    print(f"测试: {text}")
    print('='*60)
    
    # 检查年号匹配
    reign_pattern = r'([洪建永宣正景天成弘德嘉隆万泰启崇][武文乐熙德统泰顺化治靖庆历昌祯]+)(\d+|元|[一二三四五六七八九十]+)年'
    match = re.search(reign_pattern, text)
    
    if match:
        reign_title = match.group(1)
        year_num = match.group(2)
        print(f"年号匹配成功: {reign_title}, 年数: {year_num}")
        
        if reign_title in DateParser.REIGN_YEAR_MAP:
            start_year, end_year = DateParser.REIGN_YEAR_MAP[reign_title]
            print(f"找到年号映射: {start_year}-{end_year}")
            
            if year_num == "元":
                year = start_year
            else:
                year_offset = parser._chinese_year_to_int(year_num)
                year = start_year + year_offset - 1
            print(f"计算出年份: {year}")
        else:
            print(f"未找到年号: {reign_title}")
    else:
        print("年号匹配失败")
    
    # 检查月份匹配
    month_pattern = r'年.*?(\d+|正|二|三|四|五|六|七|八|九|十|十一|十二)月'
    month_match = re.search(month_pattern, text)
    if month_match:
        print(f"月份匹配成功: {month_match.group(1)}")
    else:
        print("月份匹配失败")
    
    # 检查日期匹配
    day_pattern = r'月.*?(初\d+|初一|初二|初三|初四|初五|初六|初七|初八|初九|廿\d+|二十\d+|三十\d*|\d+)日?'
    day_match = re.search(day_pattern, text)
    if day_match:
        print(f"日期匹配成功: {day_match.group(1)}")
    else:
        print("日期匹配失败")
    
    # 最终解析结果
    result = parser.parse_chinese_date(text)
    print(f"最终结果: {result}")
