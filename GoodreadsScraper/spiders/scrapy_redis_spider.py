import logging

from scrapy_redis.spiders import RedisSpider

from .book_spider import BookSpider

GOODREADS_URL_PREFIX = "https://www.goodreads.com"

logger = logging.getLogger(__name__)


# class MySpider(RedisSpider, BookSpider):
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
        # yield response.follow(book, callback=self.book_spider.parse)
        # logger.info(f"self.parse: {self.parse}")

        # return {"url": response.url}
        # return self.book_spider.parse(response.url)
        # logger.info(f"{type(response)=}")
        # yield response.follow(response.url, callback=self.book_spider.parse)
        yield response.follow(response.url, callback=self.book_parser)
        # yield response.follow(response.url, callback=self.parse)

    # def parse(self, response):
    #     # list_of_books = response.css("a.bookTitle::attr(href)").extract()

    #     # manual input override. don't know other way for now
    #     # list_of_books = ["/book/show/16085481-crazy-rich-asians", "/book/show/199519.The_Tibetan_Yogas_Of_Dream_And_Sleep", "/book/show/50512348-the-message-game"]
    #     # or listen for books through redis
    #     list_of_books = self.redis_generator()
    #     # logger.info(f"{len(list_of_books)=}")

    #     while True:

    #         for book in list_of_books:
    #             logger.info(f"yielding {book=}")

    #         logging.info(f"sleeping {REDIS_FETCH_INTERVAL} seconds")
    #         sleep(REDIS_FETCH_INTERVAL)
