
class YouDontHavePermissionToModifyFile(Exception):
    def __init__(self, file: str):
        super().__init__(f'File with name {file} already exists and you don\'t have permission to modify it')


class YouDontHavePermissionToViewFile(Exception):
    def __init__(self, file: str):
        super().__init__(f'You don\'t have permission to view file with name {file}')


class FileAlreadyExist(Exception):
    def __init__(self, file: str):
        super().__init__(f'This file already exists {file}')
