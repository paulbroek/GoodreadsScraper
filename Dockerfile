FROM python:3.11
RUN pip install --upgrade pip

# RUN apt-get update   		            && \
# 	apt-get install git -y				&& \
# 	apt-get install openssh-client

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY scrape_goodreads-0.1.1-py2.py3-none-any.whl /tmp
RUN pip install git+https://git@github.com/paulbroek/rarc-utils.git 
RUN pip install /tmp/scrape_goodreads-0.1.1-py2.py3-none-any.whl

RUN pip install git+https://github.com/rmax/scrapy-redis
RUN pip install -U Scrapy

WORKDIR /src
