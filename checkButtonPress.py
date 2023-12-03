import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

button_pin = 26  # BCM pin number for GPIO 26

# Use internal pull-up resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        input_state = GPIO.input(button_pin)
        if input_state == False:
            print("Button Pressed")
            time.sleep(0.2)  # debounce delay

finally:
    GPIO.cleanup()
