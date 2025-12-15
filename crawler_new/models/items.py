"""
Scrapy Item 定义
用于在爬虫流程中传递数据
"""

import scrapy
from typing import Optional, List


class HtmlPageItem(scrapy.Item):
    """HTML页面Item - 用于存储原始HTML内容"""
    
    # 页面类型: emperor, event, person
    page_type = scrapy.Field()
    
    # 页面标识
    page_id = scrapy.Field()
    
    # 页面名称
    page_name = scrapy.Field()
    
    # 来源: wikipedia, baidu
    data_source = scrapy.Field()
    
    # 原始URL
    source_url = scrapy.Field()
    
    # HTML内容
    html_content = scrapy.Field()
    
    # 元数据（如朝代顺序、关联ID等）
    metadata = scrapy.Field()
    
    # 爬取时间
    crawl_time = scrapy.Field()


class ExtractedDataItem(scrapy.Item):
    """千问大模型提取的结构化数据Item"""
    
    # 数据类型: emperor, event, person
    data_type = scrapy.Field()
    
    # 原始HTML Item
    html_item = scrapy.Field()
    
    # 提取的结构化数据（字典格式）
    extracted_data = scrapy.Field()
    
    # 提取的链接列表（用于递归爬取）
    extracted_links = scrapy.Field()
    
    # 提取时间
    extraction_time = scrapy.Field()


class LinkItem(scrapy.Item):
    """链接Item - 用于递归爬取"""
    
    # 链接类型: event, person
    link_type = scrapy.Field()
    
    # 链接名称
    link_name = scrapy.Field()
    
    # 链接URL
    link_url = scrapy.Field()
    
    # 来源页面
    source_page = scrapy.Field()
    
    # 递归深度
    depth = scrapy.Field()
