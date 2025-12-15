"""
Scrapy配置文件 - crawler_new
"""

BOT_NAME = 'historygogo_crawler_new'

SPIDER_MODULES = ['crawler_new.spiders']
NEWSPIDER_MODULE = 'crawler_new.spiders'

# 遵守robots.txt规则
ROBOTSTXT_OBEY = False

# 配置并发请求数
CONCURRENT_REQUESTS = 8

# 配置下载延迟（秒）
DOWNLOAD_DELAY = 5
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
HTTPCACHE_DIR = 'crawler_new/data/httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# 配置Item Pipeline
ITEM_PIPELINES = {
    'crawler_new.pipelines.html_storage_pipeline.HtmlStoragePipeline': 100,  # HTML存储
    'crawler_new.pipelines.qwen_extraction_pipeline.QwenExtractionPipeline': 200,  # 千问大模型提取
    'crawler_new.pipelines.data_validation_pipeline.DataValidationPipeline': 300,  # 数据验证
    'crawler_new.pipelines.sqlite_pipeline.SQLitePipeline': 400,  # SQLite存储
    'crawler_new.pipelines.neo4j_pipeline.Neo4jPipeline': 500,  # Neo4j存储
    'crawler_new.pipelines.recursive_crawl_pipeline.RecursiveCrawlPipeline': 600,  # 递归爬取
}

# 配置日志
LOG_LEVEL = 'INFO'
LOG_FILE = 'crawler_new/data/logs/crawler.log'

# 配置下载中间件
DOWNLOADER_MIDDLEWARES = {
    'crawler_new.middlewares.RandomUserAgentMiddleware': 400,
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
NEO4J_PASSWORD = 'Ls_gavin_08'

# HTML存储路径
HTML_STORAGE_PATH = 'crawler_new/data/html'

# 大模型配置（API 或 本地）
USE_LOCAL_LLM = False  # True: 使用本地大模型, False: 使用API

# 千问大模型 API 配置（当 USE_LOCAL_LLM = False 时使用）
QWEN_API_KEY = 'sk-c5fffea7ea6b4b4ba3e7abca37a2edc0'  # 需要用户配置
QWEN_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
QWEN_MODEL = 'qwen-max'  # 或 qwen-turbo

# 本地大模型配置（当 USE_LOCAL_LLM = True 时使用）
LOCAL_LLM_MODEL = 'qwen2.5:7b'  # Ollama 模型名称
LOCAL_LLM_BASE_URL = 'http://localhost:11434'  # Ollama API 地址

# 爬取模式配置
CRAWL_MODE = 'test'  # 'test' 或 'full'
TEST_EMPEROR_COUNT = 3  # 测试模式下爬取的皇帝数量

# 递归爬取配置
ENABLE_RECURSIVE_CRAWL = False  # 是否启用递归爬取人物、事件链接
MAX_RECURSIVE_DEPTH = 2  # 最大递归深度
