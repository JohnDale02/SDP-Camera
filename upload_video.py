import boto3

def upload_video(video_bytes, metadata):
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Bucket and file details
    bucket_name = 'unverifiedimages'
    file_key = 'NewVideo.avi'  # The desired key in the S3 bucket

    try:
        # Open the video file in binary mode and upload it
        response = s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=video_bytes, Metadata=metadata, ContentDisposition='attachment')
        print(f"Upload successful. Response: {response}")

    except Exception as e:
        print(f'We had an exception: {e}')
