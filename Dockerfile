FROM python:3.11-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install --upgrade pip \
    && pip install psycopg2

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY scrape_goodreads-0.1.1-py2.py3-none-any.whl /tmp
RUN pip install https://github.com/paulbroek/rarc-utils/archive/master.zip
RUN pip install /tmp/scrape_goodreads-0.1.1-py2.py3-none-any.whl

WORKDIR /src
