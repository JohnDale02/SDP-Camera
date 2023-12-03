import RPi.GPIO as GPIO
import time
import os
from main import main
from check_wifi import is_internet_available
from upload_saved_images import upload_saved_images
import threading

camera_number_string = "1"
if not os.path.exists(os.path.join(os.getcwd(), "tmpImages")):
    os.makedirs(os.path.join(os.getcwd(), "tmpImages"))
save_image_filepath = os.path.join(os.getcwd(), "tmpImages")

GPIO.setmode(GPIO.BOARD)

button_pin = 37

GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_callback(channel):
    print("Button Pressed")
    main(camera_number_string, save_image_filepath)

GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=2250)

# Create a thread for the upload_saved_images function
upload_thread = threading.Thread(target=upload_saved_images)
upload_thread.daemon = True
upload_thread.start()

try:
    while True:
        time.sleep(1)

finally:
    GPIO.cleanup()
