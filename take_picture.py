# capture_image.py

from pynput.mouse import Listener
import cv2

# Define a global variable to store the captured image
captured_image = None

def return_image():
    global captured_image  # Declare the global variable

    # Create a listener that calls the on_click function when a mouse click event occurs
    listener = Listener(on_click=on_click)
    listener.start()

    # Capture the image in the main thread
    captured_image = capture_image()

    # Stop the listener when image capture is done
    listener.stop()
    listener.join()

    if captured_image is not None:
        print("Image not None, now save")
        image_filename = "NewImage.jpg"
        cv2.imwrite(image_filename, captured_image)

        return captured_image
    
    else:
        print("Image is None")
        return None



def on_click(x, y, button, pressed):
    global captured_image  # Declare the global variable
    if pressed:
        print("Capture an Image...")
        captured_image = capture_image()
        

def capture_image():
    # Initialize the camera (use the appropriate video device)
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Camera not found or could not be opened.")
        return None

    # Capture a single frame from the camera
    ret, frame = camera.read()
    camera.release()

    if ret:
        return frame
    else:
        print("Error: Failed to capture an image.")
        return None

return_image()