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

def verify_image_and_metadata(image_path, json_path):

    # Read the image
    image = cv2.imread(image_path)

    # Read metadata from JSON file
    with open(json_path, 'r') as file:
        metadata = json.load(file)

    camera_number = metadata['Camera Number']
    time_data = metadata['Time']
    location_data = metadata['Location']
    signature_base64 = metadata['Signature_Base64']
    signature = base64.b64decode(signature_base64)

    # Recreate combined data
    combined_data = create_combined(camera_number, image, time_data, location_data)

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
    

def create_combined(camera_number: str, image: bytes, time: str, location: str) -> bytes:
    # Similar to your provided function
    _, encoded_image = cv2.imencode(".png", image)
    encoded_image = encoded_image.tobytes()

    encoded_number = camera_number.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_number + encoded_image + encoded_time + encoded_location

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


image_path = f"210.png"
json_path = f"210.json"
valid = verify_image_and_metadata(image_path, json_path)
print(f"Verification result: {valid}")


'''
for i in range(50):
    image_path = f"{i}.png"
    json_path = f"{i}.json"

    valid = verify_image_and_metadata(image_path, json_path)
    print(f"Verification result: {valid}")
'''

