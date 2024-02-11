# PROBLEMS:
# GPS cannot be read by mulitple threads (need to implement locking for the GPS reading)

import threading 
from threading import Lock
import RPi.GPIO as GPIO
import time
import subprocess
import cv2
import os
from main import main


from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 'auto')

# Now, import the rest of your Kivy components
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout

from kivy.core.window import Window
Window.show_cursor = False

# -------------Global Variables ------------------------------
image_mode = True
is_recording = False
ffmpeg_process = None
have_started = False
gps_lock = Lock()

camera_number_string = "1"
save_video_filepath = os.path.join(os.getcwd(), "tmpVideos")
save_image_filepath = os.path.join(os.getcwd(), "tmpImages")
video_filepath = None
# --------------------------------------------------------------------

class PhotoLockGUI(FloatLayout):
    def __init__(self, capture, **kwargs):
        super(PhotoLockGUI, self).__init__(**kwargs)
        self.capture = capture

        # Create a layout for the status label with a background
        self.status_layout = BoxLayout(size_hint=(None, None), size=(100, 40),
                                       pos_hint={'right': 1, 'y': 0})
        with self.status_layout.canvas.before:
            Color(0, 0, 0, 0.7)  # Semi-transparent black background
            self.rect = Rectangle(size=self.status_layout.size, pos=self.status_layout.pos)
            self.recording_color = Color(1, 0, 0, 0)  # Start with transparent (invisible)
            self.recording_indicator = Ellipse(size=(50, 50), pos=(740, 410))
        
        # Update the rectangle size and position when the layout changes
        self.status_layout.bind(pos=self.update_rect, size=self.update_rect)
        
        self.img1 = Image(keep_ratio=True, allow_stretch=True)
        self.add_widget(self.img1)

        # Bind to size changes of the layout to adjust the video size
        self.bind(size=self.adjust_video_size)
        
        self.status_label = Label(text='Image', color=(1, 1, 1, 1), font_size='20sp')  # White text for visibility
        self.status_layout.add_widget(self.status_label)
        self.add_widget(self.status_layout)
        
        Clock.schedule_interval(self.update, 1.0 / 33.0)
    
    def adjust_video_size(self, *args):
        # Aspect ratio of the video feed
        video_aspect_ratio = 16.0 / 9.0

        # Calculate the maximum possible size of the video feed within the window
        window_width, window_height = self.size

        video_width = window_width
        video_height = video_width / video_aspect_ratio

        # Center the video in the window
        self.img1.size = (video_width, video_height)
        self.img1.pos = ((window_width - video_width) / 2, 0)

        
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            buf1 = cv2.flip(frame, -1)
            buf = buf1.tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = texture
            
            mode_text = "Image" if image_mode else "Video"
            self.status_label.text = f"{mode_text}"

            self.recording_color.a = 1 if is_recording else 0
            
class PhotoLockApp(App):
    def build(self):
        self.capture = cv2.VideoCapture(2)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        return PhotoLockGUI(self.capture)

    def on_stop(self):
        self.capture.release()

def gui_thread():
    PhotoLockApp().run()


# --------------------------------------------------------------------

def toggle_image_mode(channel):
    global image_mode
    global have_started
    global camera_object

    if have_started:  # if someone tried to change video mode while recording
        return
    image_mode = not image_mode

def toggle_recording(channel):
    global is_recording
    is_recording = not is_recording
    handle_capture()

# --------------------------------------------------------------------

def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    record_button = 37
    mode_button = 38
    GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mode_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup event detection
    GPIO.add_event_detect(mode_button, GPIO.FALLING, callback=toggle_image_mode, bouncetime=200)
    GPIO.add_event_detect(record_button, GPIO.FALLING, callback=toggle_recording, bouncetime=200)
    
# --------------------------------------------------------------------

def handle_capture():
    '''Function for monitoring modes and recording states and starting and stopping recording accordingly.'''
    global image_mode
    global is_recording
    global have_started
    global ffmpeg_process
    global video_filepath

    if image_mode == False and is_recording == True and have_started == False:
        ffmpeg_process, video_filepath = start_recording()
        have_started = True

    elif image_mode == False and is_recording == False and have_started == True:
        ffmpeg_process = stop_recording(ffmpeg_process, video_filepath)
        have_started = False

    elif image_mode == True and is_recording == True:
        capture_image()
        is_recording = False

    else:
        pass


def start_recording():

    object_count = count_files(save_video_filepath)
    video_filepath = os.path.join(save_video_filepath, f'{object_count}.avi')

    command = [            # /dev/video3 is for high quality capture (direct from /dev/video0)
        'ffmpeg',
        '-framerate', '30',
        '-video_size', '1920x1080',
        '-i', '/dev/video0',
        '-f', 'alsa', '-i', 'default',
        '-c:v', 'h264_v4l2m2m',
        '-pix_fmt', 'yuv420p',
        '-b:v', '4M',
        '-bufsize', '4M',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-threads', '4',
        video_filepath
    ]
    
    # Start FFmpeg process
    ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE)

    return ffmpeg_process, video_filepath

def stop_recording(ffmpeg_process, video_filepath):
    '''Function for stopping the video and saving it. Key note is that we are not directly uploading after recording videos'''

    ffmpeg_process.stdin.write(b'q\n')
    ffmpeg_process.stdin.flush()
    # Wait for the process to terminate
    ffmpeg_process.wait()

    hashSignUploadThread = threading.Thread(target=main, args=(video_filepath, camera_number_string, save_video_filepath, gps_lock,))
    hashSignUploadThread.start()

    return None


def capture_image():
    ''' Initialized camera and takes picture'''
    
    # Initialize the camera (use the appropriate video device)
    camera_object = cv2.VideoCapture(0) 
    camera_object.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    camera_object.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    time.sleep(2)

    if not camera_object.isOpened():
        print("\tError: Camera not found or could not be opened.")
        return None

    # Capture a single frame from the camera
    ret, frame = camera_object.read()

    if ret:
        image = frame
        # Start automatic processing and upload process for images
        hashSignUploadThread = threading.Thread(target=main, args=(image, camera_number_string, save_image_filepath, gps_lock,))
        hashSignUploadThread.start()

    else:
        print("\tError: Failed to capture an image.")

# --------------------------------------------------------------------

def count_files(directory_path):
    '''Helper function for returning number of PNG files in the directory'''

    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return 0

    count = 0
    # Iterate over all files in the directory
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.avi'):
            count += 1

    return count

# -------------------------------------------------------------------

if __name__ == '__main__':
    setup_gpio()
    threading.Thread(target=handle_capture, daemon=True).start()
    gui_thread()  # This will start the Kivy application
    GPIO.cleanup()