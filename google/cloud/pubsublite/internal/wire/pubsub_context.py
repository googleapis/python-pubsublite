from base64 import b64encode
from typing import Mapping, Optional, NamedTuple

from absl import logging
import pkg_resources
from google.protobuf import struct_pb2


class _Semver(NamedTuple):
  major: int
  minor: int


def _version() -> _Semver:
  version = pkg_resources.get_distribution("google-cloud-pubsublite").version
  splits = version.split(".")
  if len(splits) != 3:
    logging.info(f"Failed to extract semver from {version}.")
    return _Semver(0, 0)
  return _Semver(int(splits[0]), int(splits[1]))


def pubsub_context(framework: Optional[str] = None) -> Mapping[str, str]:
  context = struct_pb2.Struct()
  context.fields["language"] = struct_pb2.Value(string_value="PYTHON")
  if framework:
    context.fields["framework"] = struct_pb2.Value(string_value=framework)
  version = _version()
  context.fields["major_version"] = struct_pb2.Value(number_value=version.major)
  context.fields["minor_version"] = struct_pb2.Value(number_value=version.minor)
  encoded = b64encode(context.SerializeToString())
  return {"x-goog-pubsub-context": encoded}

