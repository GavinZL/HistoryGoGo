"""
日期处理工具函数
用于解析和转换各种日期格式
"""

import re
from datetime import date, datetime
from typing import Optional
from dateutil import parser


class DateParser:
    """日期解析器"""
    
    # 年号到年份的映射（明朝）
    REIGN_YEAR_MAP = {
        "洪武": (1368, 1398),
        "建文": (1398, 1402),
        "永乐": (1402, 1424),
        "洪熙": (1424, 1425),
        "宣德": (1425, 1435),
        "正统": (1435, 1449),
        "景泰": (1449, 1457),
        "天顺": (1457, 1464),
        "成化": (1464, 1487),
        "弘治": (1487, 1505),
        "正德": (1505, 1521),
        "嘉靖": (1521, 1567),
        "隆庆": (1567, 1572),
        "万历": (1572, 1620),
        "泰昌": (1620, 1621),
        "天启": (1621, 1627),
        "崇祯": (1627, 1644)
    }
    
    @staticmethod
    def parse_chinese_date(text: str) -> Optional[date]:
        """
        解析中文日期格式
        例如：洪武元年、永乐三年正月初一
        """
        if not text:
            return None
        
        try:
            # 提取年号和年份（支持数字和中文数字）
            reign_pattern = r'([洪建永宣正景天成弘德嘉隆万泰启崇][武文乐熙德统泰顺化治靖庆历昌祯]+)(\d+|元|[一二三四五六七八九十]+)年'
            match = re.search(reign_pattern, text)
            
            if match:
                reign_title = match.group(1)
                year_num = match.group(2)
                
                if reign_title in DateParser.REIGN_YEAR_MAP:
                    start_year, _ = DateParser.REIGN_YEAR_MAP[reign_title]
                    if year_num == "元":
                        year = start_year
                    else:
                        # 转换中文数字或阿拉伯数字
                        year_offset = DateParser._chinese_year_to_int(year_num)
                        year = start_year + year_offset - 1
                    
                    # 尝试提取月日
                    month = 1
                    day = 1
                    
                    # 提取月份（在年号之后）
                    month_pattern = r'年.*?(\d+|正|二|三|四|五|六|七|八|九|十|十一|十二)月'
                    month_match = re.search(month_pattern, text)
                    if month_match:
                        month_str = month_match.group(1)
                        month = DateParser._chinese_num_to_int(month_str)
                    
                    # 提取日期（在月份之后）
                    day_pattern = r'月.*?(初\d+|初一|初二|初三|初四|初五|初六|初七|初八|初九|廿\d+|二十\d+|三十\d*|\d+)日?'
                    day_match = re.search(day_pattern, text)
                    if day_match:
                        day_str = day_match.group(1)
                        day = DateParser._parse_chinese_day(day_str)
                    
                    try:
                        return date(year, month, day)
                    except ValueError:
                        return date(year, 1, 1)
            
            # 尝试解析公历日期
            return DateParser.parse_gregorian_date(text)
            
        except Exception:
            return None
    
    @staticmethod
    def parse_gregorian_date(text: str) -> Optional[date]:
        """解析公历日期"""
        if not text:
            return None
        
        try:
            # 先尝试匹配完整的年月日格式
            full_date_pattern = r'(\d{3,4})年(\d{1,2})月(\d{1,2})日?'
            match = re.search(full_date_pattern, text)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                try:
                    return date(year, month, day)
                except ValueError:
                    return date(year, 1, 1)
            
            # 匹配年月格式
            year_month_pattern = r'(\d{3,4})年(\d{1,2})月'
            match = re.search(year_month_pattern, text)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                try:
                    return date(year, month, 1)
                except ValueError:
                    return date(year, 1, 1)
            
            # 只有年份
            year_pattern = r'(\d{3,4})年'
            match = re.search(year_pattern, text)
            if match:
                year = int(match.group(1))
                return date(year, 1, 1)
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def _chinese_year_to_int(year_str: str) -> int:
        """将中文年数转换为阿拉伯数字（如：三→3, 十七→17）"""
        if year_str.isdigit():
            return int(year_str)
        
        # 特殊处理：元年
        if year_str == "元":
            return 1
        
        num_map = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
        }
        
        # 处理十几、几十等
        if '十' in year_str:
            if year_str == '十':
                return 10
            elif year_str.startswith('十'):  # 十一、十二等
                return 10 + num_map.get(year_str[1], 0)
            elif year_str.endswith('十'):  # 二十、三十等
                return num_map.get(year_str[0], 0) * 10
            else:  # 二十三、三十五等
                tens = num_map.get(year_str[0], 0) * 10
                ones = num_map.get(year_str[2], 0) if len(year_str) > 2 else 0
                return tens + ones
        
        return num_map.get(year_str, 1)
    
    @staticmethod
    def _chinese_num_to_int(chinese_num: str) -> int:
        """将中文数字转换为阿拉伯数字（用于月份）"""
        chinese_map = {
            '正': 1, '一': 1, '二': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
            '十': 10, '十一': 11, '十二': 12
        }
        
        if chinese_num.isdigit():
            return int(chinese_num)
        
        return chinese_map.get(chinese_num, 1)
    
    @staticmethod
    def _parse_chinese_day(day_str: str) -> int:
        """解析中文日期（初一、初十、十五等）"""
        if not day_str:
            return 1
            
        if day_str.isdigit():
            return int(day_str)
        
        # 初一到初九、初十
        if day_str.startswith('初'):
            if len(day_str) == 2:
                if day_str[1] == '一':
                    return 1
                elif day_str[1] == '二':
                    return 2
                elif day_str[1] == '三':
                    return 3
                elif day_str[1] == '四':
                    return 4
                elif day_str[1] == '五':
                    return 5
                elif day_str[1] == '六':
                    return 6
                elif day_str[1] == '七':
                    return 7
                elif day_str[1] == '八':
                    return 8
                elif day_str[1] == '九':
                    return 9
            return int(day_str[1:]) if day_str[1:].isdigit() else 1
        
        # 廿一到廿九（20-29日）
        if day_str.startswith('廿'):
            if len(day_str) == 2 and day_str[1].isdigit():
                return 20 + int(day_str[1])
            return 20
        
        # 二十X
        if day_str.startswith('二十'):
            if len(day_str) > 2:
                return 20 + int(day_str[2:]) if day_str[2:].isdigit() else 20
            return 20
        
        # 三十、三十一
        if day_str.startswith('三十'):
            if len(day_str) > 2:
                return 30 + int(day_str[2:]) if day_str[2:].isdigit() else 30
            return 30
        
        # 十X（10-19日）
        if day_str.startswith('十'):
            if len(day_str) == 1:
                return 10
            return 10 + int(day_str[1:]) if day_str[1:].isdigit() else 10
        
        return 1


def clean_text(text: str) -> str:
    """
    清洗文本
    移除HTML标签、特殊字符、引用标记
    """
    if not text:
        return ""
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 移除引用标记
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[\d+-\d+\]', '', text)
    
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def generate_id(prefix: str, name: str, order: int = None) -> str:
    """
    生成唯一ID
    """
    import hashlib
    
    if order is not None:
        return f"{prefix}_{order:03d}"
    
    # 使用name的hash生成ID
    hash_obj = hashlib.md5(name.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()[:8]
    
    return f"{prefix}_{hash_hex}"
