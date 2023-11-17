import boto3
import json
import os
from object_count import count_objects_in_bucket
from get_public_key import get_public_key
from verification import verify_signiture

def lambda_handler(event, context):
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Extract bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    try:
        # Get the object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        # Access the object's content
        image_content = response['Body'].read()

        # Access the object's metadata
        metadata = response['Metadata']

        # Process metadata
        camera_number = metadata.get('cameranumber')
        time_data = metadata.get('time')
        location_data = metadata.get('location')
        signature = metadata.get('signature')


        # Process your content and metadata as needed
        print("Image Data: ", image_content)
        print("Metadata:", metadata)

        camera_number = metadata["CameraNumber"]

            # Get public key
        public_key = get_public_key(camera_number)

        image_file_name = image_number + '.jpg'  # Changes file extension to .json

        temp_image_path = '/tmp/image.jpg'

        with open(temp_image_path, 'wb') as file:
            file.write(image_content)

        if verify_signiture(temp_image_path, time_data, location_data, signature, public_key) == True:

            # Get S3 bucket for verified images(camera_number)
            destination_bucket_name = f'camera{camera_number}verifiedimages'

            image_number = count_objects_in_bucket(destination_bucket_name) // 2

            image_file_name = image_number + '.jpg'  # Changes file extension to .json

            temp_image_path = '/tmp/image.jpg'

            with open(temp_image_path, 'wb') as file:
                file.write(image_content)

            s3_client.upload_file(temp_image_path, destination_bucket_name, image_file_name)

            # Create JSON data
            json_data = {
                "Time": time_data,
                "Location": location_data,
                "Signature": signature
            }

                # Save JSON data to a file with the same name as the image
            json_file_name = image_number + '.json'  # Changes file extension to .json
            temp_json_path = f'/tmp/{json_file_name}'
            with open(temp_json_path, 'w') as json_file:
                json.dump(json_data, json_file)

            # Upload JSON file to the same new S3 bucket
            s3_client.upload_file(temp_json_path, destination_bucket_name, json_file_name)

            # Clean up: Delete temporary files
            os.remove(temp_image_path)
            os.remove(temp_json_path)
        

    except Exception as e:
        print(f'There was an exeption: {e}')

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }
