import logging

from scrapy_redis.spiders import RedisSpider

from .book_spider import BookSpider

GOODREADS_URL_PREFIX = "https://www.goodreads.com"

logger = logging.getLogger(__name__)


class MySpider(RedisSpider, BookSpider):
    """Spider that reads urls from redis queue (myspider:start_urls).

    Based on:
        https://github.com/rmax/scrapy-redis/blob/master/example-project/example/spiders/myspider_redis.py
    """

    name = "myspider_redis"
    redis_key = "myspider:start_urls"

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        # TODO: use dynamically domains list, see scrapy-redis docs / source code?
        # domain = kwargs.pop("domain", "")
        domain = "www.goodreads.com"
        self.allowed_domains = filter(None, domain.split(","))
        super(MySpider, self).__init__(*args, **kwargs)

        self.book_spider = BookSpider()
        self.book_parser = self.book_spider.parse
        self.author_parser = self.book_spider.author_spider.parse

        self.start_urls = [GOODREADS_URL_PREFIX]

    # def parse(self, response):
    #     return {
    #         "name": response.css("title::text").extract_first(),
    #         "url": response.url,
    #     }

    def parse(self, response):
        # yield response.follow(response.url, callback=self.book_spider.parse)
        yield response.follow(response.url, callback=self.book_parser)
