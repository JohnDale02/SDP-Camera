import boto3
import json
from get_public_key import get_public_key
from verify_signature import verify_signature
from recreate_data import recreate_data
from upload_verified import upload_verified
import base64
import cv2
import numpy as np


def lambda_function(event, context):
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Extract bucket name and object key from the event
    #bucket_name = event['Records'][0]['s3']['bucket']['name']
    #object_key = event['Records'][0]['s3']['object']['key']

    try:
        # Get the object from S3
        try:
            bucket_name = 'unverifiedimages'
            object_key = 'NewImage.jpg'
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            print("got an object")

        except Exception as e:
            print(f"Get object error : {e}")

       # Access the object's content
        image_bytes = response['Body'].read()   # this is the base64 encoded image
        temp_image_path = 'TempNewImage.jpg'   # recreate the jpg using the cv2 jpg object bytes recieved
        s3_client.download_file(bucket_name, object_key, temp_image_path)
        #temp_image_path = '/tmp/image.jpg'
        image = cv2.imread(temp_image_path)
        # Download the file from S3 and save it

        # Save the decoded image
        print(image, "ended Image")

        # Access the object's metadata
        metadata = response['Metadata']

        try:
            camera_number, time_data, location_data, signature = recreate_data(metadata)

        except Exception as e:
            print(f"Cannot recreate time and metadata {e}")
        
        try:
            public_key_base64 = get_public_key(int(camera_number))
            public_key = base64.b64decode(public_key_base64)

        except Exception as e:
            print(f"Public key error: {e}")

        try:
            valid = verify_signature(image, camera_number, time_data, location_data, signature, public_key)

        except Exception as e:
            print(f"Error verifying or denying signature {e}")

        if valid == True:
            upload_verified(s3_client, camera_number, time_data, location_data, signature, temp_image_path)
            print("valid signature")
        else:
            print("Signature is anything but valid")
        

    except Exception as e:
        print(f'There was an exeption: {e}')

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }



lambda_function(None, None)