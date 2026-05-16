from abc import ABC, abstractmethod

class BaseRule(ABC):
    """
    Abstract base class for all Data Quality Rules
    Adding a new rule only requires extending this class
    """
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def issue_type(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, conn, table_name: str) -> dict:
        """Runs the profiling check and returns issues found"""
        pass

    @abstractmethod
    def get_sql_transformation(self) -> str:
        """Returns the SQL snippet to fix the identified issue"""
        pass