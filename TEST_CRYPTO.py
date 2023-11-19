
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

    #combined_data = combine(image, time, location)
    #signature = sign_hash(combined_data)

    public_key_file_path = 'public_key.pem'

    with open(public_key_file_path, "rb") as key_file:
        public_key_data = key_file.read()

    # Deserialize the public key from PEM format
    public_key = serialization.load_pem_public_key(public_key_data)

    with open('signature.file', 'rb') as signature_file:
        signature = signature_file.read()

    with open('combined.file', 'rb') as combined_file:
        combined_data = combined_file.read()

    try:
        # For PKCS1v15 padding:
        public_key.verify(
            signature,
            combined_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print('Signature is valid with PKCS1v15 padding')

        # For PSS padding:
        public_key.verify(
            signature,
            combined_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print('Signature is valid with PSS padding')

        return True
    
    except Exception as e:
        print(f'Signature verification failed {e}')
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
