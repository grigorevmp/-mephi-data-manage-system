from enum import Enum


class Role(Enum):
    Admin = 1
    Client = 2
    HeadOfDepartment = 3

    @staticmethod
    def get_enum_from_value(value):
        if str(value) == "1":
            return Role.Admin
        elif str(value) == "2":
            return Role.Client
        elif str(value) == "3":
            return Role.HeadOfDepartment
        else:
            raise NotImplementedError
