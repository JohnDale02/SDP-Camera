# Outline for Main function
from take_picture import return_image
from wifi_check import is_internet_available
from create_metadata import create_metadata
from hash import hash_all
from upload_image import upload_image

def main():
#---------------------- Wait for Camera input and take picture ----------------------------

	image = return_image()

#---------- Capture GNSS Data (Time and Location) ------------------------

	#time, location, = capture_time_location()
	time = "2023-10-29 14:30:00"
	location = "Latitude: 40.7128, Longitude: -74.0060"

#-------------- Hash image + Time + Location ----------------------------------------------

	hash = hash_all(image, time, location)

# ---------------- Send image to TPM for Signing ------------------------

	signiture = hash
	# signiture = sign_hash(hash)

#---------------- Create Metadata ------------------------------------
	
	metadata = create_metadata(time, location, signiture)

#------------------ Check if we have Wi-FI -----------------------------

	if is_internet_available():
		upload_image(image, metadata)
	
	else: 
		print("No wifi")
        

	# ---------------- Save the image and metadata to files -------------------

#------------- Callback Functions for recieving Success or Failure messages for each image from cloud ------------
	# If success; Delete file from SD Card 
	# If Failure; Reupload 

# --------------- Callback function for re-connecting to  Wi-Fi ----------------------
	# check SD card and upload all photos
