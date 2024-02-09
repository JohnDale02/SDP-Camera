import cv2
import subprocess
import base64
import os 
import time

def create_video(save_video_filepath):
    '''Captures Video file; returns data as a byetes'''

    object_count = count_files(save_video_filepath)
    video_filepath = os.path.join(save_video_filepath, f'{object_count}.avi')
    video_bytes = capture_video(video_filepath)

    if video_bytes is not None:
        print("\Video not None, Loading...")

        return video_bytes, object_count
    
    else:
        print("Video is None")
        return None


def capture_video(video_filename):
    ''' Initialized camera and takes picture'''

    # Define the command and arguments
    command = [
        'ffmpeg',
        '-framerate', '24',
        '-video_size', '1280x720',
        '-i', '/dev/video0',
        '-f', 'alsa', '-i', 'default',
        '-c:v', 'h264_v4l2m2m',
        '-pix_fmt', 'yuv420p',
        '-b:v', '4M',
        '-bufsize', '4M',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-threads', '4',
        video_filename
    ]
    
    print("Starting to record!!!")
    # Execute the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    print(f"Video output: stdout {stdout}, stderr: {stderr}")

    print("reading and returning avi bytes")
    video_bytes = None
    with open(video_filename, 'rb') as video:
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
        if file_name.lower().endswith('.avi'):
            count += 1

    return count