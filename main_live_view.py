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
capture = cv2.VideoCapture(0)  # capture object for liveView



# --------------------------------------------------------------------

def photoLock():
    '''Main Function that performs all PhotoLock software: "The Main" '''
    recordThread = threading.Thread(target=record_thread)
    guiThread = threading.Thread(target=gui_thread)

    recordThread.start()
    guiThread.start()

    recordThread.join()
    guiThread.join()



def record_thread():
    ''' Thread resonsible for updating states of camera recording mode and recording state'''
    global image_mode
    global is_recording

    mode_button, record_button = setup_gpio()
    #changeModeThread = threading.Thread(target=toggle_image_mode, args=(mode_button,), daemon=True)
    #changeRecordingThread = threading.Thread(target=toggle_recording, args=(record_button,), daemon=True)
    handleCaptureThread = threading.Thread(target=handle_capture, daemon=True)

    #changeModeThread.start()
    #changeRecordingThread.start()
    handleCaptureThread.start()

    while True:
        continue
     

def gui_thread():
    ''' Thread responsible for reflecting state changes to the GUI'''
    global root, text_box, recording_indicator, video_label

    root = tk.Tk()
    root.geometry("800x480")

    # Create a text box widget
    text_box = ttk.Label(root, text="", background="white", font=("Helvetica", 16))
    
    # Create a recording indicator
    recording_indicator = tk.Canvas(root, width=50, height=50, highlightthickness=0)
    recording_indicator.create_oval(5, 5, 45, 45, fill="red")

    # Create a label for displaying the video
    video_label = tk.Label(root)
    video_label.pack()  # Adjust the placement as needed

    # Initialize the GUI update loop
    update_gui()
    update_frame()

    root.mainloop()
# --------------------------------------------------------------------
        
def toggle_image_mode(channel):
    global image_mode
    image_mode = not image_mode
    print("Image mode toggled:", image_mode)

def toggle_recording(channel):
    global is_recording
    is_recording = not is_recording
    print("Recording toggled:", is_recording)

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

    # For the recording indicator, check if its display state needs to change
    # This uses the `winfo_ismapped()` method to check if the widget is currently being displayed
    if is_recording and not recording_indicator.winfo_ismapped():
        recording_indicator.place(relx=0.5, rely=0.5, anchor="center")
    elif not is_recording and recording_indicator.winfo_ismapped():
        recording_indicator.place_forget()

    # Schedule the update_gui function to run again after 100ms
    root.after(200, update_gui)

def update_frame():
    global capture
    ret, frame = capture.read()
    if ret:
        # Resize the frame to half the size to reduce processing
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=im)
        video_label.img = img  # Keep a reference to avoid garbage collection
        video_label.config(image=img)
    # Update the frame in the GUI less frequently
    root.after(100, update_frame)  # Adjust the delay as needed

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

        else:
            continue

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

# --------------------------------------------------------------------

if __name__ == '__main__':
    photoLock()
    GPIO.cleanup()