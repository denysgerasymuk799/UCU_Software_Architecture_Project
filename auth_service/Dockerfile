FROM python:3.8-slim

RUN apt-get update

ADD ./requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app/

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt

COPY ./ /opt/app/

CMD uvicorn --host 0.0.0.0 --port 8080 --workers 4 app:app