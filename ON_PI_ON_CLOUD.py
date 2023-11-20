import base64
import cv2


import boto3

# Initialize the S3 client
s3_client = boto3.client('s3')

# Define the bucket name and the key of the file you want to download
bucket_name = 'unverifiedimages'
file_key = 'NewImage.jpg'

# Define the path where you want to save the downloaded file
save_path = 'test_receated.jpg'

# Download the file from S3 and save it
s3_client.download_file(bucket_name, file_key, save_path)

print(f"File downloaded and saved at {save_path}")

image1 = cv2.imread('test.jpg')
image2 = cv2.imread('test_receated.jpg')

if image1 == image2:
    print("equal als")