from scrapy_redis.spiders import RedisSpider


class MySpider(RedisSpider):
    """Spider that reads urls from redis queue (myspider:start_urls).

    Based on:
        https://github.com/rmax/scrapy-redis/blob/master/example-project/example/spiders/myspider_redis.py
    """

    name = "myspider_redis"
    redis_key = "myspider:start_urls"

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop("domain", "")
        self.allowed_domains = filter(None, domain.split(","))
        super(MySpider, self).__init__(*args, **kwargs)

    # def parse(self, response):
    #     return {
    #         "name": response.css("title::text").extract_first(),
    #         "url": response.url,
    #     }

    def parse(self, response):
        yield response.follow(response.url, callback=self.book_spider.parse)

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
