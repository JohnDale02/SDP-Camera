import subprocess
import random 
# Define the command and arguments
number = random.randint(1,100)
output_video = f"output_{number}video.avi"

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
    output_video
]

# Execute the command
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for the process to complete
stdout, stderr = process.communicate()

# Check for errors
if process.returncode != 0:
    print(f"Error occurred: {stderr}")
else:
    print("Recording finished successfully.")
