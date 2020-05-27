FROM python:3.8-slim-buster

RUN pip install pipenv

COPY Pipfile* /
RUN apt-get update && apt-get upgrade -y && \
    apt-get install build-essential -y
RUN pipenv install --system --deploy

COPY anon_api/ /anon_api
COPY Makefile /

WORKDIR /

ENTRYPOINT ["make", "serve"]
# ENTRYPOINT ["/bin/bash"]
