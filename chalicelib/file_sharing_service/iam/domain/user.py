from dataclasses import dataclass

from .identifiable import Identifiable


@dataclass(frozen=True)
class User(Identifiable):
    id: str
    username: str

    def to_identifiable(self):
        return Identifiable(self.id)
