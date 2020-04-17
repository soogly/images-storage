FROM python:3.7

RUN apt-get update && \
    apt-get install -y && \
    pip install uwsgi

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

#COPY . /usr/src/app/

EXPOSE 8000