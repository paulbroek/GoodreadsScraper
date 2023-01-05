# -*- coding: utf-8 -*-

# Scrapy settings for GoodreadsScraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'GoodreadsScraper'

SPIDER_MODULES = ['GoodreadsScraper.spiders']
# SPIDER_MODULES = ['GoodreadsScraper.spiders.list.list_spider', 'GoodreadsScraper.spiders.redis.redis_spider']
# SPIDER_MODULES = ['GoodreadsScraper.list_spider', 'GoodreadsScraper.redis_spider']
NEWSPIDER_MODULE = 'GoodreadsScraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'GoodreadsScraper (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

POSTGRES_HOST = "127.0.0.1"
# POSTGRES_PORT = 5432

# scrapy-redis settings
USER_AGENT = 'scrapy-redis (+https://github.com/rolando/scrapy-redis)'

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"
REDIS_PARAMS = {
    "REDIS_HOST": "81.169.252.73",
    "REDIS_PORT" : 6382
}

# update postgres when author item is scraped. Caution: very slow if query is
# not optimized
UPDATE_POSTGRES_PER_ITEM = False
# UPDATE_POSTGRES_PER_ITEM = True
# EXIT_ON_ZERO_TODO = True
EXIT_ON_ZERO_TODO = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'GoodreadsScraper.middlewares.GoodreadsscraperSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'GoodreadsScraper.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'GoodreadsScraper.pipelines.JsonLineItemSegregator': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = False

# The initial download delay
# AUTOTHROTTLE_START_DELAY = 0

# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 7

# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
