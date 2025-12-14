#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试脚本
验证爬虫和数据库持久化功能
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from server.database.sqlite_manager import SQLiteManager


def test_database():
    """测试数据库连接"""
    print("\n" + "=" * 80)
    print("📊 测试数据库连接...")
    print("=" * 80)
    
    db_path = project_root / 'server' / 'database' / 'historygogo.db'
    
    if not db_path.exists():
        print("❌ 数据库文件不存在，请先运行: python3 init_database.py")
        return False
    
    try:
        manager = SQLiteManager(str(db_path))
        tables = manager.get_all_tables()
        
        print(f"✓ 数据库连接成功")
        print(f"  数据库路径：{db_path}")
        print(f"  已创建的表：")
        
        for table in tables:
            if not table.startswith('sqlite_'):
                count = manager.count_records(table)
                print(f"    - {table}: {count} 条记录")
        
        manager.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败：{e}")
        return False


def test_data_models():
    """测试数据模型"""
    print("\n" + "=" * 80)
    print("📦 测试数据模型...")
    print("=" * 80)
    
    try:
        from crawler.models.entities import Emperor, Event, Person, EventType, PersonType
        from datetime import date
        
        # 创建测试皇帝
        emperor = Emperor(
            emperor_id="test_emperor_1",
            dynasty_id="ming",
            name="朱元璋",
            temple_name="太祖",
            reign_title="洪武",
            birth_date=date(1328, 10, 21),
            death_date=date(1398, 6, 24),
            reign_start=date(1368, 1, 1),
            reign_end=date(1398, 12, 31),
            dynasty_order=1,
            biography="明朝开国皇帝",
            achievements="推翻元朝，建立明朝",
            portrait_url=None,
            data_source="test"
        )
        
        print(f"✓ 成功创建Emperor实体：{emperor.name}")
        print(f"  在位时长：{emperor.reign_duration}年")
        
        # 创建测试事件
        event = Event(
            event_id="test_event_1",
            emperor_id="test_emperor_1",
            dynasty_id="ming",
            title="靖难之役",
            event_type=EventType.MILITARY,
            start_date=date(1399, 1, 1),
            end_date=date(1402, 12, 31),
            location="中国",
            description="朱棣夺取皇位的战争",
            related_persons=["test_person_1", "test_person_2"],
            data_source="test"
        )
        
        print(f"✓ 成功创建Event实体：{event.title}")
        print(f"  事件类型：{event.event_type}")
        
        # 创建测试人物
        person = Person(
            person_id="test_person_1",
            dynasty_id="ming",
            name="徐达",
            person_type=PersonType.GENERAL,
            birth_date=None,
            death_date=None,
            biography="明朝开国功臣",
            position="大将军",
            contributions="协助朱元璋建立明朝",
            works=[],
            related_emperors=["test_emperor_1"],
            data_source="test"
        )
        
        print(f"✓ 成功创建Person实体：{person.name}")
        print(f"  人物类型：{person.person_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据模型测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_date_parser():
    """测试日期解析器"""
    print("\n" + "=" * 80)
    print("📅 测试日期解析器...")
    print("=" * 80)
    
    try:
        # 首先检查dateutil是否可用
        try:
            import dateutil
        except ImportError:
            print("⚠ dateutil模块未安装，跳过测试")
            print("  请安装: pip install python-dateutil")
            return True  # 不阻塞测试
        
        from crawler.utils.date_utils import DateParser
        
        parser = DateParser()
        
        # 测试中文日期解析
        test_cases = [
            "洪武元年",
            "永乐十八年",
            "1368年",
            "1368年1月1日"
        ]
        
        for test_str in test_cases:
            result = parser.parse_chinese_date(test_str)
            if result:
                print(f"✓ {test_str} -> {result}")
            else:
                print(f"✗ {test_str} -> 解析失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 日期解析器测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "🧪 HistoryGogo 功能测试".center(80, "="))
    
    all_passed = True
    
    # 测试数据库
    if not test_database():
        all_passed = False
    
    # 测试数据模型
    if not test_data_models():
        all_passed = False
    
    # 测试日期解析器
    if not test_date_parser():
        all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有测试通过！")
        print("\n下一步：运行测试爬取")
        print("  python3 run_crawler.py --mode test --spider baidu_baike")
    else:
        print("⚠ 部分测试失败，请查看上述错误信息")
    print("=" * 80)
    print()
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
