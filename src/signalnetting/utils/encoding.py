from base64 import b64encode, b64decode


def bstring(data: bytes):
    return b64encode(data).decode("utf-8")


def sbytes(data: str):
    return b64decode(data.encode("utf-8"))
