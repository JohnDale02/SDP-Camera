# Outline for Main function

#---------------------- Wait for Camera input ----------------------------


#--------------------- Take Picture -------------------------------------


#---------- Capture GNSS Data (Time and Location) ------------------------


#-------------- Hash image ----------------------------------------------


# ---------------- Send image to TPM for Signing ------------------------

#------------------ Check if we have Wi-FI -----------------------------

	# ----- Send Image to S3 with Metadata (time, location, signiture) ---------
	# ---------------- Save the image and metadata to files -------------------

#------------- Callback Functions for recieving Success or Failure messages for each image from cloud ------------
	# If success; Delete file from SD Card 
	# If Failure; Reupload 

# --------------- Callback function for re-connecting to  Wi-Fi ----------------------
	# check SD card and upload all photos
