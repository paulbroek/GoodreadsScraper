"""Spider to extract all books for author_to_scrape items from PostgreSQL"""

import logging
import os.path

import jsonlines
import pandas as pd
import scrapy
from rarc_utils.sqlalchemy_base import (create_many, get_async_session,
                                        get_session)
from scrape_goodreads.models import AuthorToScrape, psql
from sqlalchemy import select

from .book_spider import BookSpider

GOODREADS_URL_PREFIX = "https://www.goodreads.com"

logger = logging.getLogger(__name__)

psql_session = get_session(psql)()

# get authors to scrape sorted by last_scraped
NSCRAPE = 20_000
q = (
    select(AuthorToScrape)
    .where(~AuthorToScrape.lock)
    .order_by(AuthorToScrape.last_scraped.desc())
    .limit(NSCRAPE)
)
to_scrape = psql_session.execute(q).scalars().fetchall()

# and set block = True, so other workers cannot pick them!
for item in to_scrape:
    item.block = True

psql_session.commit()

logger.info(f"{len(to_scrape)=:,}")

# todo: given structure of scrapy I cannot set item.done = True after succesful scraping. I can however do this later, when all workers finished
# just run update_author_to_scrape.py


class PgAuthorListSpider(scrapy.Spider):
    """Extract URLs of books from a Listopia list on Goodreads.

    This subsequently passes on the URLs to BookSpider
    """

    name = "pg_author_list"

    goodreads_list_url = "https://www.goodreads.com/author/list/{}?page={}"

    def __init__(self, list_name, start_page_no, end_page_no):
        global to_scrape
        super().__init__()
        self.book_spider = BookSpider()

        self.start_urls = []

        self.authors = to_scrape
        print(f"{len(self.authors)=}")
        for author in self.authors:
            for page_no in range(int(start_page_no), int(end_page_no) + 1):
                list_url = self.goodreads_list_url.format(author, page_no)
                self.start_urls.append(list_url)

        del self.authors, to_scrape

    def parse(self, response):
        list_of_books = response.css("a.bookTitle::attr(href)").extract()

        for book in list_of_books:
            logger.info(f"yielding {book=}")
            yield response.follow(book, callback=self.book_spider.parse)
