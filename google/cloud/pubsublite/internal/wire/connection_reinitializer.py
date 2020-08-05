from typing import Generic
from abc import ABCMeta, abstractmethod
from google.cloud.pubsublite.internal.wire.connection import Connection, Request, Response


class ConnectionReinitializer(Generic[Request, Response], metaclass=ABCMeta):
    @abstractmethod
    def reinitialize(self, connection: Connection[Request, Response]):
        """

        Args:
            connection: The connection to reinitialize

        Raises:
            GoogleAPICallError: If it fails to reinitialize.
        """
        raise NotImplementedError()


