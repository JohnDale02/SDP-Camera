import base64
import cv2


def recreate_data(image_base64, metadata, temp_image_path):
    '''Intakes cv2 image data and metadata; returns camera number, time, location, signature, creates image file'''

    
    image_bytes = base64.b64decode(image_base64)
    with open(temp_image_path, 'wb') as file:
        file.write(image_bytes)

    print("Metadata:", metadata)
    camera_number = metadata.get('cameranumber')
    time_data = metadata.get('time')
    location_data = metadata.get('location')
    
    signature_string = metadata.get('signature')
    signature = base64.b64decode(signature_string)

    return camera_number, time_data, location_data, signature


