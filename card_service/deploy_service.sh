docker build . -t card_service:0.1

docker tag card_service:0.1 denys8herasymuk/web-banking-card-service:0.1

docker push denys8herasymuk/web-banking-card-service:0.1

kubectl create -f ./card_service.yaml

kubectl get pods -w