import boto3
from botocore.exceptions import ClientError

def create_collection(collection_id):
    client=boto3.client('rekognition')

    #Create a collection
    print('Creating collection:' + collection_id)
    response=client.create_collection(CollectionId=collection_id)
    print('Collection ARN: ' + response['CollectionArn'])
    print('Status code: ' + str(response['StatusCode']))
    print('Done...')


def list_collections():

    max_results=2
    
    client=boto3.client('rekognition')

    #Display all the collections
    print('Displaying collections...')
    response=client.list_collections(MaxResults=max_results)
    collection_count=0
    done=False
    
    while done==False:
        collections=response['CollectionIds']

        for collection in collections:
            print (collection)
            collection_count+=1
        if 'NextToken' in response:
            nextToken=response['NextToken']
            response=client.list_collections(NextToken=nextToken,MaxResults=max_results)
            
        else:
            done=True

    return collection_count   

def describe_collection(collection_id):

    print('Attempting to describe collection ' + collection_id)
    client=boto3.client('rekognition')

    try:
        response=client.describe_collection(CollectionId=collection_id)
        print("Collection Arn: "  + response['CollectionARN'])
        print("Face Count: "  + str(response['FaceCount']))
        print("Face Model Version: "  + response['FaceModelVersion'])
        print("Timestamp: "  + str(response['CreationTimestamp']))

        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print ('The collection ' + collection_id + ' was not found ')
        else:
            print ('Error other than Not Found occurred: ' + e.response['Error']['Message'])
    print('Done...')

def add_faces_to_collection(bucket,photo,collection_id):
    client=boto3.client('rekognition')

    response=client.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                ExternalImageId=photo,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])
    print(response)


def add_faces_to_collection2(imname,collection_id):
    client=boto3.client('rekognition')
    imsource = open(imname,'rb')
    response=client.index_faces(CollectionId=collection_id,
                                Image={'Bytes':imsource.read()},
                                ExternalImageId=imname,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])
    print(response)
    '''print ('Results for ' + photo) 	
    print('Faces indexed:')						
    for faceRecord in response['FaceRecords']:
         print('  Face ID: ' + faceRecord['Face']['FaceId'])
         print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)'''
    return len(response['FaceRecords'])

def list_faces_in_collection(collection):
    client=boto3.client('rekognition')
    try:
        response = client.list_faces(CollectionId=collection)
        faces = response['Faces']
        for face in faces:
            print(face)
    except ClientError as e:
        print(e)

def delete_collection(collection_id):


    print('Attempting to delete collection ' + collection_id)
    client=boto3.client('rekognition')
    status_code=0
    try:
        response=client.delete_collection(CollectionId=collection_id)
        status_code=response['StatusCode']
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print ('The collection ' + collection_id + ' was not found ')
        else:
            print ('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        status_code=e.response['ResponseMetadata']['HTTPStatusCode']
    return(status_code)

def main():
    collection_id='FacesCollection'
    #create_collection(collection_id)
    list_collections()
    #describe_collection(collection_id)

    #bucket = 'facedatabucketcca2'
    #photo = 'rochak-2.jpg'
    #add_faces_to_collection(bucket,photo,collection_id)
    #delete_collection(collection_id)
    #photo = 'rochak-7.jpg'
    #add_faces_to_collection2(photo,collection_id)
    list_faces_in_collection(collection_id)


if __name__ == "__main__":
    main()    
