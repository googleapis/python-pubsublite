from typing import NamedTuple

from google.api_core.exceptions import InvalidArgument

from google.cloud.pubsublite.location import CloudZone


class LocationPath(NamedTuple):
  project_number: int
  location: CloudZone

  def __str__(self):
    return f"projects/{self.project_number}/locations/{self.location}"


class TopicPath(NamedTuple):
  project_number: int
  location: CloudZone
  name: str

  def __str__(self):
    return f"projects/{self.project_number}/locations/{self.location}/topics/{self.name}"

  def to_location_path(self):
    return LocationPath(self.project_number, self.location)

  @staticmethod
  def parse(to_parse: str) -> "TopicPath":
    splits = to_parse.split("/")
    if len(splits) != 6 or splits[0] != "projects" or splits[2] != "locations" or splits[4] != "topics":
      raise InvalidArgument(
        "Topic path must be formatted like projects/{project_number}/locations/{location}/topics/{name} but was instead " + to_parse)
    project_number: int
    try:
      project_number = int(splits[1])
    except ValueError:
      raise InvalidArgument(
        "Topic path must be formatted like projects/{project_number}/locations/{location}/topics/{name} but was instead " + to_parse)
    return TopicPath(project_number, CloudZone.parse(splits[3]), splits[5])


class SubscriptionPath(NamedTuple):
  project_number: int
  location: CloudZone
  name: str

  def __str__(self):
    return f"projects/{self.project_number}/locations/{self.location}/subscriptions/{self.name}"

  def to_location_path(self):
    return LocationPath(self.project_number, self.location)

  @staticmethod
  def parse(to_parse: str) -> "SubscriptionPath":
    splits = to_parse.split("/")
    if len(splits) != 6 or splits[0] != "projects" or splits[2] != "locations" or splits[4] != "subscriptions":
      raise InvalidArgument(
        "Subscription path must be formatted like projects/{project_number}/locations/{location}/subscriptions/{name} but was instead " + to_parse)
    project_number: int
    try:
      project_number = int(splits[1])
    except ValueError:
      raise InvalidArgument(
        "Subscription path must be formatted like projects/{project_number}/locations/{location}/subscriptions/{name} but was instead " + to_parse)
    return SubscriptionPath(project_number, CloudZone.parse(splits[3]), splits[5])
