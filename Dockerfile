FROM python:3.8.2
ENV PYTHONUNBUFFERED 1
RUN mkdir /athlete-stats
WORKDIR /athlete-stats
COPY requirements.txt /athlete-stats/
RUN pip install -r requirements.txt
COPY . /athlete-stats/
