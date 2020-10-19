from google.cloud.pubsublite.types.location import CloudRegion


def regional_endpoint(region: CloudRegion):
    return f"{region}-pubsublite.googleapis.com"
