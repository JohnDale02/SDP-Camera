
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
import base64
import cv2
import subprocess
import tempfile
import os

def sign_verify(image_name):

    image = cv2.imread(image_name)
    time = "2023-10-29 14:30:00"
    location = "Latitude: 40.7128, Longitude: -74.0060"

    combined_data = combine(image, time, location)
    signature = sign_hash(combined_data)

    digest_data_filepath = 'digest.file'
    with open(digest_data_filepath, 'r') as digest_file:
        digest_data = digest_file.read()    # POSSIBLY TEST IF DIGEST WORKS??



    public_key_path = 'public_key.pem'


    with open(public_key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

    try:
        public_key.verify(
            signature,
            combined_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print('Signature is valid')
        return True
    
    except InvalidSignature:
        print('Signature verification failed')
        return False
    

def sign_hash(combined_string):
    '''Takes in a hash; returns base64 encoded signature'''

    signature_file_path = 'signature.file'
    combined_file_path = 'combined.file'

    # Write hash string to a temporary file
    with open(combined_file_path, "wb") as combined_file:  # create a temporary hash file where we put our hash for signing
        combined_file.write(combined_string)

    # Use the temporary files in the tpm2_sign command
    tpm2_sign_command = [
        "tpm2_sign",
        "-c", "0x81010001",
        "-g", "sha256",
        "-s", "rsassa",
        "-o", signature_file_path,
        combined_file_path
    ]

    # Execute the command
    result = subprocess.run(tpm2_sign_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Read and delete the temporary signature file

    if os.path.exists(signature_file_path):
        with open(signature_file_path, 'rb') as file:
            signature = file.read()

    if result.returncode == 0 and signature:
        # Binary signature
        
        print("Signature:", signature)
        #\signature_base64 = base64.b64encode(signature).decode('utf-8')
        #print("Signature64:", signature_base64)
        print(f"SIgnature here: check signature.file for comparison: {signature}")

        return signature
        #return signature_base64
    else:
        raise Exception("Error in generating signature: " + result.stderr.decode())

def combine(image, time, location):
    # Encode the image as a JPEG byte array
    _, encoded_image = cv2.imencode(".jpg", image)
    encoded_image = encoded_image.tobytes()

    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_image + encoded_time + encoded_location

    return combined_data



print(sign_verify("test.jpg"))
