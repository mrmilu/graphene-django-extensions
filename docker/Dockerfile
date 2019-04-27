FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /src
WORKDIR /src
ADD . /src/
RUN pip3 install -r requirements/tests.txt
