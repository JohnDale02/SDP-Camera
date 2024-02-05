# Outline for Main function
from create_image import create_image
from check_wifi import is_internet_available
from create_metadata import create_metadata
from create_combined import create_combined
from upload_image import upload_image
from create_digest import create_digest
from create_signature import create_signature
from GPS_uart import parse_nmea_sentence, read_gps_data
import cv2
import base64
from save_image import save_image
import os
from create_combined_vid import create_combined_vid , encode_video_to_bytes
from save_video import save_video
from create_combined_vid import create_combined_vid 
from create_vid_digest import create_vid_digest

#Function called as soon Video to finish recording

def main2(camera_number_string, save_image_filepath, object_count):
#----------------------   ----------------------------
	
	print("main2: Video capture complete")

#---------- Capture GNSS Data (Time and Location) ------------------------

	#time, location, = capture_time_location()  # time and location both returned as strings
	#time = "2023-10-29 14:30:00"
	#location = "Latitude: 40.7128, Longitude: -74.0060"
	lat_value, long_value, time_value =  read_gps_data()
	location = (f"{lat_value}, {long_value}")
	time = (f"{time_value}")
	print(f"Recieved Time and GNSS Data: {time}{location}")

#-------------- combine number + image + Time + Location ----------------------------------------------
	
	#vid_filepath = os.path.join(save_image_filepath, f'{object_count}.avi')
	
	#video_hash = create_vid_digest 
	#encoded_video = encode_video_to_bytes(vid_filepath)  # This will be quite large for videos
	combined_data = create_combined_vid(camera_number_string, video_hash, time, location) 

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

		try:
			upload_image(encoded_video, metadata)   # cv2 png object, metadat
		except Exception as e:
			print(f"Exception occurred: {e}")
		print(f"Uploaded Image")
	
	else: 
		save_video(encoded_video, metadata, save_image_filepath, object_count)
		print("No wifi")
        
	# ---------------- Save the image and metadata to files -------------------

#------------- Callback Functions for recieving Success or Failure messages for each image from cloud ------------
	# If success; Delete file from SD Card 
	# If Failure; Reupload 

# --------------- Callback function for re-connecting to  Wi-Fi ----------------------
	# check SD card and upload all photos

camera_number_string = "1"  # camera number used to search for public key

# if not os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
#     os.makedirs(os.path.join(os.getcwd(), "tmpImages"))

save_image_filepath = os.path.join(os.getcwd(), "tmpImages")

#main(camera_number_string, save_image_filepath)
