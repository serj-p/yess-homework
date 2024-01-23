import logging
import jwt

from functools import wraps

import jsonschema
import boto3
from chalice import BadRequestError, UnauthorizedError

from chalicelib.file_sharing_service.iam.domain.user import User

LOG = logging.getLogger(__name__)


def validate_request(app, schema):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                jsonschema.validate(instance=app.current_request.json_body, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                raise BadRequestError(str(e))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def inject_dependencies(**dependencies):
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs.update({name: dependency() for name, dependency in dependencies.items()})
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_ssm_parameter(parameter_name):
    # Initialize the SSM client
    ssm = boto3.client('ssm')
    # Get the parameter
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    # Return the parameter value
    return response['Parameter']['Value']


def read_jwt(app):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token_header = app.current_request.headers.get('Authorization')
            if not token_header:
                raise UnauthorizedError('No token provided')
            try:
                token = token_header.split(' ')[1]
                # TODO verify signature
                claims = jwt.decode(token, options={"verify_signature": False})
            except jwt.InvalidTokenError as e:
                raise UnauthorizedError('Invalid token. %s' % str(e))
            user_id = claims.get('sub')
            user = claims.get('username')
            user_group = claims.get('cognito:groups')
            if not user_id:
                raise UnauthorizedError('Invalid claims')

            # Pass the user and user_group to the endpoint method
            return f(*args, user=User(user_id, user), group=user_group, **kwargs)

        return decorated_function
    return decorator
