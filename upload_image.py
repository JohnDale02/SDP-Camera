import boto3

def main():
    # Create an S3 client
    s3_client = boto3.client('s3')

    # Bucket and file details
    bucket_name = 'unverifiedimages'
    file_key = 'Great1MB.jpg'

    # Path to your downloaded image
    image_path = 'Great1MB.jpg'

    # Read the image file in binary mode
    with open(image_path, 'rb') as file:
        file_content = file.read()

    # Metadata
    metadata = {
        'signature': 'fn23dod2fge',
        'location': 'East of Varrock',
        'time' : '10:32 PM'
    }

    try:
        # Upload the file with metadata
        response = s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_content, Metadata=metadata)
        print(response)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
