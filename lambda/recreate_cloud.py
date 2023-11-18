import base64
import cv2


def recreate_image_and_metadata(image_content, metadata, temp_image_path):
    '''Intakes cv2 image data and metadata; returns camera number, time, location, signature, creates image file'''

    print("Metadata:", metadata)
    camera_number = metadata.get('cameranumber')
    time_data = metadata.get('time')
    location_data = metadata.get('location')
    signature = metadata.get('signature')

    image = base64.b64decode(image_content)
    cv2.imwrite(temp_image_path, image)

    return camera_number, time_data, location_data, signature


