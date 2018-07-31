
FROM ubuntu:latest

MAINTAINER raxvan

RUN apt-get update && apt-get install -y \
	git \
	python3-pip \
	python3-dev \
	build-essential


RUN pip3 install --upgrade pip && pip install \
	ply


