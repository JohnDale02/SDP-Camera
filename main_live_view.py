import threading 
import RPi.GPIO as GPIO
import time
import subprocess
import tkinter as tk
from tkinter import ttk

image_mode = True
is_recording = False


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
    changeModeThread = threading.Thread(target=monitor_mode, args=(mode_button,), daemon=True)
    changeRecordingThread = threading.Thread(target=monitor_recording, args=(record_button,), daemon=True)
    handleCaptureThread = threading.Thread(target=handle_capture, daemon=True)

    changeModeThread.start()
    changeRecordingThread.start()
    handleCaptureThread.start()

    while True:
        continue
     

def gui_thread():
    ''' Thread responsible for reflecting state changes to the GUI'''
    global root, text_box, recording_indicator

    root = tk.Tk()
    root.geometry("640x480")

    # Create a text box widget
    text_box = ttk.Label(root, text="", background="white", font=("Helvetica", 16))
    
    # Create a recording indicator
    recording_indicator = tk.Canvas(root, width=50, height=50, highlightthickness=0)
    recording_indicator.create_oval(5, 5, 45, 45, fill="red")

    # Initialize the GUI update loop
    update_gui()

    root.mainloop()
# --------------------------------------------------------------------
        
def monitor_mode(mode_button):
    global image_mode
    while True:
        button_state = GPIO.input(mode_button)
        if button_state == False:
            image_mode = not image_mode
            print("Monitor button has image_mode == ", image_mode)
            time.sleep(.2)


def monitor_recording(record_button):
    global is_recording
    while True:
        button_state = GPIO.input(record_button)
        if button_state == False:
            is_recording = not is_recording
            print("Monitor button has is_recording == ", is_recording)
            time.sleep(.2)

def update_gui():
    global image_mode, is_recording

    # Update the text box based on image_mode
    if image_mode:
        text_box.config(text="Image", anchor="ne")
        text_box.place(relx=1.0, rely=0.0, anchor="ne")
    else:
        text_box.config(text="Video", anchor="se")
        text_box.place(relx=1.0, rely=1.0, anchor="se")

    # Display or hide the recording indicator based on is_recording
    if is_recording:
        recording_indicator.place(relx=0.5, rely=0.5, anchor="center")
    else:
        recording_indicator.place_forget()

    # Schedule the update_gui function to run again after 100ms
    root.after(100, update_gui)

# --------------------------------------------------------------------

def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    record_button = 37 
    mode_button = 38   
    GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mode_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    return mode_button, record_button

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