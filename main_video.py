# Outline for Main function
from create_video import create_video
from check_wifi import is_internet_available
from create_metadata import create_metadata
from create_combined import create_combined
from upload_video import upload_video
from create_digest import create_digest
from create_signature import create_signature
from GPS_uart import parse_nmea_sentence, read_gps_data
import cv2
import base64
from save_metadata import save_metadata
import os

def main_video(camera_number_string, save_video_filepath):
#---------------------- Wait for Camera input and take picture ----------------------------
	video, encoded_video, object_count = create_video()  # take the video (return base64 (string) and bytes version of video) 
	print("main: Image captured")

#---------- Capture GNSS Data (Time and Location) ------------------------

	#time, location, = capture_time_location()  # time and location both returned as strings
	#time = "2023-10-29 14:30:00"
	#location = "Latitude: 40.7128, Longitude: -74.0060"
	lat_value, long_value, time_value =  read_gps_data()
	location = (f"{lat_value}, {long_value}")
	time = (f"{time_value}")
	print(f"Recieved Time and GNSS Data: {time}{location}")

#-------------- combine number + image + Time + Location ----------------------------------------------

	combined_data = create_combined(camera_number_string, video, time, location)   # returns combined data as a 
	#print(f"Made combined_data: {combined_data}")

# ---------------- Create digest for signing --------------------------
	try:
		digest = create_digest(combined_data)
		#print("Created Digest: ", digest)

	except Exception as e:
		print(str(e))

# ---------------- Send image to TPM for Signing ------------------------
	try:
		signature_string = create_signature(digest)  # byte64 encoded signature
		#print("Created signature_base64 string: ", signature_string)
		
	except Exception as e:
		print(str(e))

#---------------- Create Metadata ------------------------------------

	metadata = create_metadata(camera_number_string, time, location, signature_string)   # creates a dictionary for the strings [string, string, string, byte64]
	#print(f"Metadata: {metadata}")

#------------------ Check if we have Wi-FI -----------------------------

	if is_internet_available():
		print(f"Internet is available...Uploading")

		upload_video(encoded_video, metadata)   # cv2 png object, metadat
		print(f"Uploaded Video")
	
	else: 
		save_metadata(object_count, metadata, save_video_filepath)
		print("No wifi")
        
	# ---------------- Save the image and metadata to files -------------------

#------------- Callback Functions for recieving Success or Failure messages for each image from cloud ------------
	# If success; Delete file from SD Card 
	# If Failure; Reupload 

# --------------- Callback function for re-connecting to  Wi-Fi ----------------------
	# check SD card and upload all photos

camera_number_string = "1"  # camera number used to search for public key

if not os.path.exists(os.path.join(os.getcwd(), "tmpVideos")): # make a directory for tmpImages if it doesnt exist
    os.makedirs(os.path.join(os.getcwd(), "tmpVideos"))

save_video_filepath = os.path.join(os.getcwd(), "tmpVideos")

main_video(camera_number_string, save_video_filepath)
