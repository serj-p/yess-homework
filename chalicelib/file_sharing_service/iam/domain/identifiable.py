from dataclasses import dataclass


@dataclass(frozen=True)
class Identifiable:
    id: str

    def to_identifiable(self) -> 'Identifiable':
        return self
