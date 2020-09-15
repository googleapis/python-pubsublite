from google.cloud.pubsublite.location import CloudRegion


def regional_endpoint(region: CloudRegion):
  return f"{region}-pubsublite.googleapis.com"
