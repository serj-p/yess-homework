from chalice import Chalice

from chalicelib.file_sharing_service.iam.web_service import iam_web_service
from chalicelib.file_sharing_service.storage.web_service import storage_web_service

app = Chalice(app_name='file_sharing_service')
app.register_blueprint(iam_web_service)
app.register_blueprint(storage_web_service)
