#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬虫运行脚本
支持测试模式和全量爬取模式
"""
import os
import sys
import argparse
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_crawler(mode='test', spider_name='baidu_baike'):
    """
    运行爬虫
    
    Args:
        mode: 'test' 或 'full'，测试模式只爬取前3位皇帝
        spider_name: 爬虫名称，'baidu_baike' 或 'wikipedia'
    """
    print("=" * 80)
    print(f"🚀 启动爬虫：{spider_name}")
    print(f"   模式：{'测试模式（前3位皇帝）' if mode == 'test' else '全量爬取'}")
    print("=" * 80)
    
    # 获取Scrapy配置
    settings = get_project_settings()
    
    # 覆盖爬取模式配置
    settings.set('CRAWL_MODE', mode)
    
    # 创建日志目录
    log_dir = project_root / 'crawler' / 'data' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建报告目录
    report_dir = project_root / 'crawler' / 'data' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # 设置日志文件
    log_file = log_dir / f'{spider_name}_{mode}.log'
    settings.set('LOG_FILE', str(log_file))
    
    # 创建爬虫进程
    process = CrawlerProcess(settings)
    
    # 添加爬虫
    process.crawl(spider_name)
    
    # 开始爬取
    process.start()
    
    print("\n" + "=" * 80)
    print("✅ 爬虫运行完成")
    print(f"   日志文件：{log_file}")
    print("=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='HistoryGogo 数据爬取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  # 测试模式（只爬取前3位皇帝）
  python run_crawler.py --mode test --spider baidu_baike
  
  # 全量爬取百度百科
  python run_crawler.py --mode full --spider baidu_baike
  
  # 全量爬取维基百科
  python run_crawler.py --mode full --spider wikipedia
  
  # 同时爬取两个源（先百度后维基）
  python run_crawler.py --mode full --spider all
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['test', 'full'],
        default='test',
        help='爬取模式：test=测试模式（前3位皇帝），full=全量爬取'
    )
    
    parser.add_argument(
        '--spider',
        choices=['baidu_baike', 'wikipedia', 'all'],
        default='baidu_baike',
        help='选择爬虫：baidu_baike, wikipedia, 或 all（两个都爬）'
    )
    
    args = parser.parse_args()
    
    print("\n" + "🚀 HistoryGogo 数据爬取工具".center(80, "="))
    print()
    
    # 检查是否已初始化数据库
    db_path = project_root / 'server' / 'database' / 'historygogo.db'
    if not db_path.exists():
        print("⚠ 警告：数据库未初始化")
        print("请先运行：python init_database.py")
        print()
        response = input("是否继续？（y/n）：")
        if response.lower() != 'y':
            return 1
    
    # 运行爬虫
    if args.spider == 'all':
        # 先爬百度百科
        run_crawler(args.mode, 'baidu_baike')
        print("\n⏳ 等待5秒后开始爬取维基百科...\n")
        import time
        time.sleep(5)
        # 再爬维基百科
        run_crawler(args.mode, 'wikipedia')
    else:
        run_crawler(args.mode, args.spider)
    
    print("\n" + "=" * 80)
    print("✅ 所有爬取任务完成！")
    print()
    print("下一步：")
    print("  1. 查看日志文件：crawler/data/logs/")
    print("  2. 查看验证报告：crawler/data/reports/validation_report.json")
    print("  3. 查看数据库：server/database/historygogo.db")
    print("  4. 生成统计报告：python generate_statistics.py")
    print("=" * 80)
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
