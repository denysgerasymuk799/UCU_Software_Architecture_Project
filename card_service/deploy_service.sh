docker build . -t wallet_service:0.1

docker tag wallet_service:0.1 denys8herasymuk/web-banking-wallet-service:0.1

docker push denys8herasymuk/web-banking-wallet-service:0.1

kubectl create -f ./wallet_service.yaml

kubectl get pods -w