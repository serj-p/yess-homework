import pytest
import io
import boto3
import requests
import hmac
import hashlib
import base64


from e2e.aws import get_api_gateway_url, get_user_pool_id

base_uri = get_api_gateway_url()
print('base uri', base_uri)
user_pool_id = get_user_pool_id()
print('user pool id', user_pool_id)
test_user_name = 'test@email.com'
test_user2_name = 'test2@email.com'
test_user3_name = 'test3@email.com'
password = 'Test-passsword111'


def create_app_client():
    client = boto3.client('cognito-idp')
    response = client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName='pytest',
        GenerateSecret=True,  # Set to False if you're creating a client for a JavaScript app
        ExplicitAuthFlows=[
            'ALLOW_USER_PASSWORD_AUTH',
            'ALLOW_REFRESH_TOKEN_AUTH'
        ]
    )
    print('user pool client', response['UserPoolClient'])
    return response['UserPoolClient']

auth_client = create_app_client()


def calculate_secret_hash(client_id, client_secret, username):
    message = bytes(username + client_id, 'utf-8')
    key = bytes(client_secret, 'utf-8')
    secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()
    return secret_hash


def issue_jwt(user_name):
    client = boto3.client('cognito-idp')
    client_id = auth_client['ClientId']
    client_secret = auth_client['ClientSecret']
    response = client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': user_name,
            'PASSWORD': password,
            'SECRET_HASH': calculate_secret_hash(client_id, client_secret, user_name)
        },
        ClientId=client_id,
    )
    return response['AuthenticationResult']['AccessToken']


def create_user(user_name):
    client = boto3.client('cognito-idp')
    try:
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=user_name,
            TemporaryPassword=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': user_name
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ],
            MessageAction='SUPPRESS'  # Suppresses the welcome message
        )
        update_user_password(user_name)
    except client.exceptions.UsernameExistsException:
        return
    else:
        return


def update_user_password(user_name):
    client = boto3.client('cognito-idp')
    response = client.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=user_name,
        Password=password,
        Permanent=True
    )
    return response


def delete_file():
    print('deleting file')
    url = base_uri + "storage/file.txt"
    resp = requests.delete(url, headers={'Authorization': 'Bearer ' + issue_jwt(test_user_name)})
    # resp.raise_for_status()


@pytest.fixture
def create_test_users():
    create_user(test_user_name)
    create_user(test_user2_name)
    create_user(test_user3_name)
    yield


@pytest.fixture
def delete_test_files():
    delete_file()
    yield
    delete_file()


def test_create_file_creates_one(create_test_users, delete_test_files):
    url = base_uri + "storage/file.txt"
    response = requests.post(url, files={'file': io.BytesIO(b'Hello, world!')},
                             headers={'Authorization': 'Bearer ' + issue_jwt(test_user_name)})
    assert response.status_code == 201, response.text
    response = requests.post(url, files={'file': io.BytesIO(b'Hello, world!')},
                             headers={'Authorization': 'Bearer ' + issue_jwt(test_user_name)})
    assert response.status_code == 409, response.text


def test_create_file_can_be_edited_by_one_user_but_not_other(create_test_users, delete_test_files):
    # TODO get id automatically
    url = base_uri + "storage/file.txt?%s=can_view,can_delete" % '001a7ed8-920f-4bf8-899c-b04057c75828'
    response = requests.post(url, files={'file': io.BytesIO(b'Hello, world!')},
                             headers={'Authorization': 'Bearer ' + issue_jwt(test_user_name)})
    assert response.status_code == 201, response.text
    # user 2 reading
    response = requests.get(base_uri + 'storage/file.txt', headers={'Authorization': 'Bearer ' + issue_jwt(test_user2_name)})
    assert response.status_code == 200, response.text
    # user 3 reading
    response = requests.get(base_uri + 'storage/file.txt', headers={'Authorization': 'Bearer ' + issue_jwt(test_user3_name)})
    assert response.status_code == 403, response.text

