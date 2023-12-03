import RPi.GPIO as GPIO
import time
import os
from main import main



camera_number_string = "1"  # camera number used to search for public key
if not os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
    os.makedirs(os.path.join(os.getcwd(), "tmpImages"))
save_image_filepath = os.path.join(os.getcwd(), "tmpImages")

GPIO.setmode(GPIO.BOARD)

button_pin = 37  # BCM pin number for GPIO 26

# Use internal pull-up resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_callback(channel):
    print("Button Pressed")
    main(camera_number_string, save_image_filepath)  # Call the main function when the button is pressed

# Add an interrupt event for the button press
GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=2250)

try:
    while True:
        # Your script can do other tasks here, but it won't impede the button monitoring
        time.sleep(1)

finally:
    GPIO.cleanup()
