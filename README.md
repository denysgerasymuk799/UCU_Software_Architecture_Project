# UCU Software Architecture Project

## Features

- Functionality: `Deposit money` `Send money` `List transactions` `Login/Sign Up with JWT Token`
- Technologies: `Kafka` `AWS` `React` `Python` `Docker` `Grafana` `Prometheus`
- Frameworks: `FastAPI` `Faust`
- Databases: `AWS Keyspaces` `MongoDB`
- AWS Resources: `EKS`  `ELB`  `CloudWatch` `API Gateway`  `S3` `Amplify` `IAM` `KMS` `VPC`
- Orchestration: `Kubernetes` `Cortex`


## Description

**unobank** is a web banking project creared by the students of Ukrainian Catholic University. It allows user to register and top up their accounts, send money based on the card_id of recipient, and see a list of transactions. The project's architecture is heavily decoupled by using **seven** microservices that interact with each other. The system was designed to support a large number of users, since we use NoSQL databases and **event-sourcing pattern**. We leverage the AWS cloud platform to enable secure, fast, and robust infrastructure.

## Run the Project

### Start Kafka
First run Kafka to enable communication between microservices. Download Kafka, unzip the archive and run the below scripts:

* Start zookeeper server: `./bin/zookeeper-server-start.sh config/zookeeper.properties`
* Start kafka bootstrap server: `./bin/kafka-server-start.sh config/server.properties`
* Create topic: `./bin/kafka-topics.sh --zookeeper 127.0.0.1:2181  --topic TransactionService --create --partitions 3 --replication-factor 1`

You can verify everything works correctly using the command below to read messages from topics with Kafka consumer CLI:  
`./bin/kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9092 --topic TransactionService --from-beginning`

### Prepare Configurations

For each of the microservices, create a virtual environment. More info: https://www.linuxcapable.com/how-to-setup-python-3-virtual-environment-on-ubuntu-20-04/
```shell
# Prepare the Auth Service
python3.8 -m venv auth_service_venv
source auth_service_venv/bin/activate
pip install -r requirements.txt

# Prepare the Registration Service
python3.8 -m venv registration_service_venv
source registration_service_venv/bin/activate
pip install -r requirements.txt

# Prepare the Transaction Service
python3.8 -m venv transaction_service_venv
source transaction_service_venv/bin/activate
pip install -r requirements.txt

# Prepare the Card Service
python3.8 -m venv card_service_venv
source card_service_venv/bin/activate
pip install -r requirements.txt

# Prepare the Card Manager Service
python3.8 -m venv card_manager_venv
source card_manager_venv/bin/activate
pip install -r requirements.txt

# Prepare the Orchestration Service
python3.8 -m venv orchestrator_service_venv
source orchestrator_service_venv/bin/activate
pip install -r requirements.txt
```

### Start the Microservices

**NOTE:** To start microservices specify **the same ports as in the examples below**, since links to microservices are temporary hardcoded in the .env files.

**NOTE:** Inside each microservice folder add a .env file and secrets folder. Otherwise, the launch will be unsuccessful.

```shell
# Start the Auth Service
source auth_service_venv/bin/activate
bash start_service.sh

# Start the Registration Service
source registration_service_venv/bin/activate
bash start_service.sh

# Start the Transaction Service
source transaction_service_venv/bin/activate
bash start_service.sh

# Start the Card Service
source card_service_venv/bin/activate
bash start_service.sh

# Start the Card Manager Service
source card_manager_venv/bin/activate
bash start_service.sh

# Start the Orchestration Service
source orchestrator_service_venv/bin/activate
bash start_service.sh

# Start Kafka Streams workers
faust -A kafka_streams worker -l info
# or 
bash start_service.sh
```

### Start the FrontEnd

FrontEnd is implemented using React. To launch the app, install npm on Ubuntu:  
https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04  

In case of errors on linux check this link:
https://stackoverflow.com/questions/43494794/webpack-html-webpack-plugin-error-child-compilation-failed

If above step is performed, run the below commands:
```
npm install
npm start
```

### Deploy the Project

```shell
# Main reference -- https://docs.cortex.dev/workloads/async/example
aws ecr create-repository --repository-name web_banking_auth_service

# Current value
AWS_ACCOUNT_ID=218145147595

docker tag auth_service:0.1 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_auth_service

docker tag registration_service:0.1 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_registration_service

docker push 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_auth_service

cortex deploy

cortex delete auth-service

# Deploy services interacted with kafka
docker build . -t transaction_service:0.1

docker tag transaction_service:0.1 denys8herasymuk/web-banking-transaction-service:0.1

docker push denys8herasymuk/web-banking-transaction-service:0.1
```


### Kubernetes Cluster Info

```shell
# Get a cluster info
cortex cluster info

# Open dashboards
# http://<operator_url>/dashboard

# Connect to Kubernetes with kubectl
# https://aws.amazon.com/premiumsupport/knowledge-center/eks-cluster-connection/
aws eks --region eu-central-1 update-kubeconfig --name web-banking

# To find logs, go to your account Cloudwatch

# ECR login
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 218145147595.dkr.ecr.eu-central-1.amazonaws.com
```


### Configure Confluent for Kubernetes

```shell
helm repo add confluentinc https://packages.confluent.io/helm
helm repo update
helm upgrade --install confluent-operator confluentinc/confluent-for-kubernetes
kubectl apply -f ./confluent-platform.yaml

# View Control Center
kubectl port-forward controlcenter-0 9021:9021

# And go to http://localhost:9021
```
