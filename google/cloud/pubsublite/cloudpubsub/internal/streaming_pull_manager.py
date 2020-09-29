from abc import ABC, abstractmethod
from typing import Optional, Callable

from google.api_core.exceptions import GoogleAPICallError


CloseCallback = Callable[["StreamingPullManager", Optional[GoogleAPICallError]], None]


class StreamingPullManager(ABC):
    """The API expected by StreamingPullFuture."""

    @abstractmethod
    def add_close_callback(self, close_callback: CloseCallback):
        pass

    @abstractmethod
    def close(self):
        pass
