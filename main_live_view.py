
import threading 
from threading import Lock, Thread
import RPi.GPIO as GPIO
import time
import subprocess
import cv2
import os
from main import main
from nothing import sleep
from threading import Lock
from GPS_uart import read_gps_data
from upload_saved_media import upload_saved_media
from upload_image import upload_image
from upload_video import upload_video
import json

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'fullscreen', 'auto')

# Now, import the rest of your Kivy components
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image  # Use AsyncImage for potentially better handling of image loading
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from kivy.core.window import Window
Window.show_cursor = False
Window.fullscreen = False  # *********

# -------------Global Variables ------------------------------
image_mode = True
ffmpeg_process = None
record_button = 40
mode_button = 38
# uploading_after_reconnect = False

wifi_status = False
gps_status = False

ignore_button_presses = False  # This flag indicates whether to ignore button events
recording_indicator = False

gps_lock = Lock()
signature_lock = Lock()
record_lock = Lock()   
upload_lock = Lock()   # **** upload lock
mid_video = False

camera_number_string = "1"
save_video_filepath = "/home/sdp/SDP-Camera/tmpVideos"
save_image_filepath = "/home/sdp/SDP-Camera/tmpImages"
object_count = None
gui_instance = None
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
camera.set(cv2.CAP_PROP_FPS, 30.0)
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


# --------------------------------------------------------------------

def setup_gpio():
    global mode_button, record_button
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(record_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(mode_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup event detection
    GPIO.add_event_detect(mode_button, GPIO.FALLING, callback=toggle_image_mode, bouncetime=5000)
    GPIO.add_event_detect(record_button, GPIO.FALLING, callback=toggle_recording, bouncetime=2000)
    
# --------------------------------------------------------------------
    
def update_gps_data_continuously(gps_lock):
    global gps_status
    while True:
        latitude, longitude, formatted_time = read_gps_data(gps_lock)
        if latitude != "None":
            gps_status = True
        else:
            gps_status = False
        # Adjust the sleep time as needed based on how often you want to update GPS data
        time.sleep(10)

# --------------------------------------------------------------------

def update_wifi_status_continuously():
    global wifi_status
    while True:
        response = subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wifi_status = response.returncode == 0
        print(f"\Twifi status in wifi thread: {wifi_status}")
        time.sleep(5)


class PhotoLockGUI(FloatLayout):
    def __init__(self, capture, **kwargs):
        super(PhotoLockGUI, self).__init__(**kwargs)

        Thread(target=update_gps_data_continuously, args=(gps_lock,), daemon=True).start()
        Thread(target=update_wifi_status_continuously, daemon=True).start() 
        Thread(target=upload_saved_media_continuously, args=(upload_lock,), daemon=True).start()  # try to upload all media  **** added if true check and thread


        self.capture = capture

        # Specify the size and position of the background rectangles
        
        self.wifi_status_image = Image(source='nowifi.png', size_hint=(None, None), size=(100, 45))
    
        self.gps_status_image = Image(source='nogps.png', size_hint=(None, None), size=(120, 54))

        # Create a layout for the status label with a background
        self.status_layout = BoxLayout(size_hint=(None, None), size=(100, 45),
                                       pos_hint={'center_x': 0.5, 'center_y': 0.05})

        with self.status_layout.canvas.before:
            Color(0, 0, 0, 0.4)  # Semi-transparent black background
            self.rect = Rectangle(size=self.status_layout.size, pos=self.status_layout.pos)
            self.recording_color = Color(1, 0, 0, 0)  # Start with transparent (invisible)
            self.recording_indicator = Ellipse(size=(50, 50), pos=(740, 410))
            self.status_color = Color(0, 0, 0, 0.4)  # Semi-transparent black background
            self.status_background = Rectangle(size=(70, 120), pos=(25, 354))

        self.status_layout.bind(pos=self.update_rect, size=self.update_rect)
        
        self.img1 = Image(keep_ratio=False, allow_stretch=True)
        self.add_widget(self.img1)

        self.bind(size=self.adjust_video_size)

        self.status_label = Label(text='Image', color=(1, 1, 1, 1), font_size='30sp')
        self.status_layout.add_widget(self.status_label)
        self.add_widget(self.status_layout)

        self.add_widget(self.wifi_status_image)
        self.bind(size=self.adjust_wifi_image_position)
        self.add_widget(self.gps_status_image)
        self.bind(size=self.adjust_gps_image_position)

        # Countdown label and its background
        self.bg_color = Color(0, 0, 0, 0)  # Initially transparent
        self.bg_rect = Rectangle()
        
        self.countdown_label = Label(text="", font_size='30sp', size_hint=(None, None),
                                     size=(100, 50), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        with self.canvas.before:
            self.canvas.add(self.bg_color)
            self.canvas.add(self.bg_rect)
            Color(0, 0, 0, 0.4)  # Semi-transparent black background
            self.indicators_bg_rect = Rectangle(size=(150, 130), pos=(650, 350))
        
        self.add_widget(self.countdown_label)
        
        self.bind(size=self._update_bg_and_label_pos, pos=self._update_bg_and_label_pos)
        
        Clock.schedule_interval(self.update, 1.0 / 33.0)

        Clock.schedule_interval(self.check_wifi_status, 5)
        self.check_wifi_status(0)  # Immediately check the WiFi status upon start
        Clock.schedule_interval(self.check_gps_status, 10)
        self.check_gps_status(0)  # Immediately check the GPS status upon start

    def _update_bg_and_label_pos(self, *args):
        self.bg_rect.pos = (self.width / 2 - 25, self.height / 2 - 25)
        self.bg_rect.size = (50, 50)
        self.countdown_label.pos = (self.width / 2 - 100, self.height / 2 - 50)


    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = texture
            
            mode_text = "Image" if image_mode else "Video"
            self.status_label.text = f"{mode_text}"

            self.recording_color.a = 1 if recording_indicator else 0

    def check_wifi_status(self, dt):
        global wifi_status

        if wifi_status == True:
            self.wifi_status_image.source = 'wifi.png'

        else:
            self.wifi_status_image.source = 'nowifi.png'


    def adjust_wifi_image_position(self, instance, value):
        # Adjust these offsets to move the image closer/further from the edges
        left_offset = 10  # Distance from the right edge
        top_offset = 10    # Distance from the top edge
        
        self.wifi_status_image.pos = (left_offset, 
                                    self.height - self.wifi_status_image.height - top_offset)
        

    def check_gps_status(self, dt):
        # Check for internet connectivity by pinging Google's DNS server
        global gps_status
        if gps_status == True:
            # If there is connectivity, update the source to show the WiFi icon
            self.gps_status_image.source = 'gps.png'
        else:
            # If there is no connectivity, update the source to show the no WiFi icon
            self.gps_status_image.source = 'nogps.png'

    def adjust_gps_image_position(self, instance, value):
        # Adjust these offsets to move the image closer/further from the edges
        left_offset = 0  # Distance from the left edge
        top_offset = 70    # Distance from the top edge
        
        # Position the GPS status image in the top left corner with specified offsets
        self.gps_status_image.pos = (left_offset, 
                                    self.height - self.gps_status_image.height - top_offset)

    def adjust_video_size(self, *args):
        # Aspect ratio of the video feed
        video_aspect_ratio = 15.0 / 9.0

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


    def start_countdown(self, duration=5):
        self.countdown = duration
        self.countdown_label.text = str(self.countdown)
        self.bg_color.rgba = (0, 0, 0, .4)  # Make the background visible
        Clock.schedule_interval(self.update_countdown, 1)

    def update_countdown(self, dt):
        self.countdown -= 1
        if self.countdown > 0:
            self.countdown_label.text = str(self.countdown)
        else:
            self.end_countdown()

    def end_countdown(self):
        self.countdown_label.text = ""
        self.bg_color.rgba = (0, 0, 0, 0)  # Make the background transparent again
        Clock.unschedule(self.update_countdown)
            
class PhotoLockApp(App):
    def build(self):
        global gui_instance
        self.capture = cv2.VideoCapture(2)
        self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
        self.capture.set(cv2.CAP_PROP_FPS, 30.0)
        
        gui_instance = PhotoLockGUI(self.capture)  # Assign the instance to the global variable
        return gui_instance

    def on_stop(self):
        self.capture.release()

def gui_thread():
    PhotoLockApp().run()

# --------------------------------------------------------------------

def toggle_image_mode(channel):
    global image_mode
    global recording_indicator
    global camera

    if not recording_indicator:
        image_mode = not image_mode
    
    if image_mode == True and camera == None and recording_indicator == False:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        camera.set(cv2.CAP_PROP_FPS, 30.0)
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    if image_mode == False and camera != None:
        camera.release()
        camera = None


def toggle_recording(channel): 
    global mode_button
    global record_button
    global image_mode
    global ffmpeg_process
    global object_count
    global recording_indicator 
    global record_lock
    global mid_video
    global camera

    if recording_indicator and not mid_video:
        return 
    
    record_lock.acquire()
    print("Aquired lock in toggle_recording()")

    if image_mode == False and mid_video == False:
        object_count = count_files(save_video_filepath)
        recording_indicator = True
        ffmpeg_process = start_recording(object_count)
        mid_video = True
        record_lock.release()
        print("Released lock after starting video in toggle_recording()")


    elif mid_video == True:
        # Video mode, dont want to record anymore, currently recording
        ffmpeg_process = stop_recording(ffmpeg_process, object_count)
        mid_video = False
        recording_indicator = False
        record_lock.release()
        print("Released lock after stopping video in toggle_recording()")

    elif image_mode == True and mid_video == False:
        # Image mode, we want to start capture, currently not capturing
        recording_indicator= True
        capture_image(camera)
        recording_indicator = False
        record_lock.release()
        print("Released lock after capturing image in toggle_recording()")

    else:
        print("Error: Unknown state in the else case of handle_capture()")
        record_lock.release()
        quit()


# --------------------------------------------------------------------

def handle_capture():
    '''Function for monitoring modes and recording states and starting and stopping recording accordingly.'''
    global image_mode
    global ffmpeg_process
    global object_count
    global recording_indicator 

    if image_mode == False and recording_indicator == False:
        object_count = count_files(save_video_filepath)
        recording_indicator = True
        ffmpeg_process = start_recording(object_count)


    elif image_mode == False and recording_indicator == True:
        # Video mode, dont want to record anymore, currently recording
        ffmpeg_process = stop_recording(ffmpeg_process, object_count)
        recording_indicator = False

    elif image_mode == True:
        # Image mode, we want to start capture, currently not capturing
        recording_indicator= True
        capture_image()
        recording_indicator = False

    else:
        print("Error: Unknown state in the else case of handle_capture()")
        quit()


def start_recording(object_count):

    video_filepath_raw = os.path.join(save_video_filepath, f'{object_count}raw.avi')

    command = [ 
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
        video_filepath_raw
    ]
    
    # Start FFmpeg process
    ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE)

    Clock.schedule_once(lambda dt: gui_instance.start_countdown(duration=3), 0)
    
    return ffmpeg_process

def stop_recording(ffmpeg_process, object_count):
    '''Function for stopping the video and saving it. Key note is that we are not directly uploading after recording videos'''

    ffmpeg_process.stdin.write(b'q\n')
    ffmpeg_process.stdin.flush()
    # Wait for the process to terminate
    ffmpeg_process.wait()

    print("Stopped raw recording")

    video_filepath = os.path.join(save_video_filepath, f'{object_count}.avi')
    video_filepath_raw = os.path.join(save_video_filepath, f'{object_count}raw.avi')
    

    ffmpeg_cut_command = [
    'ffmpeg',
    '-i', video_filepath_raw,  # Input file path
    '-ss', '5',  # Start trimming 5 seconds into the video
    '-c:v', 'copy',  # Copy the video stream without re-encoding
    '-c:a', 'copy',  # Copy the audio stream without re-encoding
    '-threads', '4',
    video_filepath  # Output file path
    ]
    
    print("Began cutting recording")
    ffmpeg_cut_process = subprocess.Popen(ffmpeg_cut_command, stdin=subprocess.PIPE)
    ffmpeg_cut_process.wait()
    print("Stopped cutting recording")
    os.remove(video_filepath_raw)  # remove the video after uploading

    hashSignUploadThread = threading.Thread(target=main, args=(video_filepath, camera_number_string, save_video_filepath, gps_lock, signature_lock, upload_lock,))
    hashSignUploadThread.start()

    return None


def capture_image(camera):
    ''' Initialized camera and takes picture'''
    global gui_instance
    # Initialize the camera (use the appropriate video device)

    if not camera.isOpened():
        print("\tError: Camera not found or could not be opened.")
        return None

    # Capture a single frame from the camera
    frame = None
    for i in range(20):
        ret, frame = camera.read()
    
    if ret:
        image = frame
        # Start automatic processing and upload process for images
        hashSignUploadThread = threading.Thread(target=main, args=(image, camera_number_string, save_image_filepath, gps_lock, signature_lock, upload_lock,))
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

def upload_saved_media_continuously(upload_lock):
    '''thread function for uploading saved media in the background when Wifi is available and media is stored locally.'''
    global wifi_status

    while True:
        print(f"\Twifi status in upload thread: {wifi_status}")
        if wifi_status == True:
            print("Have lock trying to upload ALL FILES from both folders")
            with upload_lock:        
                if os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
                        save_image_filepath = os.path.join(os.getcwd(), "tmpImages")
                else:
                    print("There is no tmpImages directory")         
                if os.path.exists(os.path.join(os.getcwd(), "tmpVideos")): # make a directory for tmpImages if it doesnt exist
                        save_video_filepath = os.path.join(os.getcwd(), "tmpVideos")
                else:
                    print("There is no tmpVideos directory")

                print("Current Directory: ", os.getcwd())
                print("Image Directory: ", save_image_filepath)
                print("Video Directory: ", save_video_filepath)

                for file_name in os.listdir(save_image_filepath):
                    print("Image file name: ", file_name)
                    if file_name.lower().endswith('.png'):
                        file_path = os.path.join(save_image_filepath, file_name) # get the full path
                        image = cv2.imread(file_path)   # read the image
                        _, encoded_image = cv2.imencode(".png", image)  # encode the image
                        
                        file_path_metadata = os.path.join(save_image_filepath, file_name[:-3]+'json') # get matching json file
                        metadata = read_metadata(file_path_metadata)

                        try:
                            upload_image(encoded_image.tobytes(), metadata)   # cv2 png object, metadat
                            os.remove(file_path)
                            os.remove(file_path_metadata)
                        except Exception as e:
                            print(f"Error uploading saved image: {str(e)}")

                for file_name in os.listdir(save_video_filepath):
                    print("VIdeo file name: ", file_name)
                    if file_name.lower().endswith('.avi'):
                        file_path = os.path.join(save_video_filepath, file_name) # get the full path
                        with open(file_path, 'rb') as video:
                            video_bytes = video.read()
                        
                        file_path_metadata = os.path.join(save_video_filepath, file_name[:-3]+'json') # get matching json file
                        metadata = read_metadata(file_path_metadata)

                        try:
                            upload_video(video_bytes, metadata)   # cv2 png object, metadat
                            os.remove(file_path)
                            os.remove(file_path_metadata)
                        except Exception as e:
                            print(f"Error uploading saved image: {str(e)}")
        time.sleep(10)

# -------------------------------------------------------------------
                            
def read_metadata(file_path_metadata):
    with open(file_path_metadata, 'r') as file:
        metadata = json.load(file)
        return metadata
    
# -------------------------------------------------------------------

if __name__ == '__main__':
    setup_gpio()
    gui_thread()  # This will start the Kivy application
    GPIO.cleanup()