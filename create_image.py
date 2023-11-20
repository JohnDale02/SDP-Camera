import cv2

def create_image():
    '''Captures Image file; returns data as a frame (cv2.imread())'''

    image = capture_image()

    if image is not None:
        print("\tImage not None, Saving...")
        image_filename = "NewImage.png"
        cv2.imwrite(image_filename, image)

        return image
    
    else:
        print("Image is None")
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
        return frame
    else:
        print("\tError: Failed to capture an image.")
        return None
