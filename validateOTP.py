import json
import boto3

def validate(faceID, passcode):
    client = boto3.client('dynamodb')
    data = client.get_item(TableName='passcodes',
                        Key={
                            'faceID': {'S': faceID}
                        })
    if 'Item' in data:
        if 'passcode' in data['Item']:
            db_passcode = data['Item']['passcode']['S']
            return db_passcode == passcode
        else:
            print("passcode is not in Item")
            return False
    else:
        print(f"there is no faceID: {faceID} in the database")
        return False

def lambda_handler(event, context):
    faceID = event['messages'][0]['unstructured']['faceID']
    passcode = event['messages'][0]['unstructured']['passcode']
    data = {}
    data["msg"] = f'Your faceID is {faceID}, and your passcode is {passcode}'
    data["result"] = validate(str(faceID), str(passcode))
    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }