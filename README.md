# UCU Software Architecture Project

## How to run the project

### Kafka

* Start zookeeper server: `zookeeper-server-start.sh config/zookeeper.properties`
* Start kafka bootstrap server: `kafka-server-start.sh config/server.properties`

### How to start the project

**Note,** specify the same ports like in the below examples, to start microservices, 
since links to microservices are temporary hardcoded:

```shell
# Create Kafka topics
kafka-topics --zookeeper 127.0.0.1:2181  --topic TransactionService --create --partitions 3 --replication-factor 1

# Read messages from topics with Kafka consumer CLI
kafka-console-consumer --bootstrap-server 127.0.0.1:9092 --topic TransactionService --from-beginning

# Start the web app
# Firstly, create a new virtual env
# https://www.linuxcapable.com/how-to-setup-python-3-virtual-environment-on-ubuntu-20-04/
sudo apt install python3.8-venv
python3.8 -m venv web_app_venv
source web_app_venv/bin/activate
pip install -r requirements.txt

gunicorn --bind 127.0.0.1:8000  app:app


# Start the Auth Service
python3.8 -m venv auth_service_venv
source auth_service_venv/bin/activate
pip install -r requirements.txt

# Do not forget to add .env file and secret folder
# Use vpn-eu
uvicorn app:app --workers 2 --reload --port 8002


# Start the Registration Service
python3.8 -m venv registration_service_venv
source registration_service_venv/bin/activate
pip install -r requirements.txt

# Do not forget to add .env file
uvicorn app:app --workers 2 --reload --port 8003


# Start the Registration Service
python3.8 -m venv transaction_service_venv
source transaction_service_venv/bin/activate
pip install -r requirements.txt

# Do not forget to add .env file
uvicorn app:app --workers 2 --reload --port 8004

# Test user credentials located in /auth_service/.env
```

### How to deploy the project

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
```


### Kubernetes cluster info

```shell
# Get a cluster info
cortex cluster info

# Open dashboards
http://<operator_url>/dashboard

# Connect to Kubernetes with kubectl
https://aws.amazon.com/premiumsupport/knowledge-center/eks-cluster-connection/
aws eks --region eu-central-1 update-kubeconfig --name web-banking

# To find logs, go to your account Cloudwatch

# ECR login
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com
```