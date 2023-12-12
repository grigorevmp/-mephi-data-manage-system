from enum import Enum


class BranchStatus(Enum):
    Active = 1
    Merged = 2

    @staticmethod
    def get_enum_from_value(value):
        if str(value) == "1":
            return BranchStatus.Active
        elif str(value) == "2":
            return BranchStatus.Merged
        else:
            raise NotImplementedError