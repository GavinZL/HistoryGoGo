#!/usr/bin/env python
"""
运行爬虫的便捷脚本
"""

import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_crawler(spider_name='ming_emperor', source='wikipedia', mode='test'):
    """
    运行爬虫
    
    Args:
        spider_name: 爬虫名称，默认 'ming_emperor'
        source: 数据源，可选 'wikipedia', 'baidu', 'both'
        mode: 爬取模式，可选 'test', 'full'
    """
    # 设置工作目录
    os.chdir(project_root)
    
    # 加载配置
    settings = get_project_settings()
    settings.setmodule('crawler_new.config.settings')
    
    # 覆盖部分配置
    settings.set('CRAWL_MODE', mode)
    
    # 创建爬虫进程
    process = CrawlerProcess(settings)
    
    # 启动爬虫
    print(f"🚀 启动爬虫: {spider_name}")
    print(f"   数据源: {source}")
    print(f"   模式: {mode}")
    print(f"{'='*80}\n")
    
    process.crawl(spider_name, source=source)
    process.start()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='运行 crawler_new 爬虫')
    parser.add_argument('--spider', default='ming_emperor', help='爬虫名称')
    parser.add_argument('--source', default='wikipedia', choices=['wikipedia', 'baidu', 'both'], help='数据源')
    parser.add_argument('--mode', default='test', choices=['test', 'full'], help='爬取模式')
    
    args = parser.parse_args()
    
    run_crawler(
        spider_name=args.spider,
        source=args.source,
        mode=args.mode
    )
