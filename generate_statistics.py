#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据统计报告生成脚本
分析爬取的数据并生成详细的统计报告
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from server.database.sqlite_manager import SQLiteManager


def generate_statistics_report(db_path):
    """生成统计报告"""
    print("=" * 80)
    print("📊 开始生成数据统计报告...")
    print("=" * 80)
    
    manager = SQLiteManager(str(db_path))
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'database_path': str(db_path),
        'summary': {},
        'dynasties': [],
        'emperors': [],
        'events': {
            'total': 0,
            'by_type': {},
            'by_emperor': []
        },
        'persons': {
            'total': 0,
            'by_type': {},
            'by_emperor': []
        },
        'works': {
            'total': 0,
            'by_category': {}
        },
        'data_quality': {
            'emperors_with_biography': 0,
            'emperors_with_portrait': 0,
            'events_with_description': 0,
            'persons_with_biography': 0,
            'completeness_score': 0.0
        }
    }
    
    # 1. 总体统计
    stats = manager.get_statistics()
    report['summary'] = stats
    
    print(f"\n📈 总体数据统计：")
    print(f"   朝代数量：{stats.get('dynasties', 0)}")
    print(f"   皇帝数量：{stats.get('emperors', 0)}")
    print(f"   事件数量：{stats.get('events', 0)}")
    print(f"   人物数量：{stats.get('persons', 0)}")
    print(f"   作品数量：{stats.get('works', 0)}")
    
    # 2. 朝代详情
    dynasties = manager.execute("SELECT * FROM dynasties")
    for dynasty in dynasties:
        dynasty_info = {
            'id': dynasty[0],
            'name': dynasty[1],
            'start_year': dynasty[2],
            'end_year': dynasty[3],
            'emperor_count': manager.execute(
                "SELECT COUNT(*) FROM emperors WHERE dynasty_id = ?", 
                (dynasty[0],)
            )[0][0]
        }
        report['dynasties'].append(dynasty_info)
    
    # 3. 皇帝详情
    emperors = manager.execute("""
        SELECT emperor_id, name, reign_start, reign_end, reign_duration,
               biography, portrait_url
        FROM emperors
        ORDER BY reign_start
    """)
    
    emperors_with_bio = 0
    emperors_with_portrait = 0
    
    for emperor in emperors:
        emperor_info = {
            'id': emperor[0],
            'name': emperor[1],
            'reign_start': emperor[2],
            'reign_end': emperor[3],
            'reign_duration': emperor[4],
            'has_biography': bool(emperor[5]),
            'has_portrait': bool(emperor[6]),
            'event_count': manager.execute(
                "SELECT COUNT(*) FROM events WHERE emperor_id = ?",
                (emperor[0],)
            )[0][0],
            'person_count': manager.execute(
                "SELECT COUNT(*) FROM persons WHERE emperor_id = ?",
                (emperor[0],)
            )[0][0]
        }
        report['emperors'].append(emperor_info)
        
        if emperor_info['has_biography']:
            emperors_with_bio += 1
        if emperor_info['has_portrait']:
            emperors_with_portrait += 1
    
    # 4. 事件统计
    event_total = manager.execute("SELECT COUNT(*) FROM events")[0][0]
    report['events']['total'] = event_total
    
    # 按类型统计
    event_types = manager.execute("""
        SELECT event_type, COUNT(*) as count
        FROM events
        GROUP BY event_type
        ORDER BY count DESC
    """)
    
    for event_type, count in event_types:
        report['events']['by_type'][event_type] = count
    
    # 按皇帝统计
    event_by_emperor = manager.execute("""
        SELECT e.name, COUNT(ev.event_id) as count
        FROM emperors e
        LEFT JOIN events ev ON e.emperor_id = ev.emperor_id
        GROUP BY e.emperor_id
        ORDER BY e.reign_start
    """)
    
    for emperor_name, count in event_by_emperor:
        report['events']['by_emperor'].append({
            'emperor': emperor_name,
            'count': count
        })
    
    # 5. 人物统计
    person_total = manager.execute("SELECT COUNT(*) FROM persons")[0][0]
    report['persons']['total'] = person_total
    
    # 按类型统计
    person_types = manager.execute("""
        SELECT person_type, COUNT(*) as count
        FROM persons
        GROUP BY person_type
        ORDER BY count DESC
    """)
    
    for person_type, count in person_types:
        report['persons']['by_type'][person_type] = count
    
    # 按皇帝统计
    person_by_emperor = manager.execute("""
        SELECT e.name, COUNT(p.person_id) as count
        FROM emperors e
        LEFT JOIN persons p ON e.emperor_id = p.emperor_id
        GROUP BY e.emperor_id
        ORDER BY e.reign_start
    """)
    
    for emperor_name, count in person_by_emperor:
        report['persons']['by_emperor'].append({
            'emperor': emperor_name,
            'count': count
        })
    
    # 6. 作品统计
    work_total = manager.execute("SELECT COUNT(*) FROM works")[0][0]
    report['works']['total'] = work_total
    
    # 按类别统计
    work_categories = manager.execute("""
        SELECT category, COUNT(*) as count
        FROM works
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
    """)
    
    for category, count in work_categories:
        report['works']['by_category'][category] = count
    
    # 7. 数据质量评估
    events_with_desc = manager.execute(
        "SELECT COUNT(*) FROM events WHERE description IS NOT NULL AND description != ''"
    )[0][0]
    
    persons_with_bio = manager.execute(
        "SELECT COUNT(*) FROM persons WHERE biography IS NOT NULL AND biography != ''"
    )[0][0]
    
    report['data_quality']['emperors_with_biography'] = emperors_with_bio
    report['data_quality']['emperors_with_portrait'] = emperors_with_portrait
    report['data_quality']['events_with_description'] = events_with_desc
    report['data_quality']['persons_with_biography'] = persons_with_bio
    
    # 计算完整度评分 (0-100)
    total_emperors = len(emperors)
    if total_emperors > 0:
        bio_score = (emperors_with_bio / total_emperors) * 30
        portrait_score = (emperors_with_portrait / total_emperors) * 20
        event_score = min((event_total / (total_emperors * 10)) * 25, 25)  # 期望每个皇帝10个事件
        person_score = min((person_total / (total_emperors * 30)) * 25, 25)  # 期望每个皇帝30个人物
        
        completeness = bio_score + portrait_score + event_score + person_score
        report['data_quality']['completeness_score'] = round(completeness, 2)
    
    print(f"\n📊 数据质量评估：")
    print(f"   皇帝传记完整度：{emperors_with_bio}/{total_emperors} ({emperors_with_bio*100//total_emperors if total_emperors>0 else 0}%)")
    print(f"   皇帝画像完整度：{emperors_with_portrait}/{total_emperors} ({emperors_with_portrait*100//total_emperors if total_emperors>0 else 0}%)")
    print(f"   事件描述完整度：{events_with_desc}/{event_total} ({events_with_desc*100//event_total if event_total>0 else 0}%)")
    print(f"   人物传记完整度：{persons_with_bio}/{person_total} ({persons_with_bio*100//person_total if person_total>0 else 0}%)")
    print(f"   总体完整度评分：{report['data_quality']['completeness_score']}/100")
    
    return report


def print_detailed_report(report):
    """打印详细报告"""
    print("\n" + "=" * 80)
    print("📋 详细统计报告".center(80))
    print("=" * 80)
    
    # 事件类型分布
    print("\n📌 事件类型分布：")
    for event_type, count in sorted(report['events']['by_type'].items(), 
                                     key=lambda x: x[1], reverse=True):
        print(f"   {event_type}: {count}")
    
    # 人物类型分布
    print("\n👥 人物类型分布：")
    for person_type, count in sorted(report['persons']['by_type'].items(), 
                                      key=lambda x: x[1], reverse=True):
        print(f"   {person_type}: {count}")
    
    # 作品类别分布
    if report['works']['by_category']:
        print("\n📚 作品类别分布：")
        for category, count in sorted(report['works']['by_category'].items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"   {category}: {count}")
    
    # 各皇帝数据量
    print("\n👑 各皇帝数据统计：")
    for emperor_info in report['emperors']:
        print(f"   {emperor_info['name']}:")
        print(f"      在位时长：{emperor_info['reign_duration']}年")
        print(f"      相关事件：{emperor_info['event_count']}条")
        print(f"      相关人物：{emperor_info['person_count']}人")
        print(f"      传记：{'✓' if emperor_info['has_biography'] else '✗'}")
        print(f"      画像：{'✓' if emperor_info['has_portrait'] else '✗'}")


def main():
    """主函数"""
    print("\n" + "📊 HistoryGogo 数据统计报告生成工具".center(80, "="))
    print()
    
    # 数据库路径
    db_path = project_root / 'server' / 'database' / 'historygogo.db'
    
    if not db_path.exists():
        print("❌ 错误：数据库文件不存在")
        print(f"   路径：{db_path}")
        print("   请先运行：python init_database.py")
        return 1
    
    # 生成报告
    report = generate_statistics_report(db_path)
    
    # 打印详细报告
    print_detailed_report(report)
    
    # 保存报告到文件
    report_dir = project_root / 'crawler' / 'data' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / 'statistics_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ 统计报告生成完成！")
    print(f"   报告文件：{report_file}")
    print("=" * 80)
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
