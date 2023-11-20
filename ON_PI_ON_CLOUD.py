import base64
import cv2




with open('public_key.pem', 'rb') as file:
    signature_base64 = file.read()
    print(signature_base64)

signature_string = base64.b64encode(signature_base64).decode('utf-8')

# Convert the Base64 string back to bytes
signature_bytes = base64.b64decode(signature_string)
print(signature_bytes)