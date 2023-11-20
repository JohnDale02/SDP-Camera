import boto3
import json
from get_public_key import get_public_key
from verify_signature import verify_signature
from recreate_data import recreate_data
from upload_verified import upload_verified
from create_combined import create_combined
import base64
<<<<<<< HEAD
from send_text import send_text
=======
import cv2
import numpy as np

>>>>>>> c6c11074cbe193949772176b831aa2e307439209

def lambda_function(event, context):
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Extract bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    try:
        # Get the object from S3
        try:
            #bucket_name = 'unverifiedimages'
            #object_key = 'NewImage.png'
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            print("got an object")

        except Exception as e:
            print(f"Get object error : {e}")

       # Access the image content
        temp_image_path = 'TempNewImage.png'   # recreate the png using the cv2 png object bytes recieved
        s3_client.download_file(bucket_name, object_key, temp_image_path)
        #temp_image_path = '/tmp/image.png'
        image = cv2.imread(temp_image_path)

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
            combined_data = create_combined(camera_number, image, time_data, location_data)

        except Exception as e:
            print(f"Couldnt combine Data: {e}")
        try:
            
            valid = verify_signature(combined_data, signature, public_key)

        except Exception as e:
            print(f"Error verifying or denying signature {e}")

        if valid == True:
            upload_verified(s3_client, camera_number, time_data, location_data, signature, temp_image_path)
            print("valid signature")
        else:
            print("Signature is anything but valid")
        
        send_text(valid)
        

    except Exception as e:
        print(f'There was an exeption: {e}')

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }
