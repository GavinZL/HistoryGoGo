"""
Scrapy配置文件
"""

BOT_NAME = 'historygogo_crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# 遵守robots.txt规则
ROBOTSTXT_OBEY = False

# 配置并发请求数
CONCURRENT_REQUESTS = 8

# 配置下载延迟（秒）
DOWNLOAD_DELAY = 3
# 下载延迟的随机化
RANDOMIZE_DOWNLOAD_DELAY = True

# 配置User-Agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 启用或禁用cookies
COOKIES_ENABLED = True

# 配置重试次数
RETRY_TIMES = 3

# 配置超时时间（秒）
DOWNLOAD_TIMEOUT = 30

# 配置HTTP缓存
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 1天
HTTPCACHE_DIR = 'crawler/data/httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# 配置Item Pipeline
ITEM_PIPELINES = {
    'crawler.pipelines.data_cleaning.DataCleaningPipeline': 100,
    'crawler.pipelines.data_validation.DataValidationPipeline': 200,
    'crawler.pipelines.sqlite_pipeline.SQLitePipeline': 300,
    'crawler.pipelines.neo4j_pipeline.Neo4jPipeline': 400,
}

# 配置日志
LOG_LEVEL = 'INFO'
LOG_FILE = 'crawler/data/logs/crawler.log'

# 配置下载中间件
DOWNLOADER_MIDDLEWARES = {
    'crawler.middlewares.RandomUserAgentMiddleware': 400,
    'crawler.middlewares.RetryMiddleware': 500,
}

# 请求头配置
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# SQLite数据库配置
SQLITE_DB_PATH = 'server/database/historygogo.db'

# Neo4j数据库配置
NEO4J_URI = 'bolt://localhost:7687'
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'Ls_gavin_08'  # 请修改为实际密码

# 数据爬取配置
CRAWL_MODE = 'full'  # 'test' 或 'full'
TEST_EMPEROR_COUNT = 3  # 测试模式下爬取的皇帝数量

# 数据验证配置
VALIDATION_REPORT_PATH = 'crawler/data/reports/validation_report.json'

# 统计报告配置
STATISTICS_REPORT_PATH = 'crawler/data/reports/statistics_report.json'
