from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from recreate_hash import recreate_hash
import base64
import cv2

def verify_signiture(image, time_data, location_data, signature_encoded, public_key_encoded):

    hash = recreate_hash(image, time_data, location_data)

    public_key_path = 'recreated_public_key.pem'
    public_key_decoded = base64.b64decode(public_key_encoded)
    signature_decoded = base64.b64decode(signature_encoded)

    with open(public_key_path, "wb") as file:   # write our decoded public key data back to a pem file
            file.write(public_key_decoded)

    with open(public_key_path, "rb") as key_file:  # read the public key pem file
        public_key_data = key_file.read()
        public_key_object = serialization.load_pem_public_key(public_key_data)
        print("Serialization complete")

    # Verify the signature

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
signature = "ABQACwEAiejNwAsTQdN6c8ea3+WerA3Ib3sX2Ubm7+9uAiZAJ7KNhu0Gyd++Cj8y9fzbmuSYZo/CPgSl2YM1PCSMInQJqfjbxDGtEgsIdvTevqfxCBGxH6V0g5Gi91VnlTv0EAQDS4pp5DKZ34+j8EF/qp3ppHDFKkN6Yc08gA0zW6CrZgJ/u51pFdeblpE7Z69BeWL9vGo+0mnNaMKzzcnu6dIKKJiz/8mFd72QfvOVwMtyrUFrKa47Lc1UAp1jjEG+f4/3/4+m5Y1FLc0zND/3q7w8a3sbgeU/RG7ptu2+nc/bzDJqEdJbgOwSiYZXKNZBuF+Dn4CfEoYZZ07dtJ0IGdfkEA=="
public_key = "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF2YUhIbzR6eXNrT0FaVDJjZEViSApuSDZLMC9XbjIvNTVVNVVWQ3I5TkpBWnFINkQ4Q3dVa2dIeUVjeUhFcHNOc0cyUHovV2ZwNHR3Qlh2WSs1NG1QClhkVENHK2VveW5ZNlVhL2lSTURHb2ljc2M4YWNUY2FzUC9sQ1ova1dBc3lsKzRad3hwaXo3OXBaZXFuZXJ2ejMKVDgwUVFLRkxFOFJpM3Jic2UxUi9BZFVzS0FRa1JGY3IvWVNGamRKWlZLYml4Qnc5WGdzNUxERmZPNE42ajZ3WApWTzF2UnQvNldFa0R5ckJDVkZ0WGdVQXJJVzFONytIV2wwamY1OWR1LzkzWmJWSzBsMzNZOUhSUnVHT0RvbnVCCjBVWnAzeGZPT08xYkJsN2Z5cS9HenQxRlYreklFSXVrQml2Tm95Ry9jZEdoWVBMR0QyeHJzTmFkY1VPZ1A1eEMKZndJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
verify_signiture(image, time, location, signature, public_key)
