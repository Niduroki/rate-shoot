FROM python:3-slim

RUN mkdir /rate-shoot/
WORKDIR /rate-shoot/
COPY . /rate-shoot/
RUN mkdir /rate-shoot/data/

RUN apt-get update && apt-get install -y gcc fonts-freefont-ttf
ENV VIRTUAL_ENV=/rate-shoot/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

EXPOSE 8000

RUN useradd uwsgi && chown -R uwsgi /rate-shoot
USER uwsgi
RUN pip install --no-cache-dir -r /rate-shoot/requirements.txt

VOLUME ["/rate-shooot/data/"]

CMD [ "uwsgi", "rate-shoot-py.ini"]
