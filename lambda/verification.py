from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from recreate_combined import recreate_combined_data
import base64
import cv2

def verify_signiture(temp_image_path, time_data, location_data, signature_encoded, public_key_encoded):

    image = cv2.imread(temp_image_path)
    print(f"REading image type for recreating hash: {type(image)}")

    combined_data = recreate_combined_data(image, time_data, location_data)

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
            signature_decoded,
            combined_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print('Signature is valid')
        return True
    
    except InvalidSignature:
        print('Signature verification failed')
        return False


image = 'image.jpg'
time = "2023-10-29 14:30:00"
location = "Latitude: 40.7128, Longitude: -74.0060"
signature = "ABQACwEArlnwtarbuDmWu8ski7sYnAFQ7QxvKL1cksQPauRwquG13gYqTzLdSBZvayU8g/gZX2FMZOEqjBzVstdqsfo2mTbMP0z3jCxeEsjauTl64AgSG++H7hY/csTk78W3zsdJqoCE/MYHr0ctpDPls/ZmOLf9nmwSxlKxSCKWh6ASofmUUc5ilEKG/TsMWCnC2X4FFLZp3ZWjgu5f8PdgRNffQTiL/0WdoWZh4GtBfrgsF7Ak6o25bm5rzMGA+xpuh3qBoHAjK1PTlR6ArqdlFOMoCMAcRmkYVw8g0ZV357RM/OYtCRQVLsm3oT60eqm1JC90d2cTmGRouyj/iOqcu0LC+Q=="
public_key = "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF2YUhIbzR6eXNrT0FaVDJjZEViSApuSDZLMC9XbjIvNTVVNVVWQ3I5TkpBWnFINkQ4Q3dVa2dIeUVjeUhFcHNOc0cyUHovV2ZwNHR3Qlh2WSs1NG1QClhkVENHK2VveW5ZNlVhL2lSTURHb2ljc2M4YWNUY2FzUC9sQ1ova1dBc3lsKzRad3hwaXo3OXBaZXFuZXJ2ejMKVDgwUVFLRkxFOFJpM3Jic2UxUi9BZFVzS0FRa1JGY3IvWVNGamRKWlZLYml4Qnc5WGdzNUxERmZPNE42ajZ3WApWTzF2UnQvNldFa0R5ckJDVkZ0WGdVQXJJVzFONytIV2wwamY1OWR1LzkzWmJWSzBsMzNZOUhSUnVHT0RvbnVCCjBVWnAzeGZPT08xYkJsN2Z5cS9HenQxRlYreklFSXVrQml2Tm95Ry9jZEdoWVBMR0QyeHJzTmFkY1VPZ1A1eEMKZndJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
verify_signiture(image, time, location, signature, public_key)
