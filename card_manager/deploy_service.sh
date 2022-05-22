docker build . -t card_manager_service:0.4

docker tag card_manager_service:0.4 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_card_manager_service

docker push 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_card_manager_service

printf 'New version of the image is pushed\n\n'

cd ..

cortex delete card-manager-service

cortex deploy

printf 'Service is redeployed \n\n'

kubectl get pods -w
