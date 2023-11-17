import base64
from OpenSSL import crypto
import subprocess
import cv2
import hashlib

def verify_signiture(temp_image_path, time_data, location_data, signature, public_key):

    # Decode the Base64 content back to binary
    public_key = base64.b64decode(public_key)

    # Write the binary content back to a PEM file
    public_key_file_path = 'recreated_public_key.pem'
    with open(public_key_file_path, 'wb') as file:
        file.write(public_key)

    image = cv2.imread(temp_image_path)

    combined_data = data_before_hash(image, time_data, location_data)  # recreate hash we had on Raspi

    # Load the public key
    with open(public_key_file_path, "rb") as key_file:
        public_key = crypto.load_publickey(crypto.FILETYPE_PEM, key_file.read())

    # Create a verification context and verify the signature
    try:
        # The verify function expects the data itself, not the hash
        # Here we assume you have the original data that was hashed
        # If you only have the hash, you need to adjust the approach
        crypto.verify(public_key, signature, combined_data, 'sha256')
        print('Signature is valid')
        return True
    except crypto.Error as e:
        print('Signature verification failed:', e)
        return False



def data_before_hash(image, time, location):
    # Encode the image as a JPEG byte array
    _, encoded_image = cv2.imencode(".jpg", image)
    encoded_image = encoded_image.tobytes()

    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_image + encoded_time + encoded_location


    return combined_data


image = cv2.imread('NewImage.jpg')
time = "2023-10-29 14:30:00"
location = "Latitude: 40.7128, Longitude: -74.0060"

#print(data_before_hash(image, time, location))


