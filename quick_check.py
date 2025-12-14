#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速检查爬取状态
"""

import sqlite3
from pathlib import Path


def quick_check():
    """快速检查爬取状态"""
    db_path = Path('server/database/historygogo.db')
    
    print("\n" + "=" * 60)
    print("⚡ 快速数据检查".center(60))
    print("=" * 60)
    
    if not db_path.exists():
        print("\n❌ 数据库不存在")
        print("   请先运行: python run_crawler.py --mode test")
        print("=" * 60 + "\n")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查各类数据
        cursor.execute("SELECT COUNT(*) FROM emperors")
        emperors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM events")
        events = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM persons")
        persons = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM works")
        works = cursor.fetchone()[0]
        
        total = emperors + events + persons + works
        
        print(f"\n📊 数据统计:")
        print(f"  👑 皇帝: {emperors} 位")
        print(f"  📜 事件: {events} 个")
        print(f"  👤 人物: {persons} 位")
        print(f"  📖 作品: {works} 件")
        print(f"  {'─' * 30}")
        print(f"  ✨ 总计: {total} 条")
        
        # 判断状态
        print(f"\n🎯 爬取状态:")
        if emperors == 0:
            print("  ❌ 失败 - 没有皇帝数据")
        elif emperors < 3:
            print(f"  ⚠️  不完整 - 只有 {emperors} 位皇帝")
        elif emperors >= 16:
            print("  ✅ 完整 - 所有明朝皇帝数据已爬取")
        else:
            print(f"  ⏳ 部分完成 - {emperors} 位皇帝")
        
        # 给出建议
        print(f"\n💡 下一步:")
        if emperors == 0:
            print("  1. 运行: python run_crawler.py --mode test")
            print("  2. 检查日志: crawler/data/logs/")
        elif emperors < 16:
            print("  1. 运行: python run_crawler.py --mode full")
            print("  2. 验证: python verify_crawl.py")
        else:
            print("  1. 验证数据: python verify_crawl.py")
            print("  2. 启动服务器: cd server && uvicorn main:app")
        
        print("=" * 60 + "\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 检查失败: {str(e)}")
        print("=" * 60 + "\n")


if __name__ == '__main__':
    quick_check()
