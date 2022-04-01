# UCU Software Architecture Project

## How to run the project

### Kafka

* Start zookeeper server: `zookeeper-server-start.sh config/zookeeper.properties`
* Start kafka bootstrap server: `kafka-server-start.sh config/server.properties`

### How to start the project

**Note,** specify the same ports like in the below examples, to start microservices, 
since links to microservices are temporary hardcoded:

```shell
# Start the web app
gunicorn --bind 127.0.0.1:8000  app:app

# Start the Auth Service
uvicorn app:app --workers 2 --reload --port 8002

# Start the Registration Service
uvicorn app:app --workers 2 --reload --port 8003
```