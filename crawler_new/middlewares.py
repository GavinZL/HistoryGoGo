"""
Scrapy 中间件
"""

from fake_useragent import UserAgent


class RandomUserAgentMiddleware:
    """随机 User-Agent 中间件"""
    
    def __init__(self):
        self.ua = UserAgent()
    
    def process_request(self, request, spider):
        """处理请求，设置随机 User-Agent"""
        request.headers['User-Agent'] = self.ua.random
