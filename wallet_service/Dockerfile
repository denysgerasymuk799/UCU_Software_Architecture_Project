FROM python:3.8-slim

RUN apt-get update

ADD ./requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app/

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt

COPY ./ /opt/app/

CMD python -m faust -A kafka_streams worker -l info