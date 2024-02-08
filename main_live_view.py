import cv2
import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import RPi.GPIO as GPIO
import time


class CameraGUI:
    def __init__(self, window, video_source=0):
        self.window = window
        self.window.title("Live View")
        self.video_source = video_source
        
        self.capture = cv2.VideoCapture(self.video_source)
        self.image_label = tk.Label(self.window)
        self.image_label.pack()
        
        self.create_virtual_camera()
        self.update_frame()

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=im)
            self.image_label.config(image=img)
            self.image_label.image = img
        
        self.window.after(10, self.update_frame)

    def run(self):
        self.window.mainloop()

    def release(self):
        if self.capture.isOpened():
            self.capture.release()

    def create_virtual_camera():
        # Create a virtual camera device using v4l2loopback
        create_virtual_camera_command = [
        'sudo', 'modprobe', 
        'v4l2loopback', 
        'video_nr=1', 
        'card_label="VirtualCam"']
        
        create_virtual_camera_process = subprocess.Popen(create_virtual_camera_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = create_virtual_camera_process.communicate()

        print(f"Video output: stdout {stdout}, stderr: {stderr}")



def main_live_view():

    # Create a Tkinter window
    root = tk.Tk()
    # Create the GUI application and virtual camera device
    gui = CameraGUI(root, video_source='/dev/video1')

    # Run the application
    gui.run()

    # Release resources after the window is closed
    gui.release()

if __name__ == '__main__':
    main_live_view()


# Start the live view feed to the virtual camera
live_view_process = subprocess.Popen([
    'ffmpeg',
    '-f', 'v4l2', '-i', '/dev/video0',  # Real camera device
    '-f', 'v4l2', '/dev/video1',        # Virtual camera device
    '-vf', 'scale=640:-1',              # Scale down the resolution for the live view
])


# Setup your GPIO according to your needs
GPIO.setmode(GPIO.BCM)
record_button = 23  # Replace with your GPIO pin
GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variable to keep track of recording status
is_recording = False
recording_process = None



def start_recording():
    global is_recording, recording_process
    if not is_recording:
        command = [
            'ffmpeg',
            '-f', 'v4l2', '-i', '/dev/video1',  # Use the virtual camera device for recording
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '21',
            'output.mp4'
        ]
        recording_process = subprocess.Popen(command)
        is_recording = True

def stop_recording():
    global is_recording, recording_process
    if is_recording:
        recording_process.terminate()  # sends SIGTERM, or use .kill() to send SIGKILL
        recording_process.wait()  # Wait for the process to finish
        recording_process = None
        is_recording = False

# Main loop
try:
    while True:
        # Check for button press
        button_state = GPIO.input(record_button)
        if button_state == False and not is_recording:  # Assuming False means the button is pressed
            start_recording()
        elif button_state == True and is_recording:
            stop_recording()
        # Add a small delay to debounce button press
        time.sleep(0.1)
except KeyboardInterrupt:
    # Handle cleanup on Ctrl+C (optional)
    stop_recording()
    if live_view_process:
        live_view_process.terminate()
        live_view_process.wait()
    GPIO.cleanup()
