import os
import cv2
import json
from upload_image import upload_image
from upload_video import upload_video

def upload_saved_media(upload_lock):
    '''thread function for uploading saved media in the background when Wifi is available and media is stored locally.'''
    global wifi_status

    while True:
        if wifi_status == True:
            with upload_lock:
                        
                if os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
                        save_image_filepath = os.path.join(os.getcwd(), "tmpImages")
                else:
                    print("There is no tmpImages directory")         
                if os.path.exists(os.path.join(os.getcwd(), "tmpVideos")): # make a directory for tmpImages if it doesnt exist
                        save_video_filepath = os.path.join(os.getcwd(), "tmpVideos")
                else:
                    print("There is no tmpVideos directory")

                for file_name in os.listdir(save_image_filepath):
                    if file_name.lower().endswith('.png'):
                        file_path = os.path.join(save_image_filepath, file_name) # get the full path
                        image = cv2.imread(file_path)   # read the image
                        _, encoded_image = cv2.imencode(".png", image)  # encode the image
                        
                        file_path_metadata = os.path.join(save_image_filepath, file_name[:-3]+'json') # get matching json file
                        metadata = read_metadata(file_path_metadata)

                        try:
                            upload_image(encoded_image.tobytes(), metadata)   # cv2 png object, metadat
                            print(f"------------------------------------------------------")
                            print(f"Uploaded Saved Image")
                            os.remove(file_path)
                            print(file_path_metadata)
                            os.remove(file_path_metadata)
                        except Exception as e:
                            print(f"Error uploading saved image: {str(e)}")

                for file_name in os.listdir(save_video_filepath):
                    if file_name.lower().endswith('.avi'):
                        file_path = os.path.join(save_video_filepath, file_name) # get the full path
                        with open(file_path, 'rb') as video:
                            video_bytes = video.read()
                        
                        file_path_metadata = os.path.join(save_video_filepath, file_name[:-3]+'json') # get matching json file
                        metadata = read_metadata(file_path_metadata)

                        try:
                            upload_video(video_bytes, metadata)   # cv2 png object, metadat
                            print(f"------------------------------------------------------")
                            print(f"Uploaded Saved Image")
                            os.remove(file_path)
                            print(file_path_metadata)
                            os.remove(file_path_metadata)
                        except Exception as e:
                            print(f"Error uploading saved image: {str(e)}")

        
def read_metadata(file_path_metadata):
    with open(file_path_metadata, 'r') as file:
        metadata = json.load(file)
        return metadata