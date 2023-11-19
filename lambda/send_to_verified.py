from object_count import count_objects_in_bucket
import json
import os


def send_to_verified(s3_client, camera_number, time_data, location_data, signature, temp_image_path):
# Get S3 bucket for verified images(camera_number)
    destination_bucket_name = f'camera{int(camera_number)}verifiedimages'

    try:
        image_number = count_objects_in_bucket(destination_bucket_name) // 2

    except Exception as e:
        print(f"Count objects in bucket error: {e}")

    image_file_name = str(image_number) + '.jpg'  # Changes file extension to .json

    # Create JSON data
    json_data = {
        "Time": time_data,  # string
        "Location": location_data,   # string
        "Signature": signature  # signature is in base64 encoded (string)
    }

    # Save JSON data to a file with the same name as the image
    json_file_name = image_number + '.json'  # Changes file extension to .json

    #temp_json_path = f'/tmp/{json_file_name}'
    temp_json_path = json_file_name

    with open(temp_json_path, 'w') as json_file:
        json.dump(json_data, json_file)

    try:
        s3_client.upload_file(temp_image_path, destination_bucket_name, image_file_name)

    except Exception as e:
        print(f"Upload to verified bucket error: {e}")
        
    try:
    # Upload JSON file to the same new S3 bucket
        s3_client.upload_file(temp_json_path, destination_bucket_name, json_file_name)
    except Exception as e:
        print(f"Uploading JSON error : {e}")

    # Clean up: Delete temporary files
    os.remove(temp_image_path)
    os.remove(temp_json_path)
