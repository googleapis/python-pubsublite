from typing import NamedTuple


class CloudRegion(NamedTuple):
  name: str


class CloudZone(NamedTuple):
  region: CloudRegion
  zone_id: str

  def __str__(self):
    return f"{self.region.name}-{self.zone_id}"
