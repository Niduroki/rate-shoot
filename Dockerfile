FROM python:3-slim

RUN mkdir /rate-shoot/
WORKDIR /rate-shoot/
COPY . /rate-shoot/
RUN mkdir /rate-shoot/data/

RUN apt-get update && apt-get install -y gcc && pip install -r /rate-shoot/requirements.txt

EXPOSE 80

RUN useradd rate-shoot && chown -R rate-shoot /rate-shoot
USER dbakel

VOLUME ["/rate-shooot/data/"]

CMD [ "uwsgi", "rate-shoot-py.ini"]
