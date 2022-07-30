FROM python:3.9
#FROM python:3.8
#FROM python:3.8-slim
RUN pip install --upgrade pip

RUN apt-get update   		            && \
	apt-get install git -y				&& \
	apt-get install openssh-client

#ADD ./requirements.txt /requirements.txt
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY *.whl /tmp
RUN pip install git+https://git@github.com/paulbroek/rarc-utils.git 
RUN pip install /tmp/scrape_goodreads-0.0.5-py3-none-any.whl

WORKDIR /src
