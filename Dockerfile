FROM python:3.8-slim-buster

RUN pip install pipenv

COPY Pipfile* /
RUN apt-get update && apt-get upgrade -y && \
    apt-get install build-essential -y
RUN pipenv install --system --deploy

COPY anon_api/ /anon_api
COPY config_default.yaml config_default.yaml
COPY Makefile /

WORKDIR /

ENTRYPOINT ["make", "serve"]
# ENTRYPOINT ["/bin/bash"]
