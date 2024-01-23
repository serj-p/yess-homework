import unittest

from chalicelib.file_sharing_service.iam.domain.identifiable import Identifiable
from chalicelib.file_sharing_service.iam.domain.user import User
from chalicelib.file_sharing_service.storage.domain.permission import Permissions


class TestPermissions(unittest.TestCase):
    def test_to_ampersand_joined_comma_separated_string(self):
        identifiable1 = Identifiable(id='7025e002-fb92-4c47-92a8-a3023fdebd21')
        identifiable2 = User(username='test', id='7025e002-fb92-4c47-92a8-a3023fdebd22')
        permissions = Permissions(
            can_view={identifiable1, identifiable2},
            can_create={identifiable1},
            can_update={identifiable2},
            can_delete=set()
        )
        result = permissions.to_ampersand_joined_slash_separated_string()
        expected_result = "permission-for-7025e002-fb92-4c47-92a8-a3023fdebd21=can_create/can_view&" \
                          "permission-for-7025e002-fb92-4c47-92a8-a3023fdebd22=can_update/can_view"
        self.assertEqual(result, expected_result)

    def test_from_apmersand_joined_comma_separated_string(self):
        permissions_string = "permission-for-7025e002-fb92-4c47-92a8-a3023fdebd21=can_view/can_create&" \
                             "permission-for-7025e002-fb92-4c47-92a8-a3023fdebd22=can_view/can_update"
        permissions = Permissions.from_ampersand_joined_slash_separated_string(permissions_string)
        identifiable1 = Identifiable(id='7025e002-fb92-4c47-92a8-a3023fdebd21')
        identifiable2 = Identifiable(id='7025e002-fb92-4c47-92a8-a3023fdebd22')
        expected_permissions = Permissions(
            can_view={identifiable1, identifiable2},
            can_create={identifiable1},
            can_update={identifiable2},
            can_delete=set()
        )
        self.assertEqual(permissions, expected_permissions)

    def test_to_ampersand_joined_comma_separated_string_empty(self):
        permissions = Permissions(
            can_view=set(),
            can_create=set(),
            can_update=set(),
            can_delete=set()
        )
        result = permissions.to_ampersand_joined_slash_separated_string()
        expected_result = ''
        self.assertEqual(result, expected_result)

    def test_from_ampersand_joined_comma_separated_string_empty(self):
        permissions_string = ''
        permissions = Permissions.from_ampersand_joined_slash_separated_string(permissions_string)
        expected_permissions = Permissions(
            can_view=set(),
            can_create=set(),
            can_update=set(),
            can_delete=set()
        )
        self.assertEqual(permissions, expected_permissions)

    def test_from_comma_separated_dict(self):
        permissions_dict = {'001a7ed8-920f-4bf8-899c-b04057c75828': ['can_view,can_delete']}
        permissions = Permissions.from_comma_separated_dict(permissions_dict)
        identifiable1 = Identifiable(id='001a7ed8-920f-4bf8-899c-b04057c75828')
        expected_permissions = Permissions(
            can_view={identifiable1},
            can_delete={identifiable1},
            can_create=set(),
            can_update=set()
        )
        self.assertEqual(permissions, expected_permissions)
