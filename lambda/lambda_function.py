import boto3
import json
import os
from object_count import count_objects_in_bucket
from get_public_key import get_public_key
from verification import verify_signiture

event = {
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-2",
      "eventTime": "2023-10-29T14:30:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "AWS_PRINCIPAL_ID"
      },
      "requestParameters": {
        "sourceIPAddress": "IP_ADDRESS"
      },
      "responseElements": {
        "x-amz-request-id": "REQUEST_ID",
        "x-amz-id-2": "HOST_ID",
        "x-amz-meta-cameraNumber": "1",
        "x-amz-meta-time": "2023-10-29 14:30:00",
        "x-amz-meta-location": "Latitude: 40.7128, Longitude: -74.0060",
        "x-amz-meta-signature": "0014000b01001ad6a1368828f69e031efa20235b8ad3f9558b25ea45582916e4be4341b12e53a482157ddbf0e3e5ce045ab69c731475bfd2fff29d81d8be7223e53b496dac48bda53bb5fb6b2040c3285ace18ea28060d97ac3fe12d7b11e8b56227a0f0729aaecffe336e3bacaf5d6dece19265cf0ef0f3014fa070ab28b6d19922a389c9c8d4dba3e4ad5dc58cad60971e86758c1e73e6145e3566ee8ca5659b1feb4a6ca95953eab384435f2c979aa2d4238e681704b5046f48242c3a5850ce0d960b6a8e8ff35a443276c8aa6ae87f8b8d2af7e339b2da840674c2f7c01bfd07441b71d3c82b538abdf036fbe48455402d995edbd689e928164531b0f75cdb2f114a623a"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "CONFIGURATION_ID",
        "bucket": {
          "name": "unverifiedimages",
          "ownerIdentity": {
            "principalId": "BUCKET_OWNER_PRINCIPAL_ID"
          },
          "arn": "arn:aws:s3:::unverifiedimages"
        },
        "object": {
          "key": "NewImage.jpg",
          "size": 11543,
          "eTag": "ETAG",
          "sequencer": "SEQUENCER_VALUE"
        }
      }
    }
  ]
}

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

        #temp_image_path = '/tmp/image.jpg'
        temp_image_path = 'image.jpg'

        with open(temp_image_path, 'wb') as file:
            file.write(image_content)

        if verify_signiture(temp_image_path, time_data, location_data, signature, public_key) == True:

            # Get S3 bucket for verified images(camera_number)
            destination_bucket_name = f'camera{camera_number}verifiedimages'

            image_number = count_objects_in_bucket(destination_bucket_name) // 2

            image_file_name = image_number + '.jpg'  # Changes file extension to .json

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

            #temp_json_path = f'/tmp/{json_file_name}'
            temp_json_path = json_file_name



            with open(temp_json_path, 'w') as json_file:
                json.dump(json_data, json_file)

            # Upload JSON file to the same new S3 bucket
            s3_client.upload_file(temp_json_path, destination_bucket_name, json_file_name)
            print("Uploaded that litte guy")

            # Clean up: Delete temporary files
            os.remove(temp_image_path)
            os.remove(temp_json_path)

        else:
            print("Signature is anything but valid")
        
        

    except Exception as e:
        print(f'There was an exeption: {e}')

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }
