from dataclasses import dataclass

from .identifiable import Identifiable


@dataclass(frozen=True)
class Space(Identifiable):
    id: str
    name: str

    def to_identifiable(self):
        return Identifiable(self.id)
