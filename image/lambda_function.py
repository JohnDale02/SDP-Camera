import mysql.connector
import json
import cv2
import hashlib
import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def handler(event, context):
    errors = ""

    try:
        # Parse the JSON string in the body
        body = json.loads(event['body'])

        # Access the 'image' key directly
        binary_image = base64.b64decode(body['image'])

    except Exception as e:
        errors = "Error decoding image from event: " + str(e)
    
    try:
        image = binary_image_to_numpy(binary_image)
    except Exception as e:
        errors = errors + "Error:" + f"Error converting binary image to numpy: {str(e)}"

    try:
        details = get_json_details(binary_image)

        if details  != False:
            camera_number = details[0]
            time_data = details[1]
            location_data = details[2]
            signature_string = details[3]
            signature = signature = base64.b64decode(signature_string)

    except Exception as e:
        errors = errors + "Error:" + f"Error getting JSON details: {str(e)}"

    try:
        combined_data = create_combined(camera_number, image, time_data, location_data)
    
    except Exception as e:
        errors = errors + "Error:" + f"Error combining data: {str(e)}"

    try:
        public_key_base64 = get_public_key(int(camera_number))
        public_key = base64.b64decode(public_key_base64)

    except Exception as e:
        errors = errors + "Error:" + f"Public key error: {str(e)}"

    try: 
        valid = verify_signature(combined_data, signature, public_key)

    except Exception as e:
        valid = False   # something went wrong verifying signature
        errors = errors + "Error:" + f"Error verifying or denying signature {str(e)}"

    try:
        if valid:
            # Return true with metadata
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    "result": "True",
                    "metadata": {
                        "camera_number": camera_number,
                        "time_data": time_data,
                        "location_data": location_data,
                        "signature": signature_string
                    }
                })
            }
        else:
            # Return false without metadata
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({"result": "False"})
            }

    except Exception as e:
        errors = "Unhandled exception: " + str(e)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": errors})
        }


def get_hash_for_query(binary_image):
    ''' Function for taking binary version of image and converting it to hash'''
    hash_object = hashlib.sha256()
    hash_object.update(binary_image)
    image_hash = hash_object.hexdigest()

    return image_hash

def binary_image_to_numpy(binary_image):
    ''' Function for taking binary version of image and converting it to numpy array'''
    # Assuming image_data contains the binary data of the image
    temp_file_path = "/tmp/my_temp_file.png"

    with open(temp_file_path, 'wb') as file:
        file.write(binary_image)

    image = cv2.imread(temp_file_path)
    os.remove(temp_file_path)

    return image


def get_json_details(binary_image):
    # Environment variables for database connection
    #host = os.environ['DB_HOST']
    #user = os.environ['DB_USER']
    #password = os.environ['DB_PASSWORD']
    #database = os.environ['DB_NAME']
    # Hash the image data to use as an index

    image_hash = get_hash_for_query(binary_image)

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

    if result:      # if the image_hash is found in the database
        data = json.loads(result[0])
        camera_number = data.get("Camera Number")
        time_data = data.get("Time")
        location_data = data.get("Location")
        signature = data.get("Signature_Base64")
        print([camera_number, time_data, location_data, signature])

        return [camera_number, time_data, location_data, signature]
    else:
        return False   # if the image_hash is not found in the database



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
    