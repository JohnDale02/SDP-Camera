# File for validating stored PNG images with JSON pair file

import json
import base64
import cv2
import mysql.connector
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
import os

def verify_image_and_metadata(video_path, json_path):

    # Read the image
  
    with open(video_path, 'rb') as video:
        video_bytes = video.read()

    # Read metadata from JSON file
    with open(json_path, 'r') as file:
        metadata = json.load(file)

    camera_number = metadata['Camera Number']
    time_data = metadata['Time']
    location_data = metadata['Location']
    signature_base64 = metadata['Signature_Base64']
    signature = base64.b64decode(signature_base64)

    # Recreate combined data
    combined_data = create_combined(camera_number, video_bytes, time_data, location_data)

    public_key_base64 = get_public_key(int(camera_number))
    public_key = base64.b64decode(public_key_base64)

    # Verify signature
    valid = verify_signature(combined_data, signature, public_key)

    return valid


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
    

def create_combined(camera_number: str, media: bytes, time: str, location: str) -> bytes:
    '''Takes in camera number, image, time, location and encodes then combines to form one byte object'''

    encoded_number = camera_number.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_number + media + encoded_time + encoded_location

    return combined_data

def verify_signature(combined_data, signature, public_key):
    # Similar to your provided function
    # Deserialize the public key from PEM format
    
    public_key = serialization.load_pem_public_key(public_key)

    try:
        public_key.verify(
            signature,
            combined_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    
    except InvalidSignature:
        return False

# Usage

'''
image_path = f"52.png"
json_path = f"52.json"
valid = verify_image_and_metadata(image_path, json_path)
print(f"Verification result: {valid}")
'''


def verify_all_videos(directory_path):
    # List all files in the directory
    all_files = os.listdir(directory_path)
    # Filter out .png files
    avi_files = [file for file in all_files if file.endswith('.avi')]
    
    results = {}
    
    for video_name in avi_files:
        # Construct the corresponding JSON filename
        base_name = os.path.splitext(video_name)[0]
        json_name = f"{base_name}.json"
        
        # Construct full paths
        image_path = os.path.join(directory_path, video_name)
        json_path = os.path.join(directory_path, json_name)
        
        if os.path.exists(json_path):
            # Verify the image and its metadata
            valid = verify_image_and_metadata(image_path, json_path)
            results[video_name] = valid
        else:
            print(f"No JSON file found for {video_name}")
            results[video_name] = False
    
    return results

# Directory where your PNG and JSON files are stored
directory_path = "C:\\S3Backup"

# Verify all images in the directory
verification_results = verify_all_videos(directory_path)
for image, result in verification_results.items():
    print(f"Verification result for {image}: {result}")

print("-------------------------------------------------------------")
print(f"{len(verification_results)} videos checked with 0% verified")

'''
for i in range(50):
    image_path = f"{i}.png"
    json_path = f"{i}.json"

    valid = verify_image_and_metadata(image_path, json_path)
    print(f"Verification result: {valid}")
'''

