import RPi.GPIO as GPIO
import time
import os
import threading
from main import main  # For image capture
from main2 import main2
from video_capture import start_video_capture, stop_video_capture, record_video  # For video capture
from upload_saved_images import upload_saved_images
from save_video import count_vid_files

# Define GPIO pins for the buttons
button_pin_image = 37
button_pin_video = 38

# Setup directory for saving images
camera_number_string = "1"
save_image_filepath = os.path.join(os.getcwd(), "tmpImages")
if not os.path.exists(save_image_filepath):
    os.makedirs(save_image_filepath)

save_video_filepath = os.path.join(os.getcwd(), "tmpVideos")
if not os.path.exists(save_video_filepath):
    os.makedirs(save_video_filepath)

# Video recording flag and lock
is_recording = False
camera_lock = threading.Lock()

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin_image, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin_video, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Callback for image capture
def image_capture_callback(channel):
    print("Image Capture Button Pressed")
    main(camera_number_string, save_image_filepath)

# Callback for video capture
def video_capture_callback(channel):
    print("Video Capture Button Pressed")
    global is_recording
    if camera_lock.acquire(blocking=False):
        try:
            if not is_recording:
                object_count = count_vid_files(save_image_filepath)
                start_video_capture()
                is_recording = True
                threading.Thread(target=record_video, args=(object_count)).start
            else:
                stop_video_capture()
                is_recording = False
                # Post-recording processing can be added here
                main2(camera_number_string, save_image_filepath,f'{object_count}.avi')
        finally:
            camera_lock.release()

# Add event detection for buttons
GPIO.add_event_detect(button_pin_image, GPIO.FALLING, callback=image_capture_callback, bouncetime=2250)
GPIO.add_event_detect(button_pin_video, GPIO.FALLING, callback=video_capture_callback, bouncetime=2250)

# Create a thread for the upload_saved_images function
upload_thread = threading.Thread(target=upload_saved_images)
upload_thread.daemon = True
upload_thread.start()

try:
    while True:
        time.sleep(1)
finally:
    GPIO.cleanup()
