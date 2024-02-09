import threading 
import RPi.GPIO as GPIO
import time

image_mode = True
is_recording = False


def record_thread():
    # if button is pressed 
    # Check the current mode 
    # Create thread for changing the image_mode variable (need to constantly monitor that button for changing modes --> pass that variable to the GUI thread)

    global image_mode
    global is_recording
    is_recording = False

    record_button = setup_gpio()
    changeStateThread = threading.Thread(target=monitor_button, args=(record_button,), daemon=True).start()
    changeStateThread.start()

    while True:
        print(f"Recording: {is_recording}")
        time.sleep(5)
     


def gui_thread():
    global image_mode
    pass


def photoLock():

    recordThread = threading.Thread(target=record_thread)
    guiThread = threading.Thread(target=gui_thread)

    recordThread.start()
    guiThread.start()

    recordThread.join()
    guiThread.join()



def monitor_button(record_button):
    global image_mode

    while True:
        button_state = GPIO.input(record_button)
        if button_state == False:
            print("Button pressed.")
            image_mode = not image_mode
            print(f"Changing image mode to: {image_mode}")
            time.sleep(.2)



def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    record_button = 37  # Use the physical pin numbering
    GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return record_button


if __name__ == '__main__':
    photoLock()
    GPIO.cleanup()