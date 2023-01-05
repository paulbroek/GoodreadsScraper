"""Spider to extract URL's of books from a Listopia list on Goodreads."""

import logging
import os
from os.path import dirname, join
from time import sleep

import redis
import scrapy
from dotenv import load_dotenv

from .book_spider import BookSpider

GOODREADS_URL_PREFIX = "https://www.goodreads.com"
REDIS_TO_SCRAPE_KEY = "goodreads_to_scrape"
REDIS_TO_POSTGRES_KEY = "goodreads_to_postgres"

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

REDIS_FETCH_INTERVAL = 3


class RedisSpider(scrapy.Spider):
    """Extract URLs of books from a Listopia list on Goodreads.

    This subsequently passes on the URLs to BookSpider
    """

    name = "redis"

    goodreads_list_url = "https://www.goodreads.com/list/show/{}?page={}"

    def __init__(self):
        super().__init__()
        self.book_spider = BookSpider()
        host, port, db = (
            os.environ.get("REDIS_HOST"),
            os.environ.get("REDIS_PORT"),
            os.environ.get("REDIS_DB", 4),
        )
        logger.info(f"{host=} {port=} {db=}")
        self.redis = redis.Redis(
            host=host,
            port=port,
            password=os.environ.get("REDIS_PASS"),
            db=db,
            decode_responses=True,
        )

        # spiders need some sort of start_url?
        self.start_urls = [GOODREADS_URL_PREFIX]
        # or use some dummy page

        # self.start_urls = []
        # for page_no in range(int(start_page_no), int(end_page_no) + 1):
        #     list_url = self.goodreads_list_url.format(list_name, page_no)
        #     self.start_urls.append(list_url)

    def redis_generator(self):
        # TODO: use pubsub or sorted sets, so you don't have to sleep
        items = self.redis.lrange(REDIS_TO_SCRAPE_KEY, 0, -1)
        logger.info(f"{self.redis.keys('*')=}")
        logger.info(f"got {len(items)} items from redis")
        items = iter(items)  # turn list into iterator
        while True:
            # item = self.redis.lpop(REDIS_TO_SCRAPE_KEY)
            # do not pop for now, since items will be lost
            try:
                item = items.__next__()
            except StopIteration:
                item = None

            if item:
                logger.info(f"yielding {item=}")
                yield f"/book/show/{item}"
            else:
                break

    def parse(self, response):
        # list_of_books = response.css("a.bookTitle::attr(href)").extract()

        # manual input override. don't know other way for now
        # list_of_books = ["/book/show/16085481-crazy-rich-asians", "/book/show/199519.The_Tibetan_Yogas_Of_Dream_And_Sleep", "/book/show/50512348-the-message-game"]
        # or listen for books through redis
        list_of_books = self.redis_generator()
        # logger.info(f"{len(list_of_books)=}")

        while True:

            for book in list_of_books:
                logger.info(f"yielding {book=}")
                yield response.follow(book, callback=self.book_spider.parse)

            logging.info(f"sleeping {REDIS_FETCH_INTERVAL} seconds")
            sleep(REDIS_FETCH_INTERVAL)
