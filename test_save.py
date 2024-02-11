import cv2
import time

def capture_image():
    '''Initializes the camera and takes a picture, then saves it to a file.'''
    
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    camera.set(cv2.CAP_PROP_FPS, 30.0)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)

    ret, frame = camera.read()

    if ret:
        # Define the filename and path where the image will be saved
        filename = "captured_image.png"  # Change this to your preferred path and filename

        # Save the frame to a file
        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")
    else:
        print("\tError: Failed to capture an image.")

    # Don't forget to release the camera
    camera.release()

# Example usage
capture_image()
