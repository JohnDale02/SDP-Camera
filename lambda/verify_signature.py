from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
import base64
import cv2

def verify_signature(temp_image_path, camera_number, time_data, location_data, signature, public_key):

    image = cv2.imread(temp_image_path)

    combined_data = create_combined(camera_number, image, time_data, location_data)

    print(type(combined_data), "SHould be bytes")

    public_key_path = 'public_key.pem'

    with open(public_key_path, "wb") as file:   # write our decoded public key data back to a pem file
            file.write(public_key)

    with open(public_key_path, "rb") as key_file:
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
        print('Signature is valid')
        return True
    
    except InvalidSignature:
        print('Signature verification failed')
        return False


def create_combined(camera_number: str, image: bytes, time: str, location: str) -> bytes:
    '''Takes in camera number, image, time, location and encodes then combines to form one byte object'''

    # Encode the image as a JPEG byte array
    _, encoded_image = cv2.imencode(".jpg", image)
    encoded_image = encoded_image.tobytes()

    encoded_number = camera_number.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_number + encoded_image + encoded_time + encoded_location

    return combined_data


#image = 'image.jpg'
#time = "2023-10-29 14:30:00"
#location = "Latitude: 40.7128, Longitude: -74.0060"
#signature = "ABQACwEAYscrvy8zKUII/Kjvnk/2CKF+FuJrDzMS2THDJV9uVrgCGOiO8AE/3m5WDkf/JPO+IW+0yq4V5ZRrOU3SSa0EmEqVIHFe8gf/4g92mbH04C0+t7oUX+pGGSP6Nap0/litwBLCytu8Vt+VwsjbBHBLu93sidqn6NcVFo0st31LJVF6gfuEpGsftO1auhH62dLEOImtAN9QDwPLXhZZ3Mux8Vt605s3srCr5nstppYMbpwxrA9PqLb/Z7LuBDNjrxyOhMmtXCAz44IgavAWzeb9UCgLDjxvRAAv6sTeUCIvH9uAI7tAhR9X3S7GAvs4czdPJtMPc8Rg/UB1Gckw/j/a7w=="
#public_key = "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF2YUhIbzR6eXNrT0FaVDJjZEViSApuSDZLMC9XbjIvNTVVNVVWQ3I5TkpBWnFINkQ4Q3dVa2dIeUVjeUhFcHNOc0cyUHovV2ZwNHR3Qlh2WSs1NG1QClhkVENHK2VveW5ZNlVhL2lSTURHb2ljc2M4YWNUY2FzUC9sQ1ova1dBc3lsKzRad3hwaXo3OXBaZXFuZXJ2ejMKVDgwUVFLRkxFOFJpM3Jic2UxUi9BZFVzS0FRa1JGY3IvWVNGamRKWlZLYml4Qnc5WGdzNUxERmZPNE42ajZ3WApWTzF2UnQvNldFa0R5ckJDVkZ0WGdVQXJJVzFONytIV2wwamY1OWR1LzkzWmJWSzBsMzNZOUhSUnVHT0RvbnVCCjBVWnAzeGZPT08xYkJsN2Z5cS9HenQxRlYreklFSXVrQml2Tm95Ry9jZEdoWVBMR0QyeHJzTmFkY1VPZ1A1eEMKZndJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
#verify_signiture(image, time, location, signature, public_key)