import logging

from collections import defaultdict
from dataclasses import dataclass
from typing import Set
from enum import Enum

from ...iam.domain.identifiable import Identifiable

LOG = logging.getLogger(__name__)


class PermissionTypes(Enum):
    CAN_VIEW = "can_view"
    CAN_CREATE = "can_create"
    CAN_UPDATE = "can_update"
    CAN_DELETE = "can_delete"


@dataclass(frozen=True)
class Permissions:
    can_view:   Set[Identifiable]
    can_create: Set[Identifiable]
    can_update: Set[Identifiable]
    can_delete: Set[Identifiable]

    def __add__(self, other):
        LOG.error('here self, other: %s, %s', self.can_view, other.can_view)
        return Permissions(
            can_view=self.can_view.union(other.can_view),
            can_create=self.can_create.union(other.can_create),
            can_update=self.can_update.union(other.can_update),
            can_delete=self.can_delete.union(other.can_delete)
        )

    def has_access(self, identifiable: Identifiable, action: PermissionTypes) -> bool:
        LOG.error('here identifiable, __dict__, casted, filtered/casted: %s, %s, %s, %s',
                  identifiable, self.__dict__, identifiable.to_identifiable(), {o.to_identifiable() for o in self.__dict__[action.value]})
        return identifiable.to_identifiable() in {o.to_identifiable() for o in self.__dict__[action.value]}

    @staticmethod
    def full_access_for_identifiable(identifiable: Identifiable) -> 'Permissions':
        return Permissions(
            can_view={identifiable},
            can_create={identifiable},
            can_update={identifiable},
            can_delete={identifiable}
        )

    @staticmethod
    def from_comma_separated_dict(d: dict) -> 'Permissions':
        permissions = defaultdict(set)
        for identifiable_id, actions in d.items():
            identifiable = Identifiable(id=identifiable_id)
            for action in actions[0].split(','):
                permissions[action].add(identifiable)
        return Permissions(
            can_view=permissions.get('can_view', set()),
            can_create=permissions.get('can_create', set()),
            can_update=permissions.get('can_update', set()),
            can_delete=permissions.get('can_delete', set())
        )

    @staticmethod
    def from_key_value_list(kv_list: list[dict]) -> 'Permissions':
        d = defaultdict(set)
        for kv in kv_list:
            identifiable = Identifiable(id=kv['Key'].replace('permission-for-', ''))
            actions = kv['Value'].split('/')
            for action in actions:
                d[action].add(identifiable)
        return Permissions(
            can_view=d['can_view'],
            can_create=d['can_create'],
            can_update=d['can_update'],
            can_delete=d['can_delete']
        )

    @staticmethod
    def from_ampersand_joined_slash_separated_string(s: str) -> 'Permissions':
        d = defaultdict(set)
        for identifiable_permission in s.split('&'):
            if identifiable_permission:
                identifiable, actions = identifiable_permission.split('=')
                for action in actions.split('/'):
                    d[action].add(Identifiable(id=identifiable.replace('permission-for-', '')))
        return Permissions(
            can_view=d['can_view'],
            can_create=d['can_create'],
            can_update=d['can_update'],
            can_delete=d['can_delete']
        )

    def to_ampersand_joined_slash_separated_string(self):
        per_identifiable = defaultdict(set)
        for action, identifiables in self.__dict__.items():
            for identifiable in identifiables:
                per_identifiable[identifiable].add(action)

        return '&'.join(f'permission-for-{identifiable.id}={"/".join(sorted(actions))}'
                        for identifiable, actions in sorted(per_identifiable.items(), key=lambda x: x[0].id))

