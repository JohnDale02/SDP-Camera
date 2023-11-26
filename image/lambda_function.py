import boto3
import json
import base64
import mysql.connector
import os
import base64
import cv2
import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend


# Possible updates
# - Done hardcode bucket name and object key
# - want cameras to have differnt object keys so not overwriting eachother 
#   - Ex. object_key = "NewImage_1.png" for camera 1 and "NewImage_2.png" so both devices are overwriting eachothers if picture at same time

def handler(event, context):
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Extract bucket name and object key from the event
    #bucket_name = event['Records'][0]['s3']['bucket']['name']
    #object_key = event['Records'][0]['s3']['object']['key']
    bucket_name = 'unverifiedimages'
    object_key = 'NewImage.png'

    errors = ""

    try:
        # Get the object from S3
        try:
            #bucket_name = 'unverifiedimages'
            #object_key = 'NewImage.png'
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            print("got an object")

        except Exception as e:
            print(f"Get object error : {e}")
            errors = errors + "Error:" + f"Get object error : {e}"

       # Access the image content
        temp_image_path = '/tmp/TempNewImage.png'   # recreate the png using the cv2 png object bytes recieved
        s3_client.download_file(bucket_name, object_key, temp_image_path)
        print("downloaded file (image)")

        image = cv2.imread(temp_image_path)
        print("reading image")

        # Access the object's metadata
        metadata = response['Metadata']
        print("got metadata")

        try:
            camera_number, time_data, location_data, signature = recreate_data(metadata)
            print("recreated all data")

        except Exception as e:
            print(f"Cannot recreate time and metadata {e}")
            errors = errors + "Error:" + f"Cannot recreate time and metadata {e}"
        
        try:
            public_key_base64 = get_public_key(int(camera_number))
            public_key = base64.b64decode(public_key_base64)
            print("got public key")

        except Exception as e:
            print(f"Public key error: {e}")
            errors = errors + "Error:" + f"Public key error: {e}"

        try:
            combined_data = create_combined(camera_number, image, time_data, location_data)
            print("combined data")

        except Exception as e:
            print(f"Couldnt combine Data: {e}")
            errors = errors + "Error:" + f"Couldnt combine Data: {e}"
        try:
            
            valid = verify_signature(combined_data, signature, public_key)
            print("verify signature done")

        except Exception as e:
            print(f"Error verifying or denying signature {e}")
            errors = errors + "Error:" + f"Error verifying or denying signature {e}"

        if valid == True:
            upload_verified(s3_client, camera_number, time_data, location_data, signature, temp_image_path)
            print("uploading to correct bucket")
        else:
            print("Signature is anything but valid")
            errors = errors + "Signature is invalid"
        
        #send_text(valid)
        

    except Exception as e:
        print(f'There was an exeption: {e}')
        errors = errors + f'There was an exeption: {e}'

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!'),
        'errors': errors,
    }



def recreate_data(metadata):
    '''Intakes cv2 image data and metadata; returns camera number, time, location, signature, creates image file'''

    camera_number = metadata.get('cameranumber')
    time_data = metadata.get('time')
    location_data = metadata.get('location')
    
    signature_string = metadata.get('signature')
    signature = base64.b64decode(signature_string)

    return camera_number, time_data, location_data, signature


def create_combined(camera_number: str, image: bytes, time: str, location: str) -> bytes:
    '''Takes in camera number, image, time, location and encodes then combines to form one byte object'''

    # Encode the image as a JPEG byte array
    _, encoded_image = cv2.imencode(".png", image)
    encoded_image = encoded_image.tobytes()

    encoded_number = camera_number.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_number + encoded_image + encoded_time + encoded_location

    return combined_data



def get_public_key(camera_number):
    # Environment variables for database connection
    #host = os.environ['DB_HOST']
    #user = os.environ['DB_USER']
    #password = os.environ['DB_PASSWORD']
    #database = os.environ['DB_NAME']
    host = "publickeycamerastorage.c90gvpt3ri4q.us-east-2.rds.amazonaws.com"
    user = "sdp"
    password = "sdpsdpsdp"
    database = "PublicKeySchema"

    # Connect to the database
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()

    # SQL query to retrieve the public key
    query = "SELECT PublicKey FROM Cameras WHERE CameraNumber = %s"

    cursor.execute(query, (int(camera_number),))

    # Fetch the result
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        public_key = result[0]
    
        return public_key  # Return the public key
    
    else:
        return 'Public key not found'
    



def upload_verified(s3_client, camera_number, time_data, location_data, signature, temp_image_path):
# Get S3 bucket for verified images(camera_number)

    destination_bucket_name = f'camera{int(camera_number)}verifiedimages'

    try:
        image_number = count_objects_in_bucket(destination_bucket_name) // 2

    except Exception as e:
        print(f"Count objects in bucket error: {e}")

    image_file_name = str(image_number) + '.png'  # Changes file extension to .json

    # Create JSON data
    json_data = {
        "Time": time_data,  # string
        "Location": location_data,   # string
        "Signature_Base64": base64.b64encode(signature).decode('utf-8')  # signature is in base64 encoded (string)
    }

    # Save JSON data to a file with the same name as the image
    json_file_name = str(image_number) + '.json'  # Changes file extension to .json

    temp_json_path = f'/tmp/{json_file_name}'


    with open(temp_json_path, 'w') as json_file:
        json.dump(json_data, json_file)

    try:
        s3_client.upload_file(temp_image_path, destination_bucket_name, image_file_name)

    except Exception as e:
        print(f"Upload Image to verified bucket error: {e}")
        
    try:     # Upload JSON file to the same new S3 bucket
        s3_client.upload_file(temp_json_path, destination_bucket_name, json_file_name)
        
    except Exception as e:
        print(f"Uploading JSON error : {e}")

    # Clean up: Delete temporary files
    os.remove(temp_image_path)
    os.remove(temp_json_path)


def count_objects_in_bucket(bucket_name):
    print("Called 'count objects")
    s3 = boto3.client('s3')
    total_objects = 0

    # Use paginator to handle buckets with more than 1000 objects
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        total_objects += len(page.get('Contents', []))

    return total_objects



def verify_signature(combined_data, signature, public_key):


    temp_public_key_path = '/tmp/recreated_public_key.pem'

    with open(temp_public_key_path, "wb") as file:   # write our decoded public key data back to a pem file
            file.write(public_key)

    with open(temp_public_key_path, "rb") as key_file:
            public_key_data = key_file.read()

    # Deserialize the public key from PEM format
    public_key = serialization.load_pem_public_key(public_key_data)

    try:
        public_key.verify(
            signature,
            combined_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print('Signature is valid')
        os.remove(temp_public_key_path)
        return True
    
    except InvalidSignature:
        print('Signature verification failed')
        os.remove(temp_public_key_path)
        return False
    

