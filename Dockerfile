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
# RUN pip install redis

WORKDIR /src