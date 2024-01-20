import boto3
import json
import base64
import mysql.connector
import os
import base64
import cv2
import numpy as np
import os
from twilio.rest import Client
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

        except Exception as e:
            errors = errors + "Error:" + f"Get object error : {str(e)}"

       # Access the image content
        temp_image_path = '/tmp/TempNewImage.png'   # recreate the png using the cv2 png object bytes recieved
        s3_client.download_file(bucket_name, object_key, temp_image_path)

        image = cv2.imread(temp_image_path)

        # Access the object's metadata
        metadata = response['Metadata']

        try:
            camera_number, time_data, location_data, signature = recreate_data(metadata)

        except Exception as e:
            errors = errors + "Error:" + f"Cannot recreate time and metadata {str(e)}"
        
        try:
            public_key_base64 = get_public_key(int(camera_number))
            public_key = base64.b64decode(public_key_base64)

        except Exception as e:
            errors = errors + "Error:" + f"Public key error: {str(e)}"

        try:
            combined_data = create_combined(camera_number, image, time_data, location_data)

        except Exception as e:
            errors = errors + "Error:" + f"Couldnt combine Data: {str(e)}"
        try: 
            valid = verify_signature(combined_data, signature, public_key)

        except Exception as e:
            errors = errors + "Error:" + f"Error verifying or denying signature {str(e)}"

        if valid == True:
            try:
                image_save_name = upload_verified(s3_client, camera_number, time_data, location_data, signature, temp_image_path)
                send_text(valid, image_save_name)

            except Exception as e:
                errors = errors + "Issue Sending text or uploading to verified bucket" + str(e)
            
        else:
            try:
                send_text(valid)

            except Exception as e:
                errors = errors + "Issue Sending text after failing verification" + str(e)


    except Exception as e:
        errors = errors + f'There was an exeption: {str(e)}'

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

    # Encode the image as a PNG byte array
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
        pass

    image_file_name = str(image_number) + '.png'  # Changes file extension to .json

    # Create JSON data
    json_data = {
        "Camera Number": camera_number,
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
        pass
        
    try:     # Upload JSON file to the same new S3 bucket
        s3_client.upload_file(temp_json_path, destination_bucket_name, json_file_name)
        
    except Exception as e:
        pass
        #print(f"Uploading JSON error : {e}")

    # Clean up: Delete temporary files
    os.remove(temp_image_path)
    os.remove(temp_json_path)

    return image_file_name


def count_objects_in_bucket(bucket_name):
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
        os.remove(temp_public_key_path)
        return True
    
    except InvalidSignature:
        os.remove(temp_public_key_path)
        return False
    

def send_text(valid, image_save_name="default"):

    account_sid = 'AC8010fcf8a7c9217f2e222a62cc0e49cf'
    auth_token = 'AUTH TOKEN'
    client = Client(account_sid, auth_token)

    if valid == True:
        Body = f"Your Image was Successfully Authenticated. Stored as {image_save_name}"

    else:
        Body = f"Your Image failed to be Authenticated. Deleted"

    message = client.messages.create(
    from_='+18573664416',
    body=Body,
    to='+17819159187'
    )


def store_json_details(image, camera_number, time_data, location_data, signature):
    # Hash the image data to use as an index
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(image.read())
    image_hash = digest.finalize().hex()

    # Convert details to JSON format
    details = json.dumps({
        'Camera Number': camera_number,
        'Time': time_data,
        'Location': location_data,
        'Signature_Base64': signature
    })

    # Database connection details
    host = "publickeycamerastorage.c90gvpt3ri4q.us-east-2.rds.amazonaws.com"
    user = "sdp"
    password = "sdpsdpsdp"
    database = "PublicKeySchema"

    # Connect to the database
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()

    query = """
    INSERT INTO image_data (image_hash, data)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE data = %s
    """

    cursor.execute(query, (image_hash, details, details))
    
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    print(f"Stored the data with image hash {image_hash}, Time: {time_data}")

def get_json_details(image_hash):
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

    # SQL query to retrieve the data for given image_hash
    query = "SELECT data FROM image_data WHERE image_hash = %s"

    cursor.execute(query, (str(image_hash),))

    # Fetch the result
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        data = json.loads(result['data'])
        camera_number = data.get("Camera Number")
        time_data = data.get("Time")
        location_data = data.get("Location")
        signature = data.get("Signature_Base64")
        return camera_number, time_data, location_data, signature
    else:
        return None, None, None, None
