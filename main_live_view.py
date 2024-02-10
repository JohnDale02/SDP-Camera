import threading 
import RPi.GPIO as GPIO
import time
import subprocess
import cv2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

image_mode = True
is_recording = False
ffmpeg_process = None
have_started = False
# --------------------------------------------------------------------

class PhotoLockGUI(BoxLayout):
    def __init__(self, capture, **kwargs):
        super(PhotoLockGUI, self).__init__(orientation='vertical', **kwargs)
        self.capture = capture
        self.img1 = Image(size_hint=(1, .9))
        self.add_widget(self.img1)
        self.status_label = Label(text='Image', size_hint=(1, .1))
        self.add_widget(self.status_label)
        Clock.schedule_interval(self.update, 1.0 / 33.0)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Convert it to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = image_texture

            # Update status
            if image_mode:
                self.status_label.text = 'Image'
            else:
                self.status_label.text = 'Video'

            if is_recording:
                self.status_label.text += ' - Recording'
            
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