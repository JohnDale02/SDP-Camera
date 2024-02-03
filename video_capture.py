import cv2
import threading
from save_video import count_vid_files
import os 
# Flag and condition for video recording control
is_recording = False
record_condition = threading.Condition()

def start_video_capture():
    print("Envoked start_video_capture function")
    global is_recording
    with record_condition:
        is_recording = True
        print(f'is_recording: {is_recording} (start_video_capture function)')
        record_condition.notify()


def stop_video_capture():
    print("Envoked stop_video_capture function")
    global is_recording
    with record_condition:
        is_recording = False
        print(f'is_recording: {is_recording} (stop_video_capture function)')
        record_condition.notify()

def record_video(object_count):
    
    # Initialize the camera
    camera = cv2.VideoCapture(0)
    print("Camera initialized for video capture")
    if not camera.isOpened():
        print("\tError: Camera not found or could not be opened.")
        return

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    frame_width = int(camera.get(3))
    frame_height = int(camera.get(4))
    #Write video to 'video.avi'
    save_image_filepath = os.path.join(os.getcwd(), "tmpImages")
    vid_filepath = os.path.join(save_image_filepath, f'{object_count}.avi')
    video_writer = cv2.VideoWriter(vid_filepath, fourcc, 60.0, (frame_width, frame_height))
    print("Videowriter initalized")
    while True:
        with record_condition:
            if not is_recording:
                break
            try:
            # Your code block here
                ret, frame = camera.read()
                print("\nReading camera frame")
            except Exception as e:
                print(f"Exception occurred: {e}")
        if ret:
            try:
                video_writer.write(frame)
                print("\nWriting frame")
            except Exception as e:
                print(f"Exception occurred: {e}")
            
        else:
            print("\tError: Failed to capture frame.")
            break

    camera.release()
    video_writer.release()
