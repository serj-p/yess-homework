from uuid import UUID

import boto3

from logging import getLogger

from ..domain.space import Space
from ..domain.user import User
from ...util import get_ssm_parameter

LOG = getLogger(__name__)


class UserPoolNotFoundException(Exception):
    def __init__(self, pool_name):
        super().__init__(self, 'User pool not found %s' % pool_name)


class CognitoModel:
    def __init__(self):
        self._boto_client = boto3.client('cognito-idp')
        self._user_pool_id = self._get_user_pool_id_by_name(get_ssm_parameter('UserPoolNameSSM'))

    def list_spaces(self) -> [Space]:
        # List all groups (dedicated spaces) in Cognito
        response = self._boto_client.list_groups(UserPoolId=self._user_pool_id)
        organizations = [group['GroupName'] for group in response['Groups']]
        raise NotImplementedError('TODO')

    def get_user(self, username) -> User:
        assert username == 'test2@mail.com'
        # TODO just a mock so far
        return User(str(UUID()), 'test2@mail.com')

    # TODO assert user role
    def create_space(self, space: Space):
        # Create a group (dedicated space) in Cognito
        self._boto_client.create_group(
            GroupName=space.name,
            UserPoolId=self._user_pool_id
        )

    def _get_user_pool_id_by_name(self, user_pool_name):
        response = self._boto_client.list_user_pools(MaxResults=60)     # expected to be one per environment
        for user_pool in response['UserPools']:
            if user_pool['Name'] == user_pool_name:
                return user_pool['Id']
        raise UserPoolNotFoundException(user_pool_name)
