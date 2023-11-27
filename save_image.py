import os
import cv2
import numpy as np

def save_image(encoded_image_bytes, metadata, save_image_filepath):

    object_count = count_files(save_image_filepath)
    image_filepath = os.path.join(save_image_filepath, f'{object_count}.png')
    metadata_filepath = os.path.join(save_image_filepath, f"{object_count}.txt")

    encoded_image_np = np.frombuffer(encoded_image_bytes, dtype=np.uint8)  # Convert the bytes back into a numpy array
    decoded_image = cv2.imdecode(encoded_image_np, cv2.IMREAD_UNCHANGED)   # Decode the image from the numpy array

    # Save the image as a PNG file
    cv2.imwrite(image_filepath, decoded_image)

    with open(metadata_filepath, 'w') as file:
        file.write(metadata)

def count_files(directory_path):
    '''Helper function for returning number of PNG files in the directory'''

    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return 0

    count = 0
    # Iterate over all files in the directory
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.png'):
            count += 1

    return count