"""Spider to extract information from a /book/show type page on Goodreads"""

import logging

import scrapy

from ..items import BookItem, BookLoader
from .author_spider import AuthorSpider

logger = logging.getLogger(__name__)


class BookSpider(scrapy.Spider):
    """Extract information from a /book/show type page on Goodreads"""

    name = "book"

    def __init__(self):
        super().__init__()
        self.author_spider = AuthorSpider()
        self.author_parser = self.author_spider.parse

    # def parse(self, response):
    #     loader = BookLoader(BookItem(), response=response)

    #     loader.add_value("url", response.request.url)

    #     loader.add_css("cover_image", "#coverImage::attr(src)")  # added by paul
    #     loader.add_css("title", "#bookTitle::text")
    #     loader.add_css("author", "a.authorName>span::text")

    #     loader.add_css("num_ratings", "[itemprop=ratingCount]::attr(content)")
    #     loader.add_css("num_reviews", "[itemprop=reviewCount]::attr(content)")
    #     loader.add_css("avg_rating", "span[itemprop=ratingValue]::text")
    #     loader.add_css("num_pages", "span[itemprop=numberOfPages]::text")

    #     # loader.add_css("description", "#description span") # added by paul
    #     loader.add_css("description", "div.readable")  # added by paul

    #     loader.add_css("language", "div[itemprop=inLanguage]::text")
    #     loader.add_css("publish_date", "div.row::text")
    #     loader.add_css("publish_date", "nobr.greyText::text")

    #     loader.add_css("original_publish_year", "nobr.greyText::text")

    #     loader.add_css("genres", 'div.left>a.bookPageGenreLink[href*="/genres/"]::text')
    #     loader.add_css("awards", "a.award::text")
    #     loader.add_css("characters", 'a[href*="/characters/"]::text')
    #     loader.add_css("places", "div.infoBoxRowItem>a[href*=places]::text")
    #     loader.add_css("series", 'div.infoBoxRowItem>a[href*="/series/"]::text')

    #     loader.add_css("asin", "div.infoBoxRowItem[itemprop=isbn]::text")
    #     loader.add_css("isbn", "div.infoBoxRowItem[itemprop=isbn]::text")
    #     loader.add_css("isbn", "span[itemprop=isbn]::text")
    #     loader.add_css("isbn", "div.infoBoxRowItem::text")
    #     loader.add_css("isbn13", "div.infoBoxRowItem[itemprop=isbn]::text")
    #     loader.add_css("isbn13", "span[itemprop=isbn]::text")
    #     loader.add_css("isbn13", "div.infoBoxRowItem::text")

    #     loader.add_css("rating_histogram", 'script[type*="protovis"]::text')

    #     # TODO february '23': scrape all data directly from json object?

    #     yield loader.load_item()

    #     author_url = response.css("a.authorName::attr(href)").extract_first()
    #     logger.info(f"{author_url=}")
    #     # yield response.follow(author_url, callback=self.author_spider.parse)
    #     yield response.follow(author_url, callback=self.author_parser)

    def parse(self, response, loader=None):
        if not loader:
            loader = BookLoader(BookItem(), response=response)

        loader.add_value("url", response.request.url)

        # The new Goodreads page sends JSON in a script tag
        # that has these values

        loader.add_css("title", "script#__NEXT_DATA__::text")
        # loader.add_css('title_complete', 'script#__NEXT_DATA__::text')
        loader.add_css("description", "script#__NEXT_DATA__::text")
        loader.add_css("cover_image", "script#__NEXT_DATA__::text")
        loader.add_css("genres", "script#__NEXT_DATA__::text")
        loader.add_css("asin", "script#__NEXT_DATA__::text")
        loader.add_css("isbn", "script#__NEXT_DATA__::text")
        loader.add_css("isbn13", "script#__NEXT_DATA__::text")
        # loader.add_css("publisher", "script#__NEXT_DATA__::text")
        loader.add_css("series", "script#__NEXT_DATA__::text")
        loader.add_css("author", "script#__NEXT_DATA__::text")
        loader.add_css("publish_date", "script#__NEXT_DATA__::text")

        loader.add_css("characters", "script#__NEXT_DATA__::text")
        loader.add_css("places", "script#__NEXT_DATA__::text")
        loader.add_css("rating_histogram", "script#__NEXT_DATA__::text")
        loader.add_css("num_ratings", "script#__NEXT_DATA__::text")
        loader.add_css("num_reviews", "script#__NEXT_DATA__::text")
        loader.add_css("num_pages", "script#__NEXT_DATA__::text")
        # loader.add_css("format", 'script#__NEXT_DATA__::text')

        loader.add_css("language", "script#__NEXT_DATA__::text")
        loader.add_css("awards", "script#__NEXT_DATA__::text")

        yield loader.load_item()

        author_url = response.css("a.ContributorLink::attr(href)").extract_first()
        yield response.follow(author_url, callback=self.author_spider.parse)
