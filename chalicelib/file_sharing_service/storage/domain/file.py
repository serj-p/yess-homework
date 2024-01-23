import io
from dataclasses import dataclass

from ...iam.domain.user import User
from ...storage.domain.permission import Permissions


@dataclass(frozen=True)
class File:
    name: str
    data: io.BytesIO
    creator: User
    permissions: Permissions
