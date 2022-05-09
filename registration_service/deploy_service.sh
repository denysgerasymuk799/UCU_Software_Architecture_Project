docker build . -t registration_service:0.1

docker tag registration_service:0.1 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_registration_service

docker push 218145147595.dkr.ecr.eu-central-1.amazonaws.com/web_banking_registration_service

printf 'New version of the image is pushed\n\n'

cd ..

cortex delete registration-service

cortex deploy

printf 'Service is redeployed \n\n'

kubectl get pods -w