import cv2
import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import RPi.GPIO as GPIO
import threading
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

recording_process = None

def start_recording():
    global recording_process
    print("Starting recording...")
    command = [
        'ffmpeg',
        '-f', 'v4l2', '-i', '/dev/video0',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '21',
        'output.mp4'
    ]
    recording_process = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    print("Recording process started.")

def stop_recording():
    global recording_process
    if recording_process:
        print("Stopping recording...")
        recording_process.terminate()
        stdout, _ = recording_process.communicate()
        print("FFmpeg output:", stdout.decode())
        recording_process = None
        print("Recording stopped.")

def monitor_button(record_button):
    global recording_process
    print("Monitoring button...")
    while True:
        button_state = GPIO.input(record_button)
        if button_state == False and not recording_process:
            print("Button pressed.")
            start_recording()
        elif button_state == True and recording_process:
            print("Button released.")
            stop_recording()
        time.sleep(0.1)


def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    record_button = 37  # Use the physical pin numbering
    GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return record_button

def main_live_view():
    record_button = setup_gpio()

    # Create a Tkinter window
    root = tk.Tk()
    
    # Create the GUI application
    gui = CameraGUI(root, video_source='/dev/video0')

    # Setup thread for monitoring button press in the background
    threading.Thread(target=monitor_button, args=(record_button,), daemon=True).start()

    # Run the application
    gui.run()

    # Release resources after the window is closed
    gui.release()
    GPIO.cleanup()

if __name__ == '__main__':
    main_live_view()
