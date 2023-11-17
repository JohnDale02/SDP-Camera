import boto3

def count_objects_in_bucket(bucket_name):
    s3 = boto3.client('s3')
    total_objects = 0

    # Use paginator to handle buckets with more than 1000 objects
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        total_objects += len(page.get('Contents', []))

    return total_objects