from abc import ABC, abstractmethod
from typing import Generic, List, Iterable
import asyncio

from google.cloud.pubsublite.internal.wire.connection import Request, Response
from google.cloud.pubsublite.internal.wire.work_item import WorkItem


class BatchTester(Generic[Request], ABC):
    """A BatchTester determines whether a given batch of messages must be sent."""

    @abstractmethod
    def test(self, requests: Iterable[Request]) -> bool:
        """
        Args:
          requests: The current outstanding batch.

        Returns: Whether that batch must be sent.
        """
        raise NotImplementedError()


class SerialBatcher(Generic[Request, Response]):
    _tester: BatchTester[Request]
    _requests: List[WorkItem[Request, Response]]  # A list of outstanding requests

    def __init__(self, tester: BatchTester[Request]):
        self._tester = tester
        self._requests = []

    def add(self, request: Request) -> "asyncio.Future[Response]":
        """Add a new request to this batcher. Callers must always call should_flush() after add, and flush() if that returns
        true.

        Args:
          request: The request to send.

        Returns:
          A future that will resolve to the response or a GoogleAPICallError.
        """
        item = WorkItem[Request, Response](request)
        self._requests.append(item)
        return item.response_future

    def should_flush(self) -> bool:
        return self._tester.test(item.request for item in self._requests)

    def flush(self) -> List[WorkItem[Request, Response]]:
        requests = self._requests
        self._requests = []
        return requests
