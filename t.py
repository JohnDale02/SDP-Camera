import subprocess
import signal
import os

# Function to start recording
def start_recording(filename="output2.mkv", duration=60, video_device_index="0", audio_device_index=":0"):
    command = [
    "ffmpeg",
    "-f", "avfoundation",
    "-framerate", "30",
    "-video_size", "640x480",
    "-i", f"{video_device_index}{audio_device_index}",
    "-t", str(duration),
    "-vcodec", "ffv1",  # FFV1 codec for lossless video recording
    filename
]
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)  # Starts the recording process

# Function to stop recording
def stop_recording(process):
    process.terminate()  # Terminate the process more gently than SIGINT

# Example usage
if __name__ == "__main__":
    process = start_recording()
    print("Recording started, will automatically stop after the duration.")
    # Wait for the process to complete
    stdout, stderr = process.communicate()
    if stderr:
        print(f"Error: {stderr.decode()}")
    else:
        print("Recording completed successfully.")
