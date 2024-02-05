import os
import cv2
import numpy as np
import json

def save_video(encoded_video, metadata, save_image_filepath, object_count):
    
    video_filepath = os.path.join(save_image_filepath, f'{object_count}.avi')
    metadata_filepath = os.path.join(save_image_filepath, f"{object_count}.json")

    with open(metadata_filepath, 'w') as file:
        json.dump(metadata, file)

def count_vid_files(directory_path):
    '''Helper function for returning number of PNG files in the directory'''

    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return 0

    count = 0
    # Iterate over all files in the directory
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.avi') or file_name.lower().endswith('.png'):
            count += 1

    return count