from enum import Enum


class TransferType(str, Enum):
    TRANSFER = "transfer"
    GRANT = "grant"