from typing import NamedTuple

from google.cloud.pubsublite.location import CloudZone


class TopicPath(NamedTuple):
  project_number: int
  location: CloudZone
  name: str

  def __str__(self):
    return f"projects/{self.project_number}/locations/{self.location}/topics/{self.name}"


class SubscriptionPath(NamedTuple):
  project_number: int
  location: CloudZone
  name: str

  def __str__(self):
    return f"projects/{self.project_number}/locations/{self.location}/subscriptions/{self.name}"
