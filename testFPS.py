import time
import cv2
import os
# Import your existing functions and modules here
from create_image import create_image
from check_wifi import is_internet_available
from create_metadata import create_metadata
from create_combined import create_combined
from upload_image import upload_image
from create_digest import create_digest
from create_signature import create_signature
from GPS_uart import parse_nmea_sentence, read_gps_data
from upload_saved_images import upload_saved_images
from save_image import save_image

def main(camera_number_string, save_image_filepath):
    frame_count = 0
    start_time = time.time()
    
    while True:
        # Your existing code to capture, hash, sign, and upload images goes here
        image = create_image()  # take the image
        _, encoded_image = cv2.imencode('.png', image)
        
        lat_value, long_value, time_value =  read_gps_data()
        location = f"{lat_value}, {long_value}"
        time = f"{time_value}"
        
        combined_data = create_combined(camera_number_string, image, time, location)
        
        try:
            digest = create_digest(combined_data)
        except Exception as e:
            print(str(e))

        try:
            signature_string = create_signature(digest)
        except Exception as e:
            print(str(e))

        metadata = create_metadata(camera_number_string, time, location, signature_string)
        
        if is_internet_available():
            print(f"Internet is available...Uploading")
            upload_image(encoded_image.tobytes(), metadata)
            print(f"Uploaded Image")
        else:
            save_image(encoded_image.tobytes(), metadata, save_image_filepath)
            print("No wifi")
        
        frame_count += 1
        
        if time.time() - start_time >= 10:
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time
            print(f"Frames per second after 10 seconds: {fps:.2f}")
            break


camera_number_string = "1"  # camera number used to search for public key

if not os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
    os.makedirs(os.path.join(os.getcwd(), "tmpImages"))

save_image_filepath = os.path.join(os.getcwd(), "tmpImages")

main(camera_number_string, save_image_filepath)