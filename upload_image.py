import boto3

def upload_image(image, metadata): 
    # image is imread() of our image

    # Create an S3 client
    s3_client = boto3.client('s3')

    # Bucket and file details
    bucket_name = 'unverifiedimages'
    file_key = 'NewImage.jpg'

    # Path to your downloaded image
    image_path = 'NewImage.jpg'

    try:
        # Upload the file with metadata
        print("\tTrying to upload...")
        response = s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=image, Metadata=metadata)
        print(f"Response:{response}")

    except Exception as e:
        print(f'\tWe had an exception {e}')
