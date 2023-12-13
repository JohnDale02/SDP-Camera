import RPi.GPIO as GPIO
import time


# def checkButtonPressed():
#   GPIO.setmode(GPIO.BOARD)

#   button_pin = 37  # Change this to the GPIO pin you connected the button to (This is the RPI4 board # and not GPI board #)

#   # Use internal pull-up resistor
#   GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#   try:
#     input_state = GPIO.input(button_pin)
#     if input_state == False:
#         print("Button Pressed")
#         time.sleep(0.2)  # debounce delay
#     print(input_state)
#   finally:
#       GPIO.cleanup()
#   return (input_state)

# checkButtonPressed()
