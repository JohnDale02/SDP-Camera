from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from recreate_hash import recreate_hash
import base64
import cv2

def verify_signiture(image, time_data, location_data, signature_encoded, public_key_decoded):

    hash = recreate_hash(image, time_data, location_data)

    public_key_path = 'recreated_public_key.pem'
    
    with open(public_key_path, "wb") as file:   # write our decoded public key data back to a pem file
            file.write(public_key_decoded)

    with open(public_key_path, "rb") as key_file:  # read the public key pem file
        public_key_data = key_file.read()
        public_key_object = serialization.load_pem_public_key(public_key_data)
        print("Serialization complete")

    # Verify the signature
    signature = base64.b64decode(signature_encoded)
    try:
        public_key_object.verify(
            signature,
            hash,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print('Signature is valid')
        return True
    
    except InvalidSignature:
        print('Signature verification failed')
        return False


image = cv2.imread('test.jpg')
time = "2023-10-29 14:30:00"
location = "Latitude: 40.7128, Longitude: -74.0060"
signature = "this"
public_key = "test2"
verify_signiture(image, time, location, signature, public_key)
