from dataclasses import dataclass

from ...iam.domain.identifiable import Identifiable


@dataclass(frozen=True)
class Organization(Identifiable):
    id: str
    name: str

    def to_identifiable(self):
        return Identifiable(self.id)


