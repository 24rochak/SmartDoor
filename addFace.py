import json
import boto3
import time
import random
from botocore.exceptions import ClientError

def addFacetoDB(faceID, name, phoneNumber):
    item = {}
    item["faceID"] = {'S': faceID}
    item["name"] = {'S': name}
    item["phoneNumber"] = {'S': phoneNumber}
    
    client = boto3.client('dynamodb')
    try:
        response = client.put_item(TableName="visitors", Item=item)
        return None, response
    except ClientError as e:
        return True, e

def getPasscode(FaceID):
    client = boto3.client('dynamodb')
    data = client.get_item(TableName= "passcodes", Key={'faceID': {'S': FaceID}})
    return data
    
def getFaceDetails(FaceID):
    client = boto3.client('dynamodb')
    try:
        data = client.get_item(TableName= "visitors", Key={'faceID': {'S': FaceID}})
    except:
        return None
    if 'Item' in data:
        return data['Item']
    return None
    
def updatePasscodeDB(FaceID, passcode):
    client = boto3.client('dynamodb')
    item = {}
    item['faceID'] = {'S':FaceID}
    item['passcode'] = {'S':str(passcode)}
    item['ttl'] = {'S':str(int(time.time())+300)}
    try:
        response = client.put_item(TableName="passcodes", Item=item)
    except:
        return None
    return response
    
def sendPasscode(phoneNumber, passcode, faceID):
    client = boto3.client('sns')
    webpage = "https://facedatabucketcca2.s3.amazonaws.com/static/wp2.html?faceID="+faceID
    message = "Your Passcode is: "+str(passcode)+". Visit this link to enter passcode: "+webpage
    try:
        response = client.publish(PhoneNumber = phoneNumber, Message=message)
    except ClientError as e:
        return None, e
    return True, response

def sendPasscodetoVisitor(FaceID):
    response = getPasscode(FaceID)
    print("get Passcode response: ",response)
    if 'Item' in response:
        print("Message has already been sent")
    else:
        details = getFaceDetails(FaceID)
        if details is None:
            print("Fatal: Face ID data not present in visitors")
            return
        
        phoneNumber = details['phoneNumber']['S']
        #phoneNumber = '+16462703160'
        name = details['name']['S']

        passcode = random.randrange(1000,9999)
        response = updatePasscodeDB(FaceID, passcode)
        if response is not None:
            print("Update Passcode DB successfully")
        else:
            print("Update Passcode DB failed")

        err, response = sendPasscode(phoneNumber, passcode, FaceID)
        if err is not None:
            print("Message sent Successfully")
        else:
            print("Sending message failed")
            print(response)


def lambda_handler(event, context):
    
    # TODO implement
    faceID = event["faceID"]
    name = event["name"]
    phoneNumber = "+1" + str(event["phoneNumber"])
    approve = event["approve"]
    
    if not approve:
        return {
        'statusCode': 200,
        'body': json.dumps({'status':'rejected'})
        }
        
    
    bucket = 'facedatabucketcca2'
    collection_id = 'FacesCollection'
    photo = 'faceImages/'+faceID+".jpg"
    
    err, response = addFacetoDB(faceID, name, phoneNumber)
    if err:
        print(response)
        return {
        'statusCode': 200,
        'body': json.dumps({'status':'rejected'})
        }
    sendPasscodetoVisitor(faceID)
    
    return {
        'statusCode': 200,
        'body': json.dumps('approved')
    }
