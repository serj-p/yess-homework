from ..util import inject_dependencies, validate_request, read_jwt
from .model.cognito_model import CognitoModel

from chalice import Blueprint

iam_web_service = Blueprint(__name__)


organization_schema = {
    "type": "object",
    "properties": {
        "space": {
            "type": "string"
        }
    },
    "required": ["space"]
}


@iam_web_service.route('/iam/create_space', methods=['POST'], content_types=['application/json'])
@validate_request(iam_web_service, organization_schema)
@read_jwt(iam_web_service)
@inject_dependencies(iam=CognitoModel)
def create_space(iam: CognitoModel):
    # TODO check if user has rights to create space
    request = iam_web_service.current_request
    space = request.json_body['space']
    iam.create_space(space)
    return {'message': 'Space %s created successfully' % space}
