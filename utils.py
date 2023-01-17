from base64 import b64encode, b64decode
import json


class NadeoUtils:
    def basic_auth(username, password):
        token = b64encode(f"{username}:{password}".encode(
            'utf-8')).decode("ascii")
        return f'Basic {token}'

    def read_token(token):
        payload = token.split(".")[1]
        payload += "=" * ((4 - len(payload) % 4) % 4)
        return json.loads(b64decode(payload).decode("utf-8"))
