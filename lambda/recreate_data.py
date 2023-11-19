import base64
import cv2


def recreate_data(image_base64, metadata, temp_image_path):
    '''Intakes cv2 image data and metadata; returns camera number, time, location, signature, creates image file'''

    
    image = base64.b64decode(image_base64)

    print("Metadata:", metadata)
    camera_number = metadata.get('cameranumber')
    time_data = metadata.get('time')
    location_data = metadata.get('location')
    
    signature_base64 = metadata.get('signature')
    signature = base64.b64decode(signature_base64)

    print(f"recreate jpg: {type(image)}")
    
    cv2.imwrite(temp_image_path, image)

    return camera_number, time_data, location_data, signature


