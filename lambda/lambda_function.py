import boto3
import json

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
        content = response['Body'].read()

        # Access the object's metadata
        metadata = response['Metadata']

        # Process your content and metadata as needed
        print("Image Data: ", content)
        print("Metadata:", metadata)

        camera_number = metadata["CameraNumber"]

            # Get public key
        public_key = get_public_key(camera_number)

            # Get S3 bucket for verified images(camera_number)
        destination_bucket_name = f'camera{camera_number}verifiedimages'

            # Verify the data is authentic
        # verify_signature(image, time, location, signature, public_key)

            # IF verified send to camera bucket
        response = s3_client.put_object(Bucket=destination_bucket_name, Key=object_key)
        

    except Exception as e:
        print(f'There was an exeption: {e}')

    return {
        'statusCode': 200,
        'body': json.dumps('Function executed successfully!')
    }
