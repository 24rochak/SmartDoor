import json
import base64
import boto3
from botocore.exceptions import ClientError
import cv2
from datetime import datetime
from random import randrange
import time

def getFragement(fragmentID, streamARN, serverTimestamp):
    client = boto3.client('kinesisvideo')
    
    response = client.get_data_endpoint(
                        StreamARN=streamARN,
                        APIName='GET_MEDIA')
    dataEndPoint = response['DataEndpoint']
    
    client = boto3.client('kinesis-video-media', endpoint_url=dataEndPoint)
    response = client.get_media(
                        StreamARN=streamARN,
                        StartSelector={
                                'StartSelectorType': 'FRAGMENT_NUMBER',
                                'AfterFragmentNumber': fragmentID}
                        )
    fname = '/tmp/'+fragmentID+'-'+serverTimestamp+'.webm'
    with open(fname, 'wb+') as f:
        chunk = response['Payload'].read(1024*8)
        while chunk:
            f.write(chunk)
            chunk = response['Payload'].read(1024*8)
    return fname

def getImage(fname):
    cap = cv2.VideoCapture(fname)
    imname = fname.replace('.webm','.jpg')
    #imname = 'tmp/'+fragmentID+'-'+serverTimestamp+'.jpg'
    i = 0
    while cap.isOpened():
      ret, frame = cap.read()
      if not ret:
        continue
      
      cv2.imwrite(imname,frame)
      i+=1
      cap.release()
    return imname

def addImagetoCollection(photo):
    # photo = 'tmp/'+fragmentID+'-'+serverTimestamp+'.jpg'
    collection_id = 'FacesCollection'
    imsource = open(photo,'rb')

    client=boto3.client('rekognition')
    try:
        response = client.index_faces(CollectionId=collection_id,
                                Image={'Bytes':imsource.read()},
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['DEFAULT'])
        return response['FaceRecords'][0]['Face']['FaceId']
    except ClientError as e:
        return None

def addImagetoBucket(imname, faceID):
    # imname = 'tmp/'+fragmentID+'-'+serverTimestamp+'.jpg'
    client = boto3.client('s3')
    bucket = 'facedatabucketcca2'
    fname = 'faceImages/'+faceID+'.jpg'
    try:
        response = client.upload_file(imname, bucket, fname, ExtraArgs={'ACL': 'public-read'})
        return response
    except ClientError as e :
        return e

def indexFace(fragmentID, streamARN, serverTimestamp):
    
    response = getFragement(fragmentID, streamARN, serverTimestamp)
    print("Get fragment response: ",response)
    # response = 'tmp/'+fragmentID+'-'+serverTimestamp+'.webm'

    imname = getImage(response)
    print("Get Image response: ",imname)
    # imname = 'tmp/'+fragmentID+'-'+serverTimestamp+'.jpg'
        
    indexedFaceID = addImagetoCollection(imname)
    print("Add image to Collection: ",indexedFaceID)
    # indexedFaceID = '9b72508c-e03a-4762-af5b-4cd035d39b13'

    response = addImagetoBucket(imname, indexedFaceID)
    print("Add image to bucket: ",response)
    return indexedFaceID

def sendPasscode(phoneNumber, passcode, faceID):
    client = boto3.client('sns')
    webpage = "https://facedatabucketcca2.s3.amazonaws.com/static/wp2.html?faceID="+faceID
    message = "Your Passcode is: "+str(passcode)+". Visit this link to enter passcode: "+webpage
    try:
        response = client.publish(PhoneNumber = phoneNumber, Message=message)
    except:
        return None
    return response

def getPasscode(FaceId):
    client = boto3.client('dynamodb')
    data = client.get_item(TableName= "passcodes", Key={'faceID': {'S': FaceId}})
    return data

def updatePasscodeDB(FaceId, passcode):
    client = boto3.client('dynamodb')
    item = {}
    item['faceID'] = {'S':FaceId}
    item['passcode'] = {'S':str(passcode)}
    item['ttl'] = {'S':str(int(time.time())+300)}
    try:
        response = client.put_item(TableName="passcodes", Item=item)
    except:
        return None
    return response

def updateVisitorsDB(indexedFaceID, name, phoneNumber):
    fname = indexedFaceID+'.jpg'
    item = {}
    item['faceID'] = {'S':indexedFaceID}
    item['name'] = {'S':name}
    item['phoneNumber'] = {'S':phoneNumber}
    item['photos'] = {'M':{'objectKey':{'S':fname},
                            'bucket':{'S':'facedatabucketcca2'},
                            'createdTimestamp':{'S':str(datetime.today().isoformat())}
                            }
                    }

    client = boto3.client('dynamodb')
    try:
        response = client.put_item(TableName="visitors", Item=item)
    except:
        return None
    return response


def getFaceDetails(FaceId):
    client = boto3.client('dynamodb')
    data = client.get_item(TableName= "visitors", Key={'faceID': {'S': FaceId}})
    if 'Item' in data:
        return data['Item'],True
    return None, False

def sendRequest(phoneNumber, message):
    client = boto3.client('sns')
    try:
        response = client.publish(PhoneNumber = phoneNumber, Message=message)
        return response
    except:
        return None

def handleStranger(indexedFaceID):
    webpageURL = "https://facedatabucketcca2.s3.amazonaws.com/static/wp1.html?faceID="+indexedFaceID
    message = "You have a new visitor. Check this page for details "+webpageURL
    phoneNumber = "+16462703160"
    response = sendRequest(phoneNumber, message)
    if response is None:
        print("error sending Request message")
    else:
        print("Successfully sent Request message")

def handleVisitor(FaceId):
    details, exists = getFaceDetails(FaceId)
    if not exists:
        print("Fatal: Detected face not present in visitors")
        return 

    response = getPasscode(FaceId)
    print(response)
    if 'Item' in response:
        print("Message has already been sent")
        return
    else:
        phoneNumber = details['phoneNumber']['S']
        #phoneNumber = '+16462703160'
        name = details['name']['S']
        
        print("Name is: ", name)
        print("Phone Number is: ",phoneNumber)

        passcode = randrange(1000,9999)
        response = updatePasscodeDB(FaceId, passcode)
        if response is not None:
            print("Update Passcode DB successfully")
        else:
            print("Update Passcode DB failed")

        response = sendPasscode(phoneNumber, passcode, FaceId)
        if response is not None:
            print("Message sent Successfully")
        else:
            print("Sending message failed")
        
        # Adding new face to DB.
        # Not required as Rekognition gives new faceID to the same face.
        # Sends duplicate SMS next time.
        '''
        response  = updateVisitorsDB(indexedFaceID, name, phoneNumber)
        if response is not None:
            print("Update Visitor Successful")
        else:
            print("Update Visitor failed")
        '''

def lambda_handler(event, context):
    records = event['Records'][0]
    kinesis = records['kinesis']
    data = kinesis['data']
    datastring = base64.b64decode(data).decode('utf-8')
    data = json.loads(datastring)

    fragmentID = data['InputInformation']['KinesisVideo']['FragmentNumber']
    streamARN = data['InputInformation']['KinesisVideo']['StreamArn']
    serverTimestamp = str(data['InputInformation']['KinesisVideo']['ServerTimestamp']).replace('.','-')
    if len(data['FaceSearchResponse']) > 0:

        matchedFaces = data['FaceSearchResponse'][0]['MatchedFaces']

        if len(matchedFaces)==0:
            print("No matched face found i.e. visitor")
            indexedFaceID = indexFace(fragmentID, streamARN, serverTimestamp)
            handleStranger(indexedFaceID)
            
        else:
            print("Matching face found")
            matchedFaces = matchedFaces[0]

            FaceID = matchedFaces['Face']['FaceId']
            print("FaceID is: ", FaceID)
            #ImageId = matchedFaces['Face']['ImageId']

            handleVisitor(FaceID)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }