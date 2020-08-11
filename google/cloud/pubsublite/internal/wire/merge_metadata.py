from typing import Mapping, Optional


def merge_metadata(a: Optional[Mapping[str, str]], b: Optional[Mapping[str, str]]) -> Mapping[str, str]:
  result = {}
  if a:
    for k, v in a.items():
      result[k] = v
  if b:
    for k, v in b.items():
      result[k] = v
  return result
