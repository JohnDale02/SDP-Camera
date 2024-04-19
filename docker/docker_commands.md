# Pushing built image to ECR for Lambda
# Tutorial Here: https://docs.aws.amazon.com/lambda/latest/dg/python-image.html 

aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 359793706805.dkr.ecr.us-east-2.amazonaws.com

aws ecr create-repository --repository-name my-repo --region my-region
aws ecr create-repository --repository-name live --region us-east-2   

docker build --platform linux/amd64 -t <any_image_name_you_want> . 
 docker build --platform linux/amd64 -t liveverify .    

docker tag <any_image_name_you_want>:<tag> 359793706805.dkr.ecr.us-east-2.amazonaws.com/<any_image_name_you_want>:<tag>
docker tag liveverify 359793706805.dkr.ecr.us-east-2.amazonaws.com/live:my-tag    


docker push 359793706805.dkr.ecr.us-east-2.amazonaws.com/sdp:latest
docker push 359793706805.dkr.ecr.us-east-2.amazonaws.com/live:my-tag    
# --------------------------------------------------^^^^^^ image name : tag example

# Pushing changes to an Image if you want to update it 

docker build --platform linux/amd64 -t idk .
docker tag idk 359793706805.dkr.ecr.us-east-2.amazonaws.com/final:latest
docker push 359793706805.dkr.ecr.us-east-2.amazonaws.com/final:latest


# Testing Local Deployment
terminal: docker run -p 9000:8080 <any_image_name_you_want>:test  
Windows Powershell:  Invoke-WebRequest -Uri "http://localhost:9000/2015-03-31/functions/function/invocations" -Method Post -Body '{}' -ContentType "application/json"




MYSQL PASSWORD:

username: sdp
password sdpsdpsdp