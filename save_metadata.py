import os
import cv2
import numpy as np
import json

def save_metadata(metadata, save_metadata_filepath):

    with open(save_metadata_filepath, 'w') as file:
        json.dump(metadata, file)
