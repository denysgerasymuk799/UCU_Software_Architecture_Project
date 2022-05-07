FROM python:3.8-slim

RUN apt-get update

COPY ./ /opt/app/
WORKDIR /opt/app/

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt

CMD uvicorn --host 0.0.0.0 --port 8003 --workers 2 app:app