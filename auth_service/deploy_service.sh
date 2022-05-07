docker build . -t auth_service:0.4

docker tag auth_service:0.4 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_auth_service

docker push 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_auth_service

cd ..

cortex delete auth-service

cortex deploy

kubectl get pods -w