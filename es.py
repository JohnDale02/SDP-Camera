# #Testcode 

# import cv2

# # Open a connection to the USB camera (use the appropriate camera index)
# cap = cv2.VideoCapture(0)

# # Check if the camera opened successfully
# if not cap.isOpened():
#     print("Error: Could not open camera.")
#     exit()

# while True:
#     # Read a frame from the camera
#     ret, frame = cap.read()
#     print(ret, frame)
#    # Only take 1 image
#     break
#     # Check if the frame was read successfully
#     if not ret:
#         print("Error: Could not read frame.")
#         break

#     # 'frame' now contains the raw image data

#     # You can process or save the frame as needed

#     # To exit the loop, you can use a key press event (e.g., press 'q' to quit)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the camera and close the OpenCV window (if any)
# cap.release()
# cv2.destroyAllWindows()







# import cv2
# import hashlib
# import json
# import base64

# def capture_image():
#     # Initialize the camera (use the appropriate video device)
#     camera = cv2.VideoCapture(0)
    
#     if not camera.isOpened():
#         print("Error: Camera not found or could not be opened.")
#         return None

#     # Capture a single frame from the camera
#     ret, frame = camera.read()
#     camera.release()

#     if ret:
#         return frame
#     else:
#         print("Error: Failed to capture an image.")
#         return None

# def calculate_sha256_hash(data):
#     sha256_hash = hashlib.sha256()
#     sha256_hash.update(data)
#     return sha256_hash.hexdigest()

# def main():
#     # Capture an image from the USB camera
#     image = capture_image()

#     if image is not None:
#         # Encode the image as a JPEG byte array
#         _, encoded_image = cv2.imencode(".jpg", image)
        
#         if encoded_image is not None:
#             # Calculate the SHA-256 hash of the image data
#             image_data = encoded_image.tobytes()
#             image_hash = calculate_sha256_hash(image_data)
            
#             # Fake time and location data (placeholders)
#             time_data = "2023-10-29 14:30:00"
#             location_data = "Latitude: 40.7128, Longitude: -74.0060"
            
#             # Encode the image as a base64 string
#             image_base64 = base64.b64encode(image_data).decode("utf-8")
            
#             # Create a dictionary with metadata and image hash
#             metadata = {
#                 "time": time_data,
#                 "location": location_data,
#                 "hash": image_hash
#             }
            
#             # Create a JSON object containing metadata, hash, and the base64-encoded image
#             json_data = {
#                 "metadata": metadata,
#                 "image_data": image_base64
#             }
            
#             # Print the JSON object
#             print(json.dumps(json_data, indent=4))
#         else:
#             print("Error: Image encoding failed.")
#     else:
#         print("Error: Image capture failed.")

# if __name__ == "__main__":
#     main()




#--------------
#Json object print 


# import cv2
# import hashlib
# import json
# #import boto3  # Import the appropriate cloud storage library

# def capture_image():
#     # Initialize the camera (use the appropriate video device)
#     camera = cv2.VideoCapture(0)

#     if not camera.isOpened():
#         print("Error: Camera not found or could not be opened.")
#         return None

#     # Capture a single frame from the camera
#     ret, frame = camera.read()
#     camera.release()

#     if ret:
#         return frame
#     else:
#         print("Error: Failed to capture an image.")
#         return None

# def calculate_sha256_hash(data):
#     sha256_hash = hashlib.sha256()
#     sha256_hash.update(data)
#     return sha256_hash.hexdigest()

# #def upload_image_to_cloud(image_filename, bucket_name, object_key):
#     # Initialize AWS S3 client (modify for your specific cloud storage)
#    # s3 = boto3.client('s3')

#     # Upload the image to the cloud storage
#    # s3.upload_file(image_filename, bucket_name, object_key)

# def main():
#     print("Main")
#     #Capture an image from the USB camera
#     image = capture_image()

#     if image is not None:
#         # Encode the image as a JPEG byte array
#         _, encoded_image = cv2.imencode(".jpg", image)

#         if encoded_image is not None:
#             # Calculate the SHA-256 hash of the image data
#             image_data = encoded_image.tobytes()
#             image_hash = calculate_sha256_hash(image_data)

#             # Save the image as a JPEG file
#             image_filename = "captured_image.jpg"
#             cv2.imwrite(image_filename, image)

#             # Upload the image to your cloud storage service
#             #bucket_name = 'your_bucket_name'  # Replace with your cloud storage bucket name
#            # object_key = 'captured_image.jpg'  # Replace with your preferred object key

#           #  upload_image_to_cloud(image_filename, bucket_name, object_key)

#             # Fake time and location data (placeholders)
#             time_data = "2023-10-29 14:30:00"
#             location_data = "Latitude: 40.7128, Longitude: -74.0060"

#             # Create a dictionary with metadata and image hash
#             metadata = {
#                 "time": time_data,
#                 "location": location_data,
#                 "hash": image_hash
#             }

#             # Print the metadata as JSON (without the image)
#             json_data = {
#                 "metadata": metadata
#             }

#             # Print the JSON object
#             print(json.dumps(json_data, indent=4))
            

# if __name__ == "__main__":
#     main()







import cv2
import hashlib
import json
#import boto3  # Import the appropriate cloud storage library

def capture_image():
    # Initialize the camera (use the appropriate video device)
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Camera not found or could not be opened.")
        return None

    # Capture a single frame from the camera
    ret, frame = camera.read()
    camera.release()

    if ret:
        print(frame)
        return frame
    else:
        print("Error: Failed to capture an image.")
        return None

def calculate_sha256_hash(data):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.hexdigest()

#def upload_image_to_cloud(image_filename, bucket_name, object_key):
    # Initialize AWS S3 client (modify for your specific cloud storage)
   # s3 = boto3.client('s3')

    # Upload the image to the cloud storage
   # s3.upload_file(image_filename, bucket_name, object_key)

def main():
    print("Main")
    #Capture an image from the USB camera
    image = capture_image()

    if image is not None:
        # Encode the image as a JPEG byte array
        _, encoded_image = cv2.imencode(".jpg", image)
        print("ec",encoded_image)
        if encoded_image is not None:
            # Calculate the SHA-256 hash of the image data
            image_data = encoded_image.tobytes()
            image_hash = calculate_sha256_hash(image_data)
            #print("id: " ,image_data)
            # Save the image as a JPEG file
            image_filename = "captured_image.jpg"
            cv2.imwrite(image_filename, image)

            # Upload the image to your cloud storage service
            #bucket_name = 'your_bucket_name'  # Replace with your cloud storage bucket name
           # object_key = 'captured_image.jpg'  # Replace with your preferred object key

          #  upload_image_to_cloud(image_filename, bucket_name, object_key)

            # Fake time and location data (placeholders)
            time_data = "2023-10-29 14:30:00"
            location_data = "Latitude: 40.7128, Longitude: -74.0060"

            # Create a dictionary with metadata and image hash
            metadata = {
                "time": time_data,
                "location": location_data,
                "hash": image_hash
            }

            # Print the metadata as JSON (without the image)
            json_data = {
                "metadata": metadata
            }

            # Define the filename for the JSON file
            json_filename = "metadata.json"

            # Save the JSON object to a file
            with open(json_filename, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)

            # Print a message indicating the JSON file has been saved
            print(f"Metadata has been saved to {json_filename}")
            
            #Print the JSON object
            print(json.dumps(json_data, indent=4))

if __name__ == "__main__":
    main()
