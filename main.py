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
from upload_saved_images import upload_saved_images
from save_image import save_image
import os

def main(camera_number_string, save_image_filepath):
#---------------------- Wait for Camera input and take picture ----------------------------
	
	image = create_image()  # take the image
	_, encoded_image = cv2.imencode('.png', image)  # we send the encoded image to the cloud 
	print("Took Image")

#---------- Capture GNSS Data (Time and Location) ------------------------

	#time, location, = capture_time_location()  # time and location both returned as strings
	#time = "2023-10-29 14:30:00"
	#location = "Latitude: 40.7128, Longitude: -74.0060"
	lat_value, long_value, time_value =  read_gps_data()
	location = (f"{lat_value}, {long_value}")
	time = (f"{time_value}")
	print(f"Recieved Time and GNSS Data: {time}{location}")

#-------------- combine number + image + Time + Location ----------------------------------------------

	combined_data = create_combined(camera_number_string, image, time, location)   # returns combined data as a 
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

		upload_image(encoded_image.tobytes(), metadata)   # cv2 png object, metadat
		print(f"Uploaded Image")
	
	else: 
		save_image(encoded_image.tobytes(), metadata, save_image_filepath)
		print("No wifi")
        
	# ---------------- Save the image and metadata to files -------------------

#------------- Callback Functions for recieving Success or Failure messages for each image from cloud ------------
	# If success; Delete file from SD Card 
	# If Failure; Reupload 

# --------------- Callback function for re-connecting to  Wi-Fi ----------------------
	# check SD card and upload all photos

camera_number_string = "1"  # camera number used to search for public key

if not os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
    os.makedirs(os.path.join(os.getcwd(), "tmpImages"))

save_image_filepath = os.path.join(os.getcwd(), "tmpImages")


#main(camera_number_string, save_image_filepath)

#upload_saved_images(save_image_filepath)

