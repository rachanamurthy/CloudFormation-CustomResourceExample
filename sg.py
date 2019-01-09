import boto3
import json
import uuid
from botocore.vendored import requests

ec2 = boto3.client('ec2')


def creation_of_security_group(event):
    groupName = uuid.uuid4().hex
    groupDescription = event['ResourceProperties'].get('GroupDescription')
    if groupDescription is None:
        raise Exception('Someone forgot the GroupDescription!')

    ec2response = ec2.create_security_group(
            Description=groupDescription,
            GroupName=groupName)

    groupId = ec2response.get('GroupId')

    return groupId

def delete_of_security_group(event):

    groupId = event['PhysicalResourceId']
    ec2response = ec2.delete_security_group(GroupId=groupId)

    return groupId


def send_response(event,result,data={},reason=None,physicalResourceId=None):
    if result not in [ 'SUCCESS', 'FAILED']:
        raise Exception("Result is not a valid result")

    response = { 'Status' : result,
                 'StackId' : event['StackId'],
                 'RequestId' : event['RequestId'],
                 'LogicalResourceId' : event['LogicalResourceId'],
                 'Data' : data }

    if reason is not None: response['Reason'] = reason
    if physicalResourceId is not None:
        response['PhysicalResourceId'] = physicalResourceId
    else:
        response['PhysicalResourceId'] = uuid.uuid4().hex

    json_object = json.dumps(response)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_object))
    }

    print(json_object)
    requests.put(event['ResponseURL'], data=json_object, headers=headers)

def lambda_handler(event, context):
    """
        GroupDescription
        GroupName
    """
    print(json.dumps(event))

    try:
        if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
            groupId = creation_of_security_group(event)

        elif event['RequestType'] == 'Delete':
            groupId = delete_of_security_group(event)

        else:
            return 0

        send_response(event,'SUCCESS',physicalResourceId=groupId)

    except Exception as e:
        # Failure occurred
        # Sending an exception based response

        response = {
            'Status' : 'FAILED',
            'Reason' : str(e),
            'PhysicalResourceId' : event.get('PhysicalResourceId','DoesNotMatter'),
            'StackId' : event['StackId'],
            'RequestId' : event['RequestId'],
            'LogicalResourceId' : event['LogicalResourceId'],
            'Data' : {}
        }

        json_object = json.dumps(response)

        headers = {
            'content-type' : '',
            'content-length' : str(len(json_object))
        }

        print(json_object)
        requests.put(event['ResponseURL'], data=json_object, headers=headers)
