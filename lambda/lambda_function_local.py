import boto3
import json
from get_public_key import get_public_key
from verify_signature import verify_signature
from recreate_data import recreate_data
from upload_verified import upload_verified
import base64
import cv2


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

        except Exception as e:
            print(f"Get object error : {e}")

       # Access the object's content
        image_base64 = response['Body'].read()   # this is the base64 encoded image
        temp_image_path = 'NewImage.jpg'   # recreate the jpg using the cv2 jpg object bytes recieved
        #temp_image_path = '/tmp/image.jpg'

        # Access the object's metadata
        metadata = response['Metadata']

        try:
            camera_number, time_data, location_data, signature = recreate_data(image_base64, metadata, temp_image_path)

        except Exception as e:
            print(f"Cannot recreate time and metadata {e}")
        
        try:
            public_key_base64 = get_public_key(int(camera_number))
            public_key = base64.b64decode(public_key_base64)

        except Exception as e:
            print(f"Public key error: {e}")

        try:
            valid = verify_signature(temp_image_path, camera_number, time_data, location_data, signature, public_key)

        except Exception as e:
            print(f"Error verifying or denying signature {e}")

        if valid == True:
            upload_verified(s3_client, camera_number, time_data, location_data, signature, temp_image_path)

        else:
            print("Signature is anything but valid")
        

    except Exception as e:
        print(f'There was an exeption: {e}')

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }



signature = 'aEsyPeQVLBp47t1y9yqP5q64jNHOlQ0lVOCcKKmiyRvMjDOEPISY9dcKnm+ujL8LfuVsVJt4j4K7PJQN5S/RMytHj6xXgzn3LGVNL6b5GqKe1/d16LImCSC+vtqsMFTsFKDzylF461Q/nKpYSVHi2G6HaBYCN0qj69qbciBOZjJWPagEAAvOs8rHbImybruKhFj5Q3MgiyeDOzeKCS5EvNK2jOWkZdOuQNFFrJQSAalOClTk9RHEdpTh4/VZdONTsSMOjm56JCoqIKW+D0475hPb4t8A4sXbYGITK1VR2n90OvxadMM6Gv21oXA9zalqU5hzCp6EahK/opLER7vYGg=='
