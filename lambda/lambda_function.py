import boto3
import json
from get_public_key import get_public_key
from verification import verify_signiture
from recreate_cloud import recreate_image_and_metadata
from send_to_verified import send_to_verified

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

def lambda_function(event, context):
    # Create an S3 client
    s3_client = boto3.client('s3')
    temp_image_path = 'image.jpg'   # recreate the jpg using the cv2 jpg object bytes recieved

    # Extract bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    try:
        # Get the object from S3
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        except Exception as e:
            print(f"Get object error : {e}")

        # Access the object's content
        image_content = response['Body'].read()   # this is the base64 encoded image
 
        #temp_image_path = '/tmp/image.jpg'

        # Access the object's metadata
        metadata = response['Metadata']

        try:
            camera_number, time_data, location_data, signature_encoded = recreate_image_and_metadata(image_content, metadata, temp_image_path)

        except Exception as e:
            print(f"Cannot recreate time and metadata {e}")
        
        try:
            public_key_encoded = get_public_key(camera_number)  # get the public key by using camera number string
            
        except Exception as e:
            print(f"Public key error: {e}")

        print("Entered veryify signiture")

        try:
            valid = verify_signiture(temp_image_path, time_data, location_data, signature_encoded, public_key_encoded)

        except Exception as e:
            print(f"Error verifying or denying signature {e}")

        if valid == True:

            send_to_verified(s3_client, camera_number, time_data, location_data, signature_encoded, temp_image_path)

        else:
            print("Signature is anything but valid")
        

    except Exception as e:
        print(f'There was an exeption: {e}')

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }


lambda_function(event, None)