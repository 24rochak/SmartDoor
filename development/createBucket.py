import boto3
from botocore.exceptions import ClientError


def create_bucket(bucket_name, region=None):

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
        print("Bucket %s created successfully"%(bucket_name))
    except ClientError as e:
        print(e)
        return False
    return True

def addImagetoBucket(imname):
    client = boto3.client('s3')
    bucket = 'facedatabucketcca2'
    try:
        response = client.upload_file(imname, bucket, 'faceImages/'+imname, ExtraArgs={'ACL': 'public-read'})
        return response
    except ClientError as e:
        return None

def main():
    bucket = 'facedatabucketcca2'
    #create_bucket(bucket_name=bucket)
    success, response = addImagetoBucket('person.jpg')
    print(response, success)


if __name__ == "__main__":
    main()  