import json

import boto3

print('Loading function')


def lambda_handler(event, context):
    
    client = boto3.client('sqs')
    response = client.receive_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/026298698340/SearchQueue', 
                                      MaxNumberOfMessages=5)
    if 'Messages' in response.keys():
        print('Number of Messages: {}'.format(len(response['Messages'])))
        for i in range(len(response['Messages'])):
            print('New Message')
            body = response['Messages'][i]['Body']
            
            handle = response['Messages'][i]['ReceiptHandle']
            deleteResponse = client.delete_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/026298698340/SearchQueue',
                                ReceiptHandle=handle)
            
            info = body.split('|')
            cuisine = info[0]
            phone = info[1]
            number = info[2]
            date = info[3]
            time = info[4]
            print(cuisine + ' ' + phone)
    else:
        print('Empty Queue')
    print(response)
    return 'Finished'  # Echo back the first key value
    #raise Exception('Something went wrong')
