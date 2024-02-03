import cv2
import threading
from save_video import count_vid_files
import os 
# Flag and condition for video recording control
is_recording = False
record_condition = threading.Condition()

def start_video_capture():
    global is_recording
    with record_condition:
        is_recording = True
        record_condition.notify()


def stop_video_capture():
    global is_recording
    with record_condition:
        is_recording = False
        record_condition.notify()

def record_video(object_count):
    
    # Initialize the camera
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("\tError: Camera not found or could not be opened.")
        return

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    frame_width = int(camera.get(3))
    frame_height = int(camera.get(4))
    #Write video to 'video.avi'
    save_image_filepath = os.path.join(os.getcwd(), "tmpImages")
    video_writer = cv2.VideoWriter(f'{save_image_filepath}/{object_count}.avi', fourcc, 60.0, (frame_width, frame_height))

    while True:
        with record_condition:
            if not is_recording:
                break
            ret, frame = camera.read()

        if ret:
            video_writer.write(frame)
        else:
            print("\tError: Failed to capture frame.")
            break

    camera.release()
    video_writer.release()
