from grpc import StatusCode
from google.api_core.exceptions import GoogleAPICallError

retryable_codes = {
  StatusCode.DEADLINE_EXCEEDED, StatusCode.ABORTED, StatusCode.INTERNAL, StatusCode.UNAVAILABLE, StatusCode.UNKNOWN
}


def is_retryable(error: GoogleAPICallError) -> bool:
  return error.grpc_status_code in retryable_codes
