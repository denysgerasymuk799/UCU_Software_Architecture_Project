# Transaction Service
### Start Transaction Service
-  Start Kafka:
```bash
# Terminal-1
zookeeper-server-start.sh config/zookeeper.properties 

# Terminal-2
kafka-server-start.sh config/server.properties 
```
-  Create Kafka Topics using Python script:
```bash
python3 src/broker.py
```
- Start Kafka Consumers:
```bash
# Terminal-3
python3 wallet_service.py

# Terminal-4
python3 card_manager.py
```
- Start Kafka Producer:
```bash
# Terminal-5
python3 producer.py
```
