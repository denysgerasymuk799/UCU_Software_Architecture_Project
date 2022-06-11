docker build . -t analytics_service:0.1

docker tag analytics_service:0.1 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_analytics_service

docker push 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_analytics_service

printf 'New version of the image is pushed\n\n'

cd ..

cortex delete analytics-service

cortex deploy

printf 'Service is redeployed \n\n'

kubectl get pods -w