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


def start_recording():
    global recording_process
    command = [
        'ffmpeg',
        '-f', 'v4l2', '-i', '/dev/video0',  # Directly use the real camera for recording
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '21',
        'output.mp4'
    ]
    recording_process = subprocess.Popen(command)

def stop_recording():
    global recording_process
    if recording_process:
        recording_process.terminate()  # sends SIGTERM
        recording_process.wait()  # Wait for the process to finish
        recording_process = None


def setup_gpio():
    GPIO.setmode(GPIO.BOARD)

    record_button = 37
    GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return record_button


def main_live_view():
    # Create a Tkinter window
    root = tk.Tk()
    # Create the GUI application
    gui = CameraGUI(root, video_source='/dev/video0')
    
    record_button = setup_gpio()
    recording_process = None

    try:
        while True:
            # Check for button press
            button_state = GPIO.input(record_button)
            if button_state == False and not recording_process:  # Assuming False means the button is pressed
                start_recording()
            elif button_state == True and recording_process:
                stop_recording()
            # Add a small delay to debounce button press
            time.sleep(0.1)
    except KeyboardInterrupt:
        # Handle cleanup on Ctrl+C (optional)
        stop_recording()
        gui.release()
        GPIO.cleanup()

    # Run the application
    gui.run()


if __name__ == '__main__':
    main_live_view()
