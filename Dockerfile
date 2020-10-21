FROM python:3-slim

RUN mkdir /rate-shooot/
WORKDIR /rate-shooot/
COPY . /rate-shooot/

VOLUME ["/rate-shooot/data/"]

RUN apt-get update && apt-get install -y gcc && pip install -r /dbakel/requirements.txt

EXPOSE 80

CMD [ "uwsgi", "rate-shoot-py.ini"]
