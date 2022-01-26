import base64

from fastapi import HTTPException


def decode_photo(path, encoded_string):
    with open(path, "wb") as file:
        try:
            file.write(base64.b64decode(encoded_string.encode("utf-8")))
        except Exception:
            raise HTTPException(400, "Invalid photo encoding")
