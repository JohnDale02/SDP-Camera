import cv2

def create_combined(fingerprint: str, camera_number: str, media: bytes, time: str, location: str) -> bytes:
    '''Takes in camera number, image, time, location and encodes then combines to form one byte object'''

    encoded_fingerprint = fingerprint.encode('utf-8')
    encoded_number = camera_number.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_fingerprint + encoded_number + media + encoded_time + encoded_location

    return combined_data
