from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64
import cv2

def verify_signiture(image, time_data, location_data, signature, public_key):

    print(public_key)
    image_data = cv2.imread(image)
    combined_data = data_before_hash(image_data, time_data, location_data)  # recreate hash we had on Raspi

    binary_public_key = base64.b64decode(public_key)
    public_key_path = 'public_key.pem'

    # Create the public_key.PEM file on the cloud
    with open(public_key_path, 'wb') as file:
        file.write(binary_public_key)

    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(key_file.read())

    # Compute hash of the data
    digest = hashes.Hash(hashes.SHA256())
    digest.update(combined_data)
    data_hash = digest.finalize()

    print(f"Hashed : {data_hash}")

    # Verify the signature
    try:
        public_key.verify(
            base64.b64decode(signature),
            data_hash,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print('Signature is valid')
        return True
    
    except InvalidSignature:
        print('Signature verification failed')
        return False


def data_before_hash(image, time, location):
    # Encode the image as a JPEG byte array
    _, encoded_image = cv2.imencode(".jpg", image)
    encoded_image = encoded_image.tobytes()

    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_image + encoded_time + encoded_location


    return combined_data