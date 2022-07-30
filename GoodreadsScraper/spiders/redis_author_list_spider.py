"""Spider to extract all books for a list of authors."""

import logging
import os.path

import jsonlines
import pandas as pd
import scrapy

from .book_spider import BookSpider

GOODREADS_URL_PREFIX = "https://www.goodreads.com"

logger = logging.getLogger(__name__)

# file = "/home/paul/repos/misc-scraping/misc_scraping/scrape_goodreads/scrape_goodreads/top_authors.feather"
# file = "top_authors.feather"
file = "all_authors.feather"

df = pd.read_feather(file)
# filter out existing authors
existing_items = []
AUTHOR_FILE = "author_myauthor.jl"
if os.path.isfile(AUTHOR_FILE):
    with jsonlines.open(AUTHOR_FILE) as reader:
        for obj in reader:
            existing_items.append(obj)

existing_authors = pd.DataFrame(existing_items)

# only keep new authors
if not existing_authors.empty:
    nrow_before = df.shape[0]
    df = df[~df.url.isin(existing_authors.url)]
    print(f"removed {(nrow_before - df.shape[0]):,} rows")

assert not df.empty, f"probably all authors have been scraped. implement updating existing authors / books"
# sort with best authors at top of dataset
# df = df.iloc[-20_000:].sort_values("score", ascending=False)
# for sitemap author scrape, we do not know anything about authors yet, so no score

class RedisAuthorListSpider(scrapy.Spider):
    """Extract URLs of books from a Listopia list on Goodreads.

    This subsequently passes on the URLs to BookSpider
    """

    name = "redis_author_list"

    goodreads_list_url = "https://www.goodreads.com/author/list/{}?page={}"

    def __init__(self, list_name, start_page_no, end_page_no):
        super().__init__()
        self.book_spider = BookSpider()

        self.start_urls = []

        self.authors = df.url.str.split('show/').apply(lambda x: x[-1]).to_list()
        print(f"{len(self.authors)=}")
        for author in self.authors:
            for page_no in range(int(start_page_no), int(end_page_no) + 1):
                list_url = self.goodreads_list_url.format(author, page_no)
                self.start_urls.append(list_url)

    def parse(self, response):
        list_of_books = response.css("a.bookTitle::attr(href)").extract()

        for book in list_of_books:
            logger.info(f"yielding {book=}")
            yield response.follow(book, callback=self.book_spider.parse)
