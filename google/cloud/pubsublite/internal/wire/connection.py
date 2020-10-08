from typing import Generic, TypeVar, AsyncContextManager
from abc import abstractmethod

Request = TypeVar("Request")
Response = TypeVar("Response")


class Connection(Generic[Request, Response], AsyncContextManager["Connection"]):
    """
    A connection to an underlying stream. Only one call to 'read' may be outstanding at a time.
    """

    @abstractmethod
    async def write(self, request: Request) -> None:
        """
        Write a message to the stream.

        Raises:
          GoogleAPICallError: When the connection terminates in failure.
        """
        raise NotImplementedError()

    @abstractmethod
    async def read(self) -> Response:
        """
        Read a message off of the stream.

        Raises:
          GoogleAPICallError: When the connection terminates in failure.
        """
        raise NotImplementedError()


class ConnectionFactory(Generic[Request, Response]):
    """A factory for producing Connections."""

    async def new(self) -> Connection[Request, Response]:
        raise NotImplementedError()
