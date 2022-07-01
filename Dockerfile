FROM python:3.8-slim-buster
LABEL maintainer="Dan Miles - dan@ondisciple.com"

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get -qq update && \
    apt-get install --no-install-recommends -qq gcc python3-pip libpq-dev python3-dev && \
    pip3 install -r requirements.txt

COPY . ./

ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]