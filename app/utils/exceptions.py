"""
Custom exceptions for the Finance Portfolio application.
"""


class FinanceAppError(Exception):
    """Base exception for all finance app errors."""
    pass


class DataLoadError(FinanceAppError):
    """Exception raised when data loading fails."""
    def __init__(self, message: str, data_type: str = None):
        self.data_type = data_type
        super().__init__(message)


class DataSaveError(FinanceAppError):
    """Exception raised when data saving fails."""
    def __init__(self, message: str, data_type: str = None):
        self.data_type = data_type
        super().__init__(message)


class APIError(FinanceAppError):
    """Exception raised when external API calls fail."""
    def __init__(self, message: str, api_name: str = None):
        self.api_name = api_name
        super().__init__(message)


class ValidationError(FinanceAppError):
    """Exception raised when data validation fails."""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)


class DatabaseError(FinanceAppError):
    """Exception raised when database operations fail."""
    def __init__(self, message: str, operation: str = None):
        self.operation = operation
        super().__init__(message)