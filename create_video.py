import cv2
import subprocess
import base64
import os 
import time

def create_video(save_video_filepath):
    '''Captures Video file; returns data as a byetes'''

    object_count = count_files(save_video_filepath)
    video_filepath = os.path.join(save_video_filepath, f'{object_count}.avi')
    video_filepath_webm = os.path.join(save_video_filepath, f'{object_count}.webm')
    video_bytes = capture_video(video_filepath, video_filepath_webm)

    if video_bytes is not None:
        print("\Video not None, Loading...")

        return video_bytes, object_count
    
    else:
        print("Video is None")
        return None


def capture_video(video_filename, video_filename_webm):
    ''' Initialized camera and takes picture'''

    # Define the command and arguments
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-video_size', '1920x1080',
        '-i', '/dev/video0',
        '-c:v', 'h264_v4l2m2m',
        '-pix_fmt', 'yuv420p',
        '-b:v', '2M',
        '-bufsize', '2M',
        '-t', '10',
        video_filename
    ]

    command_convert_to_webm = [
        'ffmpeg',
        '-i', video_filename, 
        '-c:v', 'libvpx-vp9', 
        '-lossless', '1',
        '-c:a', 'libopus', 
        video_filename_webm
        
    ]
    
    print("Starting to record!!!")
    # Execute the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(f"Recording video Stdout and stderr: {stderr}")
    print("Starting conversion...")
    process_conversion = subprocess.Popen(command_convert_to_webm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    # Wait for the process to complete
    stdout, stderr = process_conversion.communicate()
    print(f"Converting video to WEBM Stdout and stderr: {stderr}")

    print("Removing AVI FILE")
    os.remove(video_filename)    # delete the AVI file from the folder

    print("reading and returning webm bytes")
    video_bytes = None
    with open(video_filename_webm, 'rb') as video:
        video_bytes = video.read()

    if video_bytes == None: 
        return None
    
    else:
        return video_bytes



def count_files(directory_path):
    '''Helper function for returning number of PNG files in the directory'''

    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return 0

    count = 0
    # Iterate over all files in the directory
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.webm'):
            count += 1

    return count