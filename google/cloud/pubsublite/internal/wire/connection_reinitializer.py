from typing import Generic
from abc import ABCMeta, abstractmethod
from google.cloud.pubsublite.internal.wire.connection import (
    Connection,
    Request,
    Response,
)


class ConnectionReinitializer(Generic[Request, Response], metaclass=ABCMeta):
    """A class capable of reinitializing a connection after a new one has been created."""

    @abstractmethod
    def reinitialize(self, connection: Connection[Request, Response]):
        """Reinitialize a connection.

        Args:
            connection: The connection to reinitialize

        Raises:
            GoogleAPICallError: If it fails to reinitialize.
        """
        raise NotImplementedError()
