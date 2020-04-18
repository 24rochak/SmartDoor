import boto3
from botocore.exceptions import ClientError


def create_data_stream(stream, shardCount):
    client = boto3.client('kinesis')
    try:
        _ = client.create_stream(StreamName=stream,ShardCount=1)
        print("Kinesis Data Stream %s created successfully"%(stream))
    except ClientError as e:
        print(e)

def main():
    dataStream = "KDS1"
    create_data_stream(dataStream,1)

    
if __name__ == "__main__":
    main()    
