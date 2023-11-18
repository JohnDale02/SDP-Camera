import cv2
import hashlib

def hash_all(encoded_image, time, location):
    # Encode the image as a JPEG byte array
    encoded_image = encoded_image.tobytes()

    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_image + encoded_time + encoded_location

    hash = calculate_sha256_hash(combined_data)

    return hash


def calculate_sha256_hash(data):
    
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)

    return sha256_hash.digest()


#image = cv2.imread('test.jpg')
#time = "2023-10-29 14:30:00"
#location = "Latitude: 40.7128, Longitude: -74.0060"

