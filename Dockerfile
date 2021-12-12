FROM debian:10

LABEL maintainer="dmintz"

RUN apt-get update --fix-missing
RUN apt-get install -y python3 python3-dev python3-pip nginx
RUN pip3 install uwsgi

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY ./ /app
WORKDIR /app

ENV WEBROOT='/'
ENV TIME_ZONE='UTC'
ENV STATIONS_FILE='/app/stations.json'

ENV log_level=INFO
ENV MAX_TRAINS=10
ENV MAX_MINUTES=30
ENV CACHE_SECONDS=60
ENV THREADED=False

EXPOSE 80
CMD [ "uwsgi", "--ini", "/app/MTAPI.ini" ]