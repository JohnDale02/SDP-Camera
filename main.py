# Outline for Main function
from take_picture import return_image
from wifi_check import is_internet_available
from create_metadata import create_metadata
from combined import combine
from upload_image import upload_image
from sign import sign_hash
import cv2
import base64

def main():
#---------------------- Wait for Camera input and take picture ----------------------------

	camera_number = "1"  # camera number used to search for public key
	
	# image = return_image()  bring this back ###################################################

	image = cv2.imread('test.jpg')    # cv2 jpg object  DELETE ONLY FOR DEBUGGING PURPOSES 

	print("Image type of test.jpg: {type(image)}")
	
	image_string = base64.b64encode(image)

	print("Took Image")


#---------- Capture GNSS Data (Time and Location) ------------------------

	#time, location, = capture_time_location()  # time and location both returned as strings
	time = "2023-10-29 14:30:00"
	location = "Latitude: 40.7128, Longitude: -74.0060"
	print(f"Recieved Time and GNSS Data: {time}{location}")

#-------------- Hash image + Time + Location ----------------------------------------------

	combined_data = combine(image, time, location)   # returns hash digest (bytes)
	print(f"Made combined_data")

# ---------------- Send image to TPM for Signing ------------------------
	try:
		signature = sign_hash(combined_data)  # byte64 encoded signature
		
	except Exception as e:
		print(str(e))

#---------------- Create Metadata ------------------------------------

	metadata = create_metadata(camera_number, time, location, signature)   # creates a dictionary for the strings [string, string, string, byte64]
	print(f"Metadata: {metadata}")

	print(f"Signature: {signature}")

#------------------ Check if we have Wi-FI -----------------------------

	if is_internet_available():
		print(f"Internet is available...Uploading")

		upload_image(image_string, metadata)   # cv2 jpg object, metadat

		print(f"Uploaded Image")
	
	else: 
		print("No wifi")
        
	# ---------------- Save the image and metadata to files -------------------

#------------- Callback Functions for recieving Success or Failure messages for each image from cloud ------------
	# If success; Delete file from SD Card 
	# If Failure; Reupload 

# --------------- Callback function for re-connecting to  Wi-Fi ----------------------
	# check SD card and upload all photos


main()

