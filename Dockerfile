FROM python:3-slim

RUN mkdir /rate-shoot/
WORKDIR /rate-shoot/
COPY . /rate-shoot/

VOLUME ["/rate-shooot/data/"]

RUN apt-get update && apt-get install -y gcc && pip install -r /rate-shoot/requirements.txt

EXPOSE 80

CMD [ "uwsgi", "rate-shoot-py.ini"]
