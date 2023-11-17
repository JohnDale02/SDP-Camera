import base64
import openssl
import subprocess
import opencv
import hashlib

def verify_signiture(temp_image_path, time_data, location_data, signature, public_key):

    # Decode the Base64 content back to binary
    public_key = base64.b64decode(public_key)

    # Write the binary content back to a PEM file
    public_key_file_path = 'recreated_public_key.pem'
    with open(public_key_file_path, 'wb') as file:
        file.write(public_key)

    

    hash = hash_all(temp_image_path, time_data, location_data)  # recreate hash we had on Raspi

    hash_file_path = 'hash.txt'
    with open(hash_file_path, 'wb') as file:
        file.write(hash)

    signature_file_path = 'recreated_signature.bin'
    with open(signature_file_path) as file:
        file.write(signature)

    result = subprocess.run(
        ['openssl', 'dgst', '-sha256', '-verify', 'recreated_public_key.pem',
         '-signature', 'recreated_signature.bin', 'hash.txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if 'Verified OK' in result.stdout.decode():
        print('Signature is valid') 
        return True
    else:
        print('Signature verification failed')
        return False


def hash_all(image, time, location):
    # Encode the image as a JPEG byte array
    _, encoded_image = cv2.imencode(".jpg", image)
    encoded_image = encoded_image.tobytes()

    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_image + encoded_time + encoded_location
    hash = calculate_sha256_hash(combined_data)

    return hash


def calculate_sha256_hash(data):
    
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)

    return sha256_hash.hexdigest()


image = cv2.imread('NewImage.jpg')
time = "2023-10-29 14:30:00"
location = "Latitude: 40.7128, Longitude: -74.0060"

print(hash_all(image, time, location))


