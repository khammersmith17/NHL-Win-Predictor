from enum import Enum

class DB_STATUS(Enum):
    USER_FAILURE = -2
    SUCCESS = 1
    FAILURE = 0
    DELETE_FAILURE = -1

class AUTH_STATUS(Enum):
    GRANTED = 1
    DENIED = 0

class PatternConstraints(Enum):
    PASSWORD_PATTERN = "^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}"
    USERNAME_PATTERN = "^[0-9A-Za-z]{6,16}"


