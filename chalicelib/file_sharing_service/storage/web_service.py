import logging
import io
from chalice import Blueprint, Response

from .domain.file import File
from .domain.permission import Permissions
from .exceptions import FileAlreadyExist, YouDontHavePermissionToViewFile, YouDontHavePermissionToModifyFile
from ..iam.domain.user import User
from .interfaces import IStorageModel
from .model.s3_storage_model import S3StorageModel
from ..util import inject_dependencies, read_jwt

LOG = logging.getLogger(__name__)

storage_web_service = Blueprint(__name__)


# TODO querystring schema validation at all web services
@storage_web_service.route('/storage/{filename}', methods=['POST'], content_types=['multipart/form-data'])
@read_jwt(storage_web_service)
@inject_dependencies(storage_model=S3StorageModel)
def create_file(filename, user: User, group: str, storage_model: IStorageModel):
    permissions = Permissions.from_comma_separated_dict(storage_web_service.current_request.query_params or {})
    LOG.critical('here create permissions: %s', permissions)
    file = File(filename, data=io.BytesIO(
        storage_web_service.current_request.raw_body), creator=user, permissions=permissions)
    try:
        storage_model.create_file(file)
    except FileAlreadyExist as e:
        return Response(body={'message': str(e)}, status_code=409)
    else:
        return Response(body={'message': 'File created'}, status_code=201)


@storage_web_service.route('/storage/{filename}', methods=['DELETE'])
@read_jwt(storage_web_service)
@inject_dependencies(storage_model=S3StorageModel)
def delete_file(filename, user: User, group: str, storage_model: IStorageModel):
    try:
        storage_model.delete_file(user, filename)
    except FileNotFoundError as e:
        return Response(body={'message': str(e)}, status_code=404)
    except YouDontHavePermissionToModifyFile as e:
        return Response(body={'message': str(e)}, status_code=403)
    else:
        return Response(body={'message': "File deleted"}, status_code=204)


@storage_web_service.route('/storage/{filename}', methods=['PUT'])
def update_file(name):
    raise NotImplementedError('TODO')


@storage_web_service.route('/storage/{filename}', methods=['GET'])
@read_jwt(storage_web_service)
@inject_dependencies(storage_model=S3StorageModel)
def view_file(filename, user: User, group: str, storage_model: IStorageModel):
    try:
        data = storage_model.view_file(user, filename)
    except FileNotFoundError as e:
        return Response(body={'message': str(e)}, status_code=404)
    except YouDontHavePermissionToViewFile as e:
        return Response(body={'message': str(e)}, status_code=403)
    else:
        return Response(body=data, status_code=200)
