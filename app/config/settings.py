"""
Configuration settings for the Finance Portfolio application.
"""
import os
from typing import Dict, List


class Settings:
    """Application settings and configuration."""
    
    # Database settings
    DB_PATH = os.getenv("FINANCE_DB_PATH", "app/data/finance.db")
    DB_TIMEOUT = 30  # seconds
    
    # API settings
    DEFAULT_EXCHANGE_RATE = 1300.0
    API_TIMEOUT = 10  # seconds
    EXCHANGE_RATE_CACHE_TTL = 300  # 5 minutes
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "app/logs/finance.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Validation settings
    MAX_STRING_LENGTH = 255
    MAX_MEMO_LENGTH = 1000
    MIN_AMOUNT = 0.01
    MAX_AMOUNT = 999_999_999_999.99
    MIN_EXCHANGE_RATE = 500.0
    MAX_EXCHANGE_RATE = 2000.0
    
    # UI settings
    PAGE_TITLE = "Personal Finance Portfolio"
    PAGE_ICON = "💰"
    LAYOUT = "wide"
    SIDEBAR_STATE = "expanded"
    
    # Categories
    INCOME_CATEGORIES = ["급여", "투자수익", "부수입", "기타"]
    EXPENSE_CATEGORIES = ["식비", "교통", "주거", "통신", "의료", "교육", "여가", "기타"]
    INVESTMENT_TYPES = ["주식", "채권", "펀드", "현금성 자산", "암호화폐", "원자재", "Gold", "기타"]
    CURRENCIES = ["KRW", "USD"]
    
    # Chart settings
    CHART_COLORS = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", 
        "#FECA57", "#FF9FF3", "#54A0FF", "#5F27CD"
    ]
    
    # Performance settings
    CACHE_TTL = 300  # 5 minutes
    MAX_RECORDS_PER_PAGE = 100
    
    # Security settings
    ALLOWED_FILE_EXTENSIONS = ['.json', '.csv', '.xlsx']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @classmethod
    def get_db_config(cls) -> Dict[str, any]:
        """Get database configuration."""
        return {
            'path': cls.DB_PATH,
            'timeout': cls.DB_TIMEOUT
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, any]:
        """Get API configuration."""
        return {
            'timeout': cls.API_TIMEOUT,
            'default_exchange_rate': cls.DEFAULT_EXCHANGE_RATE,
            'cache_ttl': cls.EXCHANGE_RATE_CACHE_TTL
        }
    
    @classmethod
    def get_validation_config(cls) -> Dict[str, any]:
        """Get validation configuration."""
        return {
            'max_string_length': cls.MAX_STRING_LENGTH,
            'max_memo_length': cls.MAX_MEMO_LENGTH,
            'min_amount': cls.MIN_AMOUNT,
            'max_amount': cls.MAX_AMOUNT,
            'min_exchange_rate': cls.MIN_EXCHANGE_RATE,
            'max_exchange_rate': cls.MAX_EXCHANGE_RATE
        }
    
    @classmethod
    def is_debug_mode(cls) -> bool:
        """Check if debug mode is enabled."""
        return cls.LOG_LEVEL.upper() == "DEBUG"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


class UIConfig:
    """UI-specific configuration."""
    
    # Menu options
    MAIN_MENU_OPTIONS = [
        "Dashboard", "Income/Expense", "Budget", "Investments", "Portfolio"
    ]
    
    MAIN_MENU_ICONS = [
        "house", "currency-exchange", "piggy-bank", "graph-up", "briefcase"
    ]
    
    # Metrics formatting
    CURRENCY_FORMAT = "₩{:,.0f}"
    PERCENTAGE_FORMAT = "{:.1f}%"
    NUMBER_FORMAT = "{:,.0f}"
    
    # Color themes
    SUCCESS_COLOR = "#28a745"
    WARNING_COLOR = "#ffc107"
    ERROR_COLOR = "#dc3545"
    INFO_COLOR = "#17a2b8"
    
    @classmethod
    def get_menu_config(cls) -> Dict[str, List[str]]:
        """Get menu configuration."""
        return {
            'options': cls.MAIN_MENU_OPTIONS,
            'icons': cls.MAIN_MENU_ICONS
        }


# Environment-specific settings
if Settings.is_production():
    # Production overrides
    Settings.LOG_LEVEL = "WARNING"
    Settings.CACHE_TTL = 600  # 10 minutes
else:
    # Development settings
    Settings.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")