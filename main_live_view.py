import threading 
import RPi.GPIO as GPIO
import time
import subprocess
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

image_mode = True
is_recording = False
ffmpeg_process = None
have_started = False

capture = cv2.VideoCapture(0)  # capture object for liveView
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Adjust width
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Adjust height



# --------------------------------------------------------------------

def photoLock():

    '''Main Function that performs all PhotoLock software: "The Main" '''
    setup_gpio()
    handleCaptureThread = threading.Thread(target=handle_capture, daemon=True)
    handleCaptureThread.start()
    print("Handle Capture thread started")

    gui_thread()



def gui_thread():
    ''' Thread responsible for reflecting state changes to the GUI'''
    global root, text_box, video_label

    root = tk.Tk()
    root.geometry("800x480")

    video_canvas = tk.Canvas(root, width=1280, height=720)
    video_canvas.pack()  # Adjust the placement as needed
    
    # Create a text box widget
    text_box = ttk.Label(root, text="", background="white", font=("Helvetica", 16))
    

    # Create a label for displaying the video
    video_label = video_canvas

    print("Initialized everythign in the GUI; updating frame and text dynamically")
    # Initialize the GUI update loop
    update_gui()
    update_frame()


    root.mainloop()
# --------------------------------------------------------------------
        
def toggle_image_mode(channel):
    global image_mode
    image_mode = not image_mode
    print("Image mode toggled:", image_mode)\

def toggle_recording(channel):
    global image_mode
    global is_recording
    global ffmpeg_process
    global have_started

    is_recording = not is_recording
    print("Recording toggled:", is_recording)

    if image_mode == False and is_recording == True and have_started == False:
        ffmpeg_process = start_recording()
        have_started = True

    elif image_mode == False and is_recording == False and have_started == True:
        ffmpeg_process = stop_recording(ffmpeg_process)
        have_started = False

# --------------------------------------------------------------------

def update_gui():
    global image_mode, is_recording

    # Current state of the text box (to minimize unnecessary updates)
    current_text = text_box.cget("text")  # Get the current text of the text box
    desired_text = "Image" if image_mode else "Video"

    # Only update the text box if the text has changed
    if current_text != desired_text:
        text_box.config(text=desired_text)
        # Since both conditions place the text box in the same location, we don't need to check this every time
        text_box.place(relx=1.0, rely=0.0, anchor="ne")

    # Schedule the update_gui function to run again after 100ms
    root.after(100, update_gui)

def update_frame():
    global capture, video_label
    ret, frame = capture.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=im)
        video_label.img = img  # Keep a reference to avoid garbage collection
        video_label.create_image(0, 0, anchor="nw", image=img)
        if is_recording:
            video_label.create_oval(5, 5, 45, 45, fill="red")
        else:
            video_label.delete("recording_indicator")
            
    # Update the frame in the GUI less frequently
    root.after(3, update_frame)  # Adjust the delay as needed

# --------------------------------------------------------------------

def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    record_button = 37
    mode_button = 38
    GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mode_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup event detection
    GPIO.add_event_detect(mode_button, GPIO.FALLING, callback=toggle_image_mode, bouncetime=200)
    GPIO.add_event_detect(record_button, GPIO.FALLING, callback=toggle_recording, bouncetime=200)
    
# --------------------------------------------------------------------

def handle_capture():
    '''Function for monitoring modes and recording states and starting and stopping recording accordingly.'''
    global image_mode
    global is_recording

    ffmpeg_process = None
    have_started = False
    while True: 
        if image_mode == False and is_recording == True and have_started == False:
            ffmpeg_process = start_recording()
            have_started = True

        elif image_mode == False and is_recording == False and have_started == True:
            ffmpeg_process = stop_recording(ffmpeg_process)
            have_started = False

        elif image_mode == True and is_recording == True:
            ffmpeg_process = capture_image()
            is_recording = False


def start_recording():
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'video4linux2',  # Example input format
        '-i', '/dev/video0',  # Example input source
        'PleaseWork.mp4'  # Output file
    ]
    # Start FFmpeg process
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

    return ffmpeg_process

def stop_recording(ffmpeg_process):

    ffmpeg_process.stdin.write(b'q\n')
    ffmpeg_process.stdin.flush()
    # Wait for the process to terminate
    ffmpeg_process.wait()

    return None


def capture_image():
    ''' Initialized camera and takes picture'''
    
    # Initialize the camera (use the appropriate video device)
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("\tError: Camera not found or could not be opened.")
        return None

    # Capture a single frame from the camera
    ret, frame = camera.read()
    camera.release()

    if ret:
        image = frame
        image_filename = "NewImage.png"
        cv2.imwrite(image_filename, image)

        return image

    else:
        print("\tError: Failed to capture an image.")
        return None

# --------------------------------------------------------------------

if __name__ == '__main__':
    photoLock()
    GPIO.cleanup()