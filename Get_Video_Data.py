import subprocess

def read_video_as_bytes(video_path):
    command = ['ffmpeg', '-i', video_path, '-f', 'rawvideo', '-']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        return stdout  # This is the raw video data as bytes
    else:
        print(f"Error reading video: {stderr}")
        return None

video_bytes = read_video_as_bytes('path/to/your/video.mp4')
if video_bytes:
    # Process the video bytes, e.g., hash them
    print(f"Read {len(video_bytes)} bytes from the video.")
