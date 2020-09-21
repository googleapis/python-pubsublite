import base64
import pickle


def to_b64_string(src: object) -> str:
  return base64.b64encode(pickle.dumps(src)).decode('utf-8')


def from_b64_string(src: str) -> object:
  return pickle.loads(base64.b64decode(src.encode('utf-8')))

