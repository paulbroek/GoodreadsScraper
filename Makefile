PYTHON=python

PACKAGE=GoodreadsScraper
PYDIR :=./$(PACKAGE)
PYSRC := $(shell find $(PYDIR) -type f -name '*.py')
DIST=./dist

# TESTS_DIR=./tests

SCRAPER_DIR=.
SCRAPER_NAME=scrape-goodreads-redis
SCRAPER_DOCKERFILE=$(SCRAPER_DIR)/Dockerfile
SCRAPER_LOG_FILE=$(SCRAPER_DIR)/scrapy.log

# SITEMAP_TO_REDIS_NAME="sitemap-to-redis"
# POPULATE_REDIS_NAME="populate-redis"
# PARSE_REDIS_NAME="parse-redis"
# REDIS_TO_PG_NAME="redis-to-pg"
# API_NAME="meetup-api"

all: clean scraper

.PHONY: scraper
scraper: clean_scraper
	touch $(SCRAPER_LOG_FILE) && docker rm -f $(SCRAPER_NAME) && docker-compose up --build -d $(SCRAPER_NAME) && $(MAKE) scrapy_logs

.PHONY: docker_logs
docker_logs:
	docker-compose logs -f $(SCRAPER_NAME)

.PHONY: scrapy_logs
scrapy_logs:
	tail -n 100 -f $(SCRAPER_LOG_FILE)

clean:
	rm -f $(DIST)/*
	rm -rf build/*
	touch $(SCRAPER_LOG_FILE)
	echo "" > $(SCRAPER_LOG_FILE)

clean_scraper:
	docker rm -f $(SCRAPER_NAME)

# TODO: clean dupefilter
clean_redis:
	create command!
