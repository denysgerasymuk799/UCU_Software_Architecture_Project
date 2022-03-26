# UCU Software Architecture Project

## How to run the project

### Kafka

* Start zookeeper server: `zookeeper-server-start.sh config/zookeeper.properties`
* Start kafka bootstrap server: `kafka-server-start.sh config/server.properties`

### Web App

```shell
# Start the service:
uvicorn app:app --reload
```