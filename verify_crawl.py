#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬取数据验证脚本
用于验证爬取是否成功，检查数据完整性
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import json


class CrawlVerifier:
    """爬取验证器"""
    
    def __init__(self, db_path='server/database/historygogo.db'):
        self.db_path = Path(db_path)
        self.conn = None
        self.report = {
            'verification_time': datetime.now().isoformat(),
            'database_exists': False,
            'database_size': 0,
            'data_counts': {},
            'data_quality': {},
            'issues': [],
            'overall_status': 'UNKNOWN'
        }
    
    def verify(self):
        """执行验证"""
        print("=" * 80)
        print("🔍 开始验证爬取数据".center(80))
        print("=" * 80)
        print()
        
        # 1. 检查数据库文件
        if not self._check_database_exists():
            return False
        
        # 2. 连接数据库
        if not self._connect_database():
            return False
        
        # 3. 检查数据数量
        self._check_data_counts()
        
        # 4. 检查数据质量
        self._check_data_quality()
        
        # 5. 检查数据完整性
        self._check_data_integrity()
        
        # 6. 生成验证报告
        self._generate_report()
        
        # 7. 关闭数据库
        if self.conn:
            self.conn.close()
        
        return self.report['overall_status'] == 'SUCCESS'
    
    def _check_database_exists(self):
        """检查数据库是否存在"""
        print("📋 步骤1: 检查数据库文件")
        print("-" * 80)
        
        if self.db_path.exists():
            self.report['database_exists'] = True
            size = self.db_path.stat().st_size
            self.report['database_size'] = size
            size_mb = size / (1024 * 1024)
            print(f"✅ 数据库文件存在: {self.db_path}")
            print(f"   文件大小: {size_mb:.2f} MB")
            print()
            return True
        else:
            self.report['database_exists'] = False
            self.report['issues'].append({
                'level': 'ERROR',
                'message': f'数据库文件不存在: {self.db_path}'
            })
            print(f"❌ 数据库文件不存在: {self.db_path}")
            print(f"   请先运行爬虫: python run_crawler.py")
            print()
            return False
    
    def _connect_database(self):
        """连接数据库"""
        print("📋 步骤2: 连接数据库")
        print("-" * 80)
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print("✅ 数据库连接成功")
            print()
            return True
        except Exception as e:
            self.report['issues'].append({
                'level': 'ERROR',
                'message': f'数据库连接失败: {str(e)}'
            })
            print(f"❌ 数据库连接失败: {str(e)}")
            print()
            return False
    
    def _check_data_counts(self):
        """检查数据数量"""
        print("📋 步骤3: 检查数据数量")
        print("-" * 80)
        
        tables = {
            'dynasties': '朝代',
            'emperors': '皇帝',
            'events': '事件',
            'persons': '人物',
            'works': '作品'
        }
        
        total_count = 0
        for table, name in tables.items():
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                self.report['data_counts'][table] = count
                total_count += count
                
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {name}: {count} 条")
            except Exception as e:
                self.report['issues'].append({
                    'level': 'ERROR',
                    'message': f'查询表 {table} 失败: {str(e)}'
                })
                print(f"❌ {name}: 查询失败")
        
        print(f"\n📊 数据总量: {total_count} 条")
        print()
        
        # 判断数据是否足够
        if self.report['data_counts'].get('emperors', 0) == 0:
            self.report['issues'].append({
                'level': 'ERROR',
                'message': '未找到任何皇帝数据'
            })
        elif self.report['data_counts'].get('emperors', 0) < 3:
            self.report['issues'].append({
                'level': 'WARNING',
                'message': f"皇帝数据过少: {self.report['data_counts']['emperors']} 位"
            })
    
    def _check_data_quality(self):
        """检查数据质量"""
        print("📋 步骤4: 检查数据质量")
        print("-" * 80)
        
        # 检查皇帝数据完整性
        cursor = self.conn.cursor()
        
        # 有biography的皇帝数量
        cursor.execute("SELECT COUNT(*) as count FROM emperors WHERE biography IS NOT NULL AND biography != ''")
        emperors_with_bio = cursor.fetchone()['count']
        total_emperors = self.report['data_counts'].get('emperors', 0)
        
        if total_emperors > 0:
            bio_rate = (emperors_with_bio / total_emperors) * 100
            self.report['data_quality']['emperors_with_biography'] = bio_rate
            print(f"✅ 皇帝有简介: {emperors_with_bio}/{total_emperors} ({bio_rate:.1f}%)")
        
        # 有描述的事件数量
        cursor.execute("SELECT COUNT(*) as count FROM events WHERE description IS NOT NULL AND description != ''")
        events_with_desc = cursor.fetchone()['count']
        total_events = self.report['data_counts'].get('events', 0)
        
        if total_events > 0:
            desc_rate = (events_with_desc / total_events) * 100
            self.report['data_quality']['events_with_description'] = desc_rate
            print(f"✅ 事件有描述: {events_with_desc}/{total_events} ({desc_rate:.1f}%)")
        
        # 有简介的人物数量
        cursor.execute("SELECT COUNT(*) as count FROM persons WHERE biography IS NOT NULL AND biography != ''")
        persons_with_bio = cursor.fetchone()['count']
        total_persons = self.report['data_counts'].get('persons', 0)
        
        if total_persons > 0:
            person_bio_rate = (persons_with_bio / total_persons) * 100
            self.report['data_quality']['persons_with_biography'] = person_bio_rate
            print(f"✅ 人物有简介: {persons_with_bio}/{total_persons} ({person_bio_rate:.1f}%)")
        
        print()
    
    def _check_data_integrity(self):
        """检查数据完整性"""
        print("📋 步骤5: 检查数据完整性")
        print("-" * 80)
        
        cursor = self.conn.cursor()
        
        # 检查是否有孤立的事件（没有关联皇帝）
        cursor.execute("""
            SELECT COUNT(*) as count FROM events 
            WHERE emperor_id IS NULL OR emperor_id NOT IN (SELECT emperor_id FROM emperors)
        """)
        orphan_events = cursor.fetchone()['count']
        
        if orphan_events > 0:
            self.report['issues'].append({
                'level': 'WARNING',
                'message': f'发现 {orphan_events} 个孤立事件（无关联皇帝）'
            })
            print(f"⚠️ 孤立事件: {orphan_events} 个")
        else:
            print(f"✅ 所有事件都有关联皇帝")
        
        # 检查日期异常
        cursor.execute("""
            SELECT COUNT(*) as count FROM emperors 
            WHERE birth_date IS NOT NULL AND death_date IS NOT NULL 
            AND birth_date >= death_date
        """)
        invalid_dates = cursor.fetchone()['count']
        
        if invalid_dates > 0:
            self.report['issues'].append({
                'level': 'WARNING',
                'message': f'发现 {invalid_dates} 位皇帝的出生/去世日期异常'
            })
            print(f"⚠️ 日期异常: {invalid_dates} 条")
        else:
            print(f"✅ 日期数据正常")
        
        print()
    
    def _generate_report(self):
        """生成验证报告"""
        print("📋 步骤6: 生成验证报告")
        print("-" * 80)
        
        # 判断总体状态
        error_count = len([i for i in self.report['issues'] if i['level'] == 'ERROR'])
        warning_count = len([i for i in self.report['issues'] if i['level'] == 'WARNING'])
        
        if error_count > 0:
            self.report['overall_status'] = 'FAILED'
            status_emoji = "❌"
            status_text = "失败"
        elif warning_count > 0:
            self.report['overall_status'] = 'WARNING'
            status_emoji = "⚠️"
            status_text = "有警告"
        else:
            self.report['overall_status'] = 'SUCCESS'
            status_emoji = "✅"
            status_text = "成功"
        
        # 输出问题
        if self.report['issues']:
            print(f"\n发现 {len(self.report['issues'])} 个问题：")
            for issue in self.report['issues']:
                emoji = "❌" if issue['level'] == 'ERROR' else "⚠️"
                print(f"  {emoji} [{issue['level']}] {issue['message']}")
        else:
            print("✅ 未发现任何问题")
        
        # 保存报告到文件
        report_path = Path('crawler/data/reports/crawl_verification_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存: {report_path}")
        print()
        
        # 输出最终结果
        print("=" * 80)
        print(f"{status_emoji} 验证结果: {status_text}".center(80))
        print("=" * 80)
        print()
        
        # 输出数据统计摘要
        print("📊 数据统计摘要:")
        print(f"  - 皇帝: {self.report['data_counts'].get('emperors', 0)} 位")
        print(f"  - 事件: {self.report['data_counts'].get('events', 0)} 个")
        print(f"  - 人物: {self.report['data_counts'].get('persons', 0)} 位")
        print(f"  - 作品: {self.report['data_counts'].get('works', 0)} 件")
        
        total = sum(self.report['data_counts'].values())
        print(f"  - 总计: {total} 条")
        print()
        
        if self.report['overall_status'] == 'SUCCESS':
            print("🎉 恭喜！数据爬取成功，质量良好！")
        elif self.report['overall_status'] == 'WARNING':
            print("⚠️ 数据爬取完成，但存在一些警告，建议检查。")
        else:
            print("❌ 数据爬取失败或不完整，请检查错误信息。")
        
        print()


def main():
    """主函数"""
    verifier = CrawlVerifier()
    success = verifier.verify()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
