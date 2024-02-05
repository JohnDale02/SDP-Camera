import subprocess
import signal
import os

# Function to start recording
def start_recording(directory, filename="output2.mkv", duration=120):
    
    full_path = os.path.join(directory, filename)
    command = [
        "ffmpeg",
        "-f", "v4l2",
        "-framerate", "30",
        "-video_size", "640x480",
        "-i", "/dev/video0",  # Default camera device on Raspberry Pi
        "-t", str(duration),
        "-vcodec", "ffv1",  # Use 'copy' for testing or specify another codec
        full_path
    ]
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)  # Starts the recording process

# Function to stop recording
def stop_recording(process):
    process.terminate()  # Terminate the process more gently than SIGINT

# Example usage
if __name__ == "__main__":
    process = start_recording("./tmpImages")
    print("Recording started, will automatically stop after the duration.")
    # Wait for the process to complete
    stdout, stderr = process.communicate()
    if stderr:
        print(f"Error: {stderr.decode()}")
    else:
        print("Recording completed successfully.")


