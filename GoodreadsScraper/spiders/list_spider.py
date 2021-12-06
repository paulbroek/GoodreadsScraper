"""Spider to extract URL's of books from a Listopia list on Goodreads"""

import scrapy

from .book_spider import BookSpider

GOODREADS_URL_PREFIX = "https://www.goodreads.com"

class ListSpider(scrapy.Spider):
    """Extract URLs of books from a Listopia list on Goodreads

        This subsequently passes on the URLs to BookSpider
    """
    name = "list"

    goodreads_list_url = "https://www.goodreads.com/list/show/{}?page={}"

    def __init__(self, list_name, start_page_no, end_page_no, books_from_redis=False):
        super().__init__()
        self.book_spider = BookSpider()
        self.books_from_redis = books_from_redis

        self.start_urls = []
        for page_no in range(int(start_page_no), int(end_page_no) + 1):
            list_url = self.goodreads_list_url.format(list_name, page_no)
            self.start_urls.append(list_url)

    def parse(self, response):
        list_of_books = response.css("a.bookTitle::attr(href)").extract()

        # manual input override. don't know other way for now
        list_of_books = ["/book/show/16085481-crazy-rich-asians", "/book/show/199519.The_Tibetan_Yogas_Of_Dream_And_Sleep", "/book/show/50512348-the-message-game"]
        # or listen for books through redis
        # print(f'{list_of_books=}')
        print(f'{len(list_of_books)=}')

        for book in list_of_books:
            yield response.follow(book, callback=self.book_spider.parse)
