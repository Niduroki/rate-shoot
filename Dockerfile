FROM python:3-alpine

RUN mkdir /app/
WORKDIR /app/

ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /app/
RUN mkdir /app/data/

EXPOSE 8000

RUN adduser -S app && chown -R app /app

# Remove gcc & musl-dev when Pillow is installed
RUN apk add --no-cache ttf-freefont gcc g++ musl-dev \
    && pip install --no-cache-dir -r /app/requirements.txt gunicorn \
    && apk del gcc g++ musl-dev

USER app

VOLUME ["/app/data/"]

CMD [ "gunicorn", "-b", "[::]:8000", "main:app"]
