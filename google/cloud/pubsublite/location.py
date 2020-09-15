from typing import NamedTuple

from google.api_core.exceptions import InvalidArgument


class CloudRegion(NamedTuple):
  name: str


class CloudZone(NamedTuple):
  region: CloudRegion
  zone_id: str

  def __str__(self):
    return f"{self.region.name}-{self.zone_id}"

  @staticmethod
  def parse(to_parse: str):
    splits = to_parse.split('-')
    if len(splits) != 3 or len(splits[2]) != 1:
      raise InvalidArgument("Invalid zone name: " + to_parse)
    region = CloudRegion(name=splits[0] + '-' + splits[1])
    return CloudZone(region, zone_id=splits[2])
