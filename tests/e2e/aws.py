import boto3


def get_api_gateway_url():
    client = boto3.client('cloudformation')
    response = client.describe_stacks(StackName='yess-app')
    outputs = response['Stacks'][0]['Outputs']
    for output in outputs:
        if output['OutputKey'] == 'EndpointURL':
            return output['OutputValue']
    raise RuntimeError('cannot find ApiGatewayUrl')


def get_user_pool_id():
    client = boto3.client('cognito-idp')
    response = client.list_user_pools(MaxResults=60)  # Adjust MaxResults as needed
    print('UserPools:', response['UserPools'])
    for user_pool in response['UserPools']:
        if user_pool['Name'] == 'yess_user_pool_dev':
            return user_pool['Id']
    raise RuntimeError('cannot find user pool')
