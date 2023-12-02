FROM ubuntu:23.10

RUN apt update && apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv libpq-dev -y
COPY . .

ARG POSTGRES_PASSWORD 
ARG POSTGRES_DATABASE
ARG POSTGRES_HOST
ARG POSTGRES_USER
ARG POSTGRES_PORT

ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
ENV POSTGRES_DATABASE=$POSTGRES_DATABASE
ENV POSTGRES_HOST=$POSTGRES_HOST
ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PORT=$POSTGRES_PORT

EXPOSE 6969

RUN chmod +x docker_entry.sh

ENTRYPOINT ["/docker_entry.sh"]