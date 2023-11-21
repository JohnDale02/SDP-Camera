
# Pushing built image to ECR for Lambda
# Tutorial Here: https://docs.aws.amazon.com/lambda/latest/dg/python-image.html 

aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 359793706805.dkr.ecr.us-east-2.amazonaws.com
docker build --platform linux/amd64 -t <any_image_name_you_want>:test . 
docker push 359793706805.dkr.ecr.us-east-2.amazonaws.com/sdp:latest

# Testing Local Deployment
terminal: docker run -p 9000:8080 <any_image_name_you_want>:test  
Windows Powershell:  Invoke-WebRequest -Uri "http://localhost:9000/2015-03-31/functions/function/invocations" -Method Post -Body '{}' -ContentType "application/json"



# Pushing built image to Docker Hub

docker login --username johndale02
docker tag docker-image:test johndale02/sdp:test
docker push johndale02/sdp:test