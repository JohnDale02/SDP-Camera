import os
import cv2
import numpy as np
import json

def save_metadata(object_count, metadata, save_video_filepath):

    metadata_filepath = os.path.join(save_video_filepath, f"{object_count}.json")

    with open(metadata_filepath, 'w') as file:
        json.dump(metadata, file)
