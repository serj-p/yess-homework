from abc import ABC, abstractmethod

from ..iam.domain.user import User
from ..storage.domain.file import File


class IStorageModel(ABC):
    @abstractmethod
    def create_file(self, file: File):
        pass

    @abstractmethod
    def update_file(self, file: File):
        pass

    @abstractmethod
    def delete_file(self, user: User, filename: str):
        pass

    @abstractmethod
    def view_file(self, user: User, filename: str):
        pass
