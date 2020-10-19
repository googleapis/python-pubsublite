from google.cloud.pubsublite.types import CloudRegion


def regional_endpoint(region: CloudRegion):
    return f"{region}-pubsublite.googleapis.com"
