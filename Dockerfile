FROM python:3-slim

RUN mkdir /rate-shoot/
WORKDIR /rate-shoot/
COPY . /rate-shoot/
RUN mkdir /rate-shoot/data/

RUN apt-get update && apt-get install -y gcc && pip install -r /rate-shoot/requirements.txt

EXPOSE 8000

RUN useradd uwsgi && chown -R uwsgi /rate-shoot
USER uwsgi

VOLUME ["/rate-shooot/data/"]

CMD [ "uwsgi", "rate-shoot-py.ini"]
