# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

from rarc_utils.sqlalchemy_base import get_session
from scrape_goodreads.models import AuthorToScrape, psql
# Define your item pipelines here
#
from scrapy import signals
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonLinesItemExporter
from scrapy.utils.project import get_project_settings
from sqlalchemy import select

logger = logging.getLogger(__name__)

settings = get_project_settings()
UPDATE_POSTGRES_PER_ITEM = settings.get("UPDATE_POSTGRES_PER_ITEM")

if UPDATE_POSTGRES_PER_ITEM:
    psql.host = settings.get("POSTGRES_HOST")
    psql.port = os.environ.get("POSTGRES_PORT")
    psql_session = get_session(psql)()
    logger.info(f"{psql.host=}")


class JsonLineItemSegregator(object):
    @classmethod
    def from_crawler(cls, crawler):
        output_file_suffix = crawler.settings.get("OUTPUT_FILE_SUFFIX", default="")
        return cls(crawler, output_file_suffix)

    def __init__(self, crawler, output_file_suffix):
        self.types = {"book", "author"}
        self.output_file_suffix = output_file_suffix
        self.files = set()
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_opened(self, spider):
        self.files = {
            name: open(name + "_" + self.output_file_suffix + ".jl", "a+b")
            for name in self.types
        }
        self.exporters = {
            name: JsonLinesItemExporter(self.files[name]) for name in self.types
        }

        for e in self.exporters.values():
            e.start_exporting()

    def spider_closed(self, spider):
        for e in self.exporters.values():
            e.finish_exporting()

        for f in self.files.values():
            f.close()

    def process_item(self, item, spider):
        item_type = type(item).__name__.replace("Item", "").lower()
        if item_type in self.types:
            self.exporters[item_type].export_item(item)

        # update AuthorToScrape.lock = False and .last_scraped = now()
        if UPDATE_POSTGRES_PER_ITEM and item_type == "author":

            # other way: always look look up author_to_scrape, and set lock = False
            author_id = item["url"].split("show/")[-1]
            author_to_scrape = (
                psql_session.query(AuthorToScrape).filter_by(id=author_id).one_or_none()
            )

            if author_to_scrape is None:
                logger.warning(
                    f"could not find {author_id=}, not updating AuthorToScrape in db"
                )

            else:
                # logger.info(f"{author_to_scrape=}")

                author_to_scrape.lock = False
                author_to_scrape.last_scraped = datetime.utcnow()
                author_to_scrape.nscrape += 1
                author_to_scrape.nupdate += 1
                psql_session.commit()

        # todo: also decrement npage when you get rejected request for author page=3

        return item


class RedisPipeline(object):
    def process_item(self, item, spider):
        redis_item = dict(item=item)

        redis_item["crawled"] = datetime.utcnow()
        redis_item["spider"] = spider.name
        url = redis_item["item"]["url"]

        redis_item["type"] = ""
        if "/author/" in url:
            redis_item["type"] = "author"
        elif "/book/" in url:
            redis_item["type"] = "book"
        else:
            raise Exception(f"type does not exist: goodreads_{url=}")

        logger.info(f"processed item: {redis_item}")
        return redis_item
