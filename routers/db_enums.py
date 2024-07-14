from enum import Enum

class DB_STATUS(Enum):
    SUCCESS = 1
    FAILURE = 0
    DELETE_FAILURE = -1

class AUTH_STATUS(Enum):
    GRANTED = 1
    DENIED = 0

