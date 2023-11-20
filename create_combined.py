import cv2
import hashlib

def create_combined(camera_number: str, image: bytes, time: str, location: str) -> bytes:
    '''Takes in camera number, image, time, location and encodes then combines to form one byte object'''

    # Encode the image as a JPEG byte array
    _, encoded_image = cv2.imencode(".png", image)
    encoded_image = encoded_image.tobytes()

    encoded_number = camera_number.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_number + encoded_image + encoded_time + encoded_location

    return combined_data
