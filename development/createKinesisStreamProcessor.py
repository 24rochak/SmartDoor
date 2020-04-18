import boto3
from botocore.exceptions import ClientError

def create_stream_processor(streamProcessorName):
    client = boto3.client('rekognition')
    try:
        response = client.create_stream_processor(
                Input={
                    'KinesisVideoStream': {
                        'Arn': 'arn:aws:kinesisvideo:us-east-1:275443693297:stream/kvs1/1587158742465'
                    }
                },
                Output={
                    'KinesisDataStream': {
                        'Arn': 'arn:aws:kinesis:us-east-1:275443693297:stream/dataStream'
                    }
                },
                Name=streamProcessorName,
                Settings={
                    'FaceSearch': {
                        'CollectionId': 'FacesCollection',
                        'FaceMatchThreshold': float(0.0)
                    }
                },
                RoleArn='arn:aws:iam::275443693297:role/StreamProcessorRole')
        print(response)
    except ClientError as e:
        print(e)

def get_all_stream_processors():
    client = boto3.client('rekognition')
    try:
        response = client.list_stream_processors()
        print(response)
    except ClientError as e:
        print(e)

def start_stream_processor(streamName):
    client = boto3.client('rekognition')
    try:
        response = client.start_stream_processor(Name=streamName)
        print(response)
    except ClientError as e:
        print(e)

def stop_stream_processor(streamName):
    client = boto3.client('rekognition')
    try:
        response = client.stop_stream_processor(Name=streamName)
        print(response)
    except ClientError as e:
        print(e)


def delete_stream_processor(streamName):
    client = boto3.client('rekognition')
    try:
        stop_stream_processor(streamName)
        response = client.delete_stream_processor(Name=streamName)
        print(response)
    except ClientError as e:
        print(e)

def main():
    # collectionID = "FacesCollection"
    streamName = "StreamProcessorforRekognition"
    #create_stream_processor(streamName)
    #start_stream_processor(streamName)
    #get_all_stream_processors()
    #delete_stream_processor(streamName)
    get_all_stream_processors()
    #stop_stream_processor(streamName)
    #streamProcessorARN = "arn:aws:rekognition:us-east-1:275443693297:streamprocessor/StreamProcessorforRekognition"
    
if __name__ == "__main__":
    main()    
