docker build . -t transaction_service:0.1

docker tag transaction_service:0.1 denys8herasymuk/web-banking-transaction-service:0.1

docker push denys8herasymuk/web-banking-transaction-service:0.1

kubectl create -f ./transaction_service.yaml

kubectl get pods -w