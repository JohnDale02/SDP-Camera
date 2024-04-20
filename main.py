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
from save_metadata import save_metadata
import os
from upload_video import upload_video

def main(fingerprint, media_input, camera_number_string, save_media_filepath, gps_lock, signature_lock, upload_lock):
	'''main function for processing media for signing and uploading
				media_input : for images = imread(image) ; for videos = video_filpath for reading bytes from
				camera_number_string : number representing the actual device 
				save_media_filepath : folder for storing the media (tmpImages or tmpVideos)
		'''
	print("Main Called; upload 1 image or video")
	
	if save_media_filepath.endswith('Images'):

		#print("We are dealing with an image here folks")
		save_image_filepath = save_media_filepath
#---------------------- Receive Image input  ----------------------------
		image = media_input
		# image = create_image()  # take the image
		
		_, encoded_image = cv2.imencode('.png', image)  # we send the encoded image to the cloud 
		#print("main: Image captured")

	#---------- Capture GNSS Data (Time and Location) ------------------------

		lat_value, long_value, time_value =  read_gps_data(gps_lock)
		location = (f"{lat_value}, {long_value}")
		time = (f"{time_value}")
		#print(f"Recieved Time and GNSS Data: {time}{location}")

	#-------------- combine number + image + Time + Location ----------------------------------------------

		combined_data = create_combined(fingerprint, camera_number_string, encoded_image.tobytes(), time, location)   # returns combined data as a 

	# ---------------- Create digest for signing --------------------------
		try:
			digest = create_digest(combined_data)

		except Exception as e:
			#print(str(e))
			pass

	# ---------------- Send image to TPM for Signing ------------------------
		try:
			signature_string = create_signature(digest, signature_lock)  # byte64 encoded signature
			
		except Exception as e:
			#print(str(e))
			pass

	#---------------- Create Metadata ------------------------------------

		metadata = create_metadata(fingerprint, camera_number_string, time, location, signature_string)   # creates a dictionary for the strings [string, string, string, byte64]

	#------------------ Check if we have Wi-FI -----------------------------

		with upload_lock:
			print("We have upload_lock for image")
			if is_internet_available():
				print("Have lock trying to upload image from Main")
				upload_image(encoded_image.tobytes(), metadata)   # cv2 png object, metadat
				#print(f"Uploaded Image")
			
			else: 
				save_image(encoded_image.tobytes(), metadata, save_image_filepath)
				#print("No wifi")

	else: # if we are working with a video
		save_video_filepath = save_media_filepath
		#video_filepath = os.path.join(save_video_filepath, media_input)
		video_filepath = media_input

	#---------- Capture GNSS Data (Time and Location) ------------------------

		lat_value, long_value, time_value =  read_gps_data(gps_lock)
		location = (f"{lat_value}, {long_value}")
		time = (f"{time_value}")
		#print(f"Recieved Time and GNSS Data: {time}{location}")

	#---------------------- Receive Video input  ----------------------------

		with upload_lock:  # must have the lock the entire time because reading video from storage and deciding if we should upload or save metadata to JSON
			print("We have upload_lock for video")

			#  IN OUR CASE, VIDEOS WILL BE READ FROM STORAGE AND UPLOADED IN THE BACKGROUND 
			with open(video_filepath, 'rb') as video:
				video_bytes = video.read()
			
			#print("main: Image captured")
			#print("Last 10 bytes of video: ", video_bytes[-10:])

	#-------------- combine number + image + Time + Location ----------------------------------------------

		combined_data = create_combined(fingerprint, camera_number_string, video_bytes, time, location)   # returns combined data as a 

	# ---------------- Create digest for signing --------------------------
		try:
			digest = create_digest(combined_data)

		except Exception as e:
			#print(str(e))
			pass
	# ---------------- Send image to TPM for Signing ------------------------
		try:
			signature_string = create_signature(digest, signature_lock)  # byte64 encoded signature
			
		except Exception as e:
			#print(str(e))
			pass
	#---------------- Create Metadata ------------------------------------

		try:
			metadata = create_metadata(fingerprint, camera_number_string, time, location, signature_string)   # creates a dictionary for the strings [string, string, string, byte64]
		
		except Exception as e:
			#print(f"Could not create metadata for video: {str(e)}")
			pass

		try:
			base, _ = os.path.splitext(media_input)
			save_metadata_filepath = base + ".json"
			save_metadata(metadata, save_metadata_filepath)
		
		except Exception as e:
			#print(f"Could not save metadata for video: {str(e)}")
			pass

		if is_internet_available():
			try:
				print("Have lock trying to upload video from Main")
				upload_video(video_bytes, metadata)  
				os.remove(video_filepath)  # remove the video after uploading
				os.remove(save_metadata_filepath)  # remove the metadata after uploading

			except Exception as e:
				#print(str(e))
				pass
