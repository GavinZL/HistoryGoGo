"""
爬虫测试脚本
用于测试百度百科爬虫的基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.models.entities import Emperor, Event, Person, EventType, PersonType
from crawler.utils.date_utils import DateParser, clean_text, generate_id
from crawler.config.ming_data import MING_EMPERORS, MING_DYNASTY
from datetime import date


def test_date_parser():
    """测试日期解析器"""
    print("=" * 50)
    print("测试日期解析器")
    print("=" * 50)
    
    parser = DateParser()
    
    test_cases = [
        "洪武元年",
        "永乐三年正月初一",
        "1368年1月23日",
        "崇祯十七年",
    ]
    
    for test_case in test_cases:
        result = parser.parse_chinese_date(test_case)
        print(f"输入: {test_case:20s} => 输出: {result}")
    
    print()


def test_clean_text():
    """测试文本清洗"""
    print("=" * 50)
    print("测试文本清洗")
    print("=" * 50)
    
    test_texts = [
        "朱元璋<sup>[1]</sup>，明朝开国皇帝。",
        "永乐大典 [2-3] 是一部重要著作。",
        "   多余的   空白   ",
    ]
    
    for text in test_texts:
        result = clean_text(text)
        print(f"原文: {text}")
        print(f"清洗后: {result}")
        print()


def test_generate_id():
    """测试ID生成"""
    print("=" * 50)
    print("测试ID生成")
    print("=" * 50)
    
    # 测试基于顺序的ID生成
    emperor_id = generate_id("ming_emperor", "朱元璋", 1)
    print(f"皇帝ID (带顺序): {emperor_id}")
    
    # 测试基于名称hash的ID生成
    event_id = generate_id("ming_event", "靖难之役")
    print(f"事件ID (基于名称): {event_id}")
    
    person_id = generate_id("ming_person", "郑和")
    print(f"人物ID (基于名称): {person_id}")
    
    print()


def test_emperor_entity():
    """测试皇帝实体"""
    print("=" * 50)
    print("测试皇帝实体创建")
    print("=" * 50)
    
    emperor = Emperor(
        emperor_id="ming_emperor_001",
        dynasty_id="ming",
        name="朱元璋",
        temple_name="明太祖",
        reign_title="洪武",
        birth_date=date(1328, 10, 21),
        death_date=date(1398, 6, 24),
        reign_start=date(1368, 1, 23),
        reign_end=date(1398, 6, 24),
        dynasty_order=1,
        biography="明朝开国皇帝，杰出的军事家、政治家。",
        achievements="建立明朝，统一中国。",
        data_source="baidu"
    )
    
    print(f"皇帝ID: {emperor.emperor_id}")
    print(f"姓名: {emperor.name}")
    print(f"庙号: {emperor.temple_name}")
    print(f"年号: {emperor.reign_title}")
    print(f"在位时间: {emperor.reign_start} ~ {emperor.reign_end}")
    print(f"在位年数: {emperor.reign_duration}年")
    print(f"生平简介: {emperor.biography}")
    print()


def test_event_entity():
    """测试事件实体"""
    print("=" * 50)
    print("测试事件实体创建")
    print("=" * 50)
    
    event = Event(
        event_id="ming_event_001",
        dynasty_id="ming",
        emperor_id="ming_emperor_003",
        title="靖难之役",
        event_type=EventType.MILITARY,
        start_date=date(1399, 7, 5),
        end_date=date(1402, 7, 13),
        location="北京",
        description="朱棣发动的夺取皇位的战争。",
        significance="朱棣成功夺得皇位，成为明成祖。",
        related_persons=["ming_person_001", "ming_person_002"],
        data_source="baidu"
    )
    
    print(f"事件ID: {event.event_id}")
    print(f"事件名称: {event.title}")
    print(f"事件类型: {event.event_type.value}")
    print(f"发生时间: {event.start_date} ~ {event.end_date}")
    print(f"发生地点: {event.location}")
    print(f"事件描述: {event.description}")
    print(f"历史意义: {event.significance}")
    print(f"相关人物: {len(event.related_persons)}人")
    print()


def test_person_entity():
    """测试人物实体"""
    print("=" * 50)
    print("测试人物实体创建")
    print("=" * 50)
    
    person = Person(
        person_id="ming_person_001",
        dynasty_id="ming",
        name="郑和",
        person_type=PersonType.GENERAL,
        alias=["三宝太监", "马和"],
        birth_date=date(1371, 1, 1),
        death_date=date(1433, 1, 1),
        position="钦差正使",
        biography="明朝航海家、外交家。",
        contributions="七下西洋，加强了明朝与海外各国的联系。",
        works=["航海图"],
        related_emperors=["ming_emperor_003"],
        data_source="baidu"
    )
    
    print(f"人物ID: {person.person_id}")
    print(f"姓名: {person.name}")
    print(f"别名: {', '.join(person.alias)}")
    print(f"人物类型: {person.person_type.value}")
    print(f"生卒年: {person.birth_date} ~ {person.death_date}")
    print(f"主要职位: {person.position}")
    print(f"生平简介: {person.biography}")
    print(f"主要贡献: {person.contributions}")
    print(f"代表作品: {', '.join(person.works)}")
    print()


def test_ming_data():
    """测试明朝基础数据"""
    print("=" * 50)
    print("测试明朝基础数据")
    print("=" * 50)
    
    print(f"朝代: {MING_DYNASTY['name']}")
    print(f"朝代ID: {MING_DYNASTY['dynasty_id']}")
    print(f"时间范围: {MING_DYNASTY['start_year']} - {MING_DYNASTY['end_year']}")
    print(f"国都: {MING_DYNASTY['capital']}")
    print(f"开国皇帝: {MING_DYNASTY['founder']}")
    print()
    
    print(f"明朝皇帝数量: {len(MING_EMPERORS)}")
    print("\n前5位皇帝:")
    for i, emperor in enumerate(MING_EMPERORS[:5], 1):
        print(f"  {i}. {emperor['name']} ({emperor['temple_name']}) - {emperor['reign_title']} - {emperor['reign_years']}")
    print()


def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("历史时间轴爬虫 - 功能测试")
    print("=" * 50 + "\n")
    
    try:
        test_ming_data()
        test_date_parser()
        test_clean_text()
        test_generate_id()
        test_emperor_entity()
        test_event_entity()
        test_person_entity()
        
        print("=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        print("\n提示: 爬虫基础功能已实现，可以开始运行Scrapy爬虫。")
        print("运行命令: scrapy crawl baidu_baike -s JOBDIR=crawler/data/jobs/baidu")
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
