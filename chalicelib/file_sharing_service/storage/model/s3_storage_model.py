import logging
import boto3

from ..domain.file import File
from ..domain.permission import Permissions, PermissionTypes
from ..exceptions import YouDontHavePermissionToModifyFile, YouDontHavePermissionToViewFile, FileAlreadyExist
from ..interfaces import IStorageModel
from ...iam.domain.user import User

from ...util import get_ssm_parameter


LOG = logging.getLogger(__name__)


class S3StorageModel(IStorageModel):
    def __init__(self):
        self._boto_client = boto3.client('s3')
        self._bucket_name = get_ssm_parameter('FileStorageBucketNameSSM')

    def create_file(self, file: File):
        try:
            self._boto_client.get_object_tagging(Bucket=self._bucket_name, Key=file.name)
            raise FileAlreadyExist(file.name)
        except self._boto_client.exceptions.NoSuchKey as e:
            # no such file, safe to create
            tags = (
                file.permissions + Permissions.full_access_for_identifiable(file.creator)
            ).to_ampersand_joined_slash_separated_string()
            LOG.error('here joined tags: %s', tags)
            self._boto_client.put_object(
                Bucket=self._bucket_name, Key=file.name, Body=file.data, Tagging=tags
            )

    def update_file(self, file: File):
        raise NotImplementedError('TODO')

    def delete_file(self, user: User, filename):
        try:
            existing_tags = self._boto_client.get_object_tagging(Bucket=self._bucket_name, Key=filename)['TagSet']
        except self._boto_client.exceptions.NoSuchKey as e:
            raise FileNotFoundError(filename)
        else:
            LOG.error('here has access: %s', Permissions.from_key_value_list(existing_tags).has_access(
                user, PermissionTypes.CAN_DELETE))
            LOG.error('here permissions: %s', Permissions.from_key_value_list(existing_tags))
            if Permissions.from_key_value_list(existing_tags).has_access(
                    user, PermissionTypes.CAN_DELETE):
                return self._boto_client.delete_object(Bucket=self._bucket_name, Key=filename)
            else:
                raise YouDontHavePermissionToModifyFile(filename)

    def view_file(self, user: User, filename: str):
        try:
            existing_tags = self._boto_client.get_object_tagging(Bucket=self._bucket_name, Key=filename)['TagSet']
        except self._boto_client.exceptions.NoSuchKey as e:
            raise FileNotFoundError(filename)
        else:
            if Permissions.from_key_value_list(existing_tags).has_access(
                    user, PermissionTypes.CAN_VIEW):
                return self._boto_client.get_object(Bucket=self._bucket_name, Key=filename)['Body'].read()
            else:
                raise YouDontHavePermissionToViewFile(filename)
