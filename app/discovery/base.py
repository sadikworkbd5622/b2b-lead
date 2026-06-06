from abc import ABC, abstractmethod

from app.discovery.models import RawBusinessData


class DataSource(ABC):
    @abstractmethod
    def search(self, query: str, location: str, max_results: int = 20) -> list[RawBusinessData]:
        """
        Executes a search and returns raw business data.
        """
        pass
