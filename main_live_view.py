import threading 
import RPi.GPIO as GPIO
import time
import subprocess
import cv2
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
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout

image_mode = True
is_recording = False
ffmpeg_process = None
have_started = False
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
            self.recording_indicator = Ellipse(size=(50, 50), pos=(750, 410))
        
        # Update the rectangle size and position when the layout changes
        self.status_layout.bind(pos=self.update_rect, size=self.update_rect)
        
        self.img1 = Image(keep_ratio=True, allow_stretch=True)
        self.add_widget(self.img1)

        # Bind to size changes of the layout to adjust the video size
        self.bind(size=self.adjust_video_size)
        
        self.status_label = Label(text='Image', color=(1, 1, 1, 1), font_size='50sp')  # White text for visibility
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
        self.capture = cv2.VideoCapture(0)
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
    image_mode = not image_mode
    print("Image mode toggled:", image_mode)\

def toggle_recording(channel):
    global image_mode
    global is_recording
    global ffmpeg_process
    global have_started

    is_recording = not is_recording
    print("Recording toggled:", is_recording)

    if image_mode == False and is_recording == True and have_started == False:
        ffmpeg_process = start_recording()
        have_started = True

    elif image_mode == False and is_recording == False and have_started == True:
        ffmpeg_process = stop_recording(ffmpeg_process)
        have_started = False

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

    ffmpeg_process = None
    have_started = False
    while True: 
        if image_mode == False and is_recording == True and have_started == False:
            ffmpeg_process = start_recording()
            have_started = True

        elif image_mode == False and is_recording == False and have_started == True:
            ffmpeg_process = stop_recording(ffmpeg_process)
            have_started = False

        elif image_mode == True and is_recording == True:
            ffmpeg_process = capture_image()
            is_recording = False


def start_recording():
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'video4linux2',  # Example input format
        '-i', '/dev/video0',  # Example input source
        'PleaseWork.mp4'  # Output file
    ]
    # Start FFmpeg process
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

    return ffmpeg_process

def stop_recording(ffmpeg_process):

    ffmpeg_process.stdin.write(b'q\n')
    ffmpeg_process.stdin.flush()
    # Wait for the process to terminate
    ffmpeg_process.wait()

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
        image = frame
        image_filename = "NewImage.png"
        cv2.imwrite(image_filename, image)

        return image

    else:
        print("\tError: Failed to capture an image.")
        return None

# --------------------------------------------------------------------

if __name__ == '__main__':
    setup_gpio()
    threading.Thread(target=handle_capture, daemon=True).start()
    gui_thread()  # This will start the Kivy application
    GPIO.cleanup()