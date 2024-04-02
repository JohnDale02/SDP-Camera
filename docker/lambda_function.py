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
import hashlib
import subprocess

# Possible updates
# - Done hardcode bucket name and object key
# - want cameras to have differnt object keys so not overwriting eachother 
#   - Ex. object_key = "NewImage_1.png" for camera 1 and "NewImage_2.png" so both devices are overwriting eachothers if picture at same time

def handler(event, context):
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Extract bucket name and object key from the event
    object_key = str(event['Records'][0]['s3']['object']['key'])
    print("Object key: should be NewImage.png or NewVideo.avi", object_key)
    bucket_name = 'unverifiedimages'

    image = False   # video default
    if object_key.endswith(".png"):
        image = True  # we have an image now 
    
    print(f"Is this an image: {image}")

    errors = ""

    try:
        # Get the object from S3
        try:
            #bucket_name = 'unverifiedimages'
            #object_key = 'NewImage.png'
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        except Exception as e:
            errors = errors + "Error:" + f"Get object error : {str(e)}"


        if image: 
            temp_media_path = '/tmp/TempNewImage.png'   # recreate the png using the cv2 png object bytes recieved
            s3_client.download_file(bucket_name, object_key, temp_media_path)
            media = cv2.imread(temp_media_path)
            _, encoded_image = cv2.imencode('.png', media)  # we send the encoded image to the cloud
            encoded_media = encoded_image.tobytes()

        else:
            temp_media_path = '/tmp/TempNewVideo.avi'
            s3_client.download_file(bucket_name, object_key, temp_media_path)
            print("Downloading video Done")
            temp_mp4_path = '/tmp/TempNewMp4.mp4'

            with open(temp_media_path, 'rb') as video:
                encoded_media = video.read()
                print(encoded_media[-10:])
                
        # Access the object's metadata
        metadata = response['Metadata']

        try:
            fingerprint, camera_number, time_data, location_data, signature, signature_string = recreate_data(metadata)

        except Exception as e:
            errors = errors + "Error:" + f"Cannot recreate time and metadata {str(e)}"

        try: 
            print("Storing json details")
            store_json_details(temp_media_path, fingerprint, camera_number, time_data, location_data, signature_string)
            print("Stored json details")
        except Exception as e: 
            errors = errors + "Error:" + f"Cannot store json details {str(e)}"
        
        try:
            public_key_base64 = get_public_key(int(camera_number))
            public_key = base64.b64decode(public_key_base64)

        except Exception as e:
            errors = errors + "Error:" + f"Public key error: {str(e)}"

        try:
            combined_data = create_combined(camera_number, encoded_media, time_data, location_data)

        except Exception as e:
            errors = errors + "Error:" + f"Couldnt combine Data: {str(e)}"
        try: 
            valid = verify_signature(combined_data, signature, public_key)

        except Exception as e:
            errors = errors + "Error:" + f"Error verifying or denying signature {str(e)}"

        if valid == True:
            try:
                media_save_name, media_number = upload_verified(s3_client, fingerprint, camera_number, time_data, location_data, signature, temp_media_path, image)  # save the AVI file

            except Exception as e:
                errors = errors + "Issue uploading to verified bucket" + str(e)

            try: 
                convert_to_mp4(temp_media_path, temp_mp4_path)
                upload_verified_mp4(s3_client, camera_number, temp_mp4_path, media_number)  # create and save a mp4 file

            except Exception as e:
                errors = errors + "Issue uploading to verified bucket" + str(e)

            try:
                send_text(valid, media_save_name)

            except Exception as e:
                errors = errors + "Issue Sending text: " + str(e)

            os.remove(temp_media_path)
            os.remove(temp_mp4_path)
            
        else:
            try:
                send_text(valid)

            except Exception as e:
                errors = errors + "Issue Sending text after failing verification" + str(e)


    except Exception as e:
        errors = errors + f'There was an exeption: {str(e)}'

    print("Errors: ", errors)

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!'),
        'errors': errors,
    }


def recreate_data(metadata):
    '''Intakes cv2 image data and metadata; returns camera number, time, location, signature, creates image file'''

    fingerprint = metadata.get('fingerprint')
    camera_number = metadata.get('cameranumber')
    time_data = metadata.get('time')
    location_data = metadata.get('location')
    
    signature_string = metadata.get('signature')
    signature = base64.b64decode(signature_string)

    return fingerprint, camera_number, time_data, location_data, signature, signature_string


def create_combined(fingerprint: str, camera_number: str, media: bytes, time: str, location: str) -> bytes:
    '''Takes in fingerprint, camera number, image, time, location and encodes then combines to form one byte object'''

    encoded_fingerprint = fingerprint.encode('utf-8')
    encoded_number = camera_number.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_fingerprint + encoded_number + media + encoded_time + encoded_location

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
    


def upload_verified(s3_client, fingerprint, camera_number, time_data, location_data, signature, temp_media_path, image): #################### CHANGED TO FINGERPRINt, BUCKET NOT BASED ON NUMBER BUT FINGERPRINT
# Get S3 bucket for verified images(camera_number)
    bucket_name  = ''.join(fingerprint.split()).lower()
    destination_bucket_name = bucket_name

    try:
        media_number = get_next_number_for_new_file(destination_bucket_name)

    except Exception as e:
        pass
    
    if image:
        media_file_name = str(media_number) + '.png'  # Changes file extension
    else:
        media_file_name = str(media_number) + '.avi'

    # Create JSON data
    json_data = {
        "Fingerprint": fingerprint,  # string
        "Camera Number": camera_number,
        "Time": time_data,  # string
        "Location": location_data,   # string
        "Signature_Base64": base64.b64encode(signature).decode('utf-8')  # signature is in base64 encoded (string)
    }

    # Save JSON data to a file with the same name as the image
    json_file_name = str(media_number) + '.json'  # Changes file extension to .json

    temp_json_path = f'/tmp/{json_file_name}'


    with open(temp_json_path, 'w') as json_file:
        json.dump(json_data, json_file)

    try:
        s3_client.upload_file(temp_media_path, destination_bucket_name, media_file_name)

    except Exception as e:
        pass
        
    try:     # Upload JSON file to the same new S3 bucket
        s3_client.upload_file(temp_json_path, destination_bucket_name, json_file_name)
        
    except Exception as e:
        pass
        #print(f"Uploading JSON error : {e}")

    # Clean up: Delete temporary files
    os.remove(temp_json_path)

    return media_file_name, media_number


def upload_verified_mp4(s3_client, fingerprint, temp_mp4_path, media_number):  #################### CHANGED TO FINGERPRING, BUCKET NOT BASED ON NUMBER BUT FINGERPRINT
# Get S3 bucket for verified images(camera_number)
    bucket_name  = ''.join(fingerprint.split()).lower()
    destination_bucket_name = bucket_name

    media_file_name = str(media_number) + '.mp4'

    try:
        s3_client.upload_file(temp_mp4_path, destination_bucket_name, media_file_name, ExtraArgs={'ContentType': 'video/mp4'})

    except Exception as e:
        pass


def get_next_number_for_new_file(bucket_name):
    s3 = boto3.client('s3')
    
    # Use paginator to ensure we check all objects if there are more than 1000
    paginator = s3.get_paginator('list_objects_v2')
    highest_number = 0

    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            file_name = obj['Key']
            try:
                # Extract the number from the file name
                number = int(file_name.split('.')[0])
                if number > highest_number:
                    highest_number = number
            except ValueError:
                # If the file name does not start with a number, ignore it
                continue
    
    # Assuming the sequence is uninterrupted and follows the naming convention strictly
    next_number = highest_number + 1
    return next_number



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

    account_sid = 'SID HERE'
    auth_token = 'AUTH TOKEN HERE'
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


def store_json_details(temp_image_path, fingerprint, camera_number, time_data, location_data, signature):
    # Hash the image data to use as an index
    with open(temp_image_path, 'rb') as file:
        data = file.read()
        hash_object = hashlib.sha256()
        hash_object.update(data)
        image_hash = hash_object.hexdigest()

    # Convert details to JSON format
    details = json.dumps({
        'Fingerprint': fingerprint,
        'Camera Number': camera_number,
        'Time': time_data,
        'Location': location_data,
        'Signature_Base64': signature
    })
    
    print(f"Image Hash: {image_hash}")
    print(f"Details: {details}")

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


def convert_to_mp4(temp_media_path, temp_mp4_path):

    print("Trying to convert to mp4 from avi...........")

    command_convert_to_mp4 = [
        'ffmpeg',
        '-i', temp_media_path,          # Input file path
        '-c:v', 'libx264',              # Video codec to use (H.264)
        '-crf', '23',                   # Constant Rate Factor (CRF) value, 18-28 is a good range, lower is higher quality
        '-preset', 'medium',          # Preset for compression efficiency (you can use 'medium' for a balance between speed and quality)
        '-c:a', 'aac',                  # Audio codec to use (AAC)
        '-b:a', '128k',                 # Audio bitrate
        '-strict', 'experimental',      # Allow experimental codecs (if needed for AAC)
        temp_mp4_path                   # Output file path
    ]

    process = subprocess.Popen(command_convert_to_mp4, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(f"Video output: stdout {stdout}, stderr: {stderr}")