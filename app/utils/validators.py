"""
Input validation utilities for the Finance Portfolio application.
"""
import re
from datetime import datetime, date
from typing import List, Dict, Any, Union, Optional
from .exceptions import ValidationError


class Validator:
    """Input validation utility class."""
    
    # Constants for validation
    CURRENCIES = ["KRW", "USD"]
    INCOME_CATEGORIES = ["급여", "투자수익", "부수입", "기타"]
    EXPENSE_CATEGORIES = ["식비", "교통", "주거", "통신", "의료", "교육", "여가", "기타"]
    INVESTMENT_TYPES = ["주식", "채권", "펀드", "현금성 자산", "암호화폐", "원자재", "Gold", "기타"]
    
    MAX_STRING_LENGTH = 255
    MAX_MEMO_LENGTH = 1000
    MIN_AMOUNT = 0.01
    MAX_AMOUNT = 999999999999.99
    MIN_EXCHANGE_RATE = 500.0
    MAX_EXCHANGE_RATE = 2000.0
    
    @staticmethod
    def validate_string(value: str, field_name: str, max_length: int = None, required: bool = True) -> str:
        """Validate string input."""
        if not value or not value.strip():
            if required:
                raise ValidationError(f"{field_name}은(는) 필수 입력 항목입니다.")
            return ""
        
        value = value.strip()
        max_len = max_length or Validator.MAX_STRING_LENGTH
        
        if len(value) > max_len:
            raise ValidationError(f"{field_name}은(는) {max_len}자를 초과할 수 없습니다.")
        
        # 특수문자 검증 (SQL 인젝션 방지)
        if re.search(r'[<>"\';\\]', value):
            raise ValidationError(f"{field_name}에는 특수문자(<, >, \", ', ;, \\)를 사용할 수 없습니다.")
        
        return value
    
    @staticmethod
    def validate_amount(value: Union[str, float, int], field_name: str) -> float:
        """Validate monetary amount."""
        try:
            amount = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}은(는) 유효한 숫자여야 합니다.")
        
        if amount < Validator.MIN_AMOUNT:
            raise ValidationError(f"{field_name}은(는) {Validator.MIN_AMOUNT} 이상이어야 합니다.")
        
        if amount > Validator.MAX_AMOUNT:
            raise ValidationError(f"{field_name}은(는) {Validator.MAX_AMOUNT:,.0f}를 초과할 수 없습니다.")
        
        # 소수점 2자리까지만 허용
        return round(amount, 2)
    
    @staticmethod
    def validate_quantity(value: Union[str, float, int], field_name: str) -> float:
        """Validate quantity (can be 0)."""
        try:
            quantity = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}은(는) 유효한 숫자여야 합니다.")
        
        if quantity < 0:
            raise ValidationError(f"{field_name}은(는) 0 이상이어야 합니다.")
        
        if quantity > Validator.MAX_AMOUNT:
            raise ValidationError(f"{field_name}은(는) {Validator.MAX_AMOUNT:,.0f}를 초과할 수 없습니다.")
        
        return round(quantity, 4)  # 주식 수량은 소수점 4자리까지
    
    @staticmethod
    def validate_date(value: Union[str, date, datetime], field_name: str) -> str:
        """Validate date input."""
        if isinstance(value, (date, datetime)):
            return value.strftime("%Y-%m-%d")
        
        if not value:
            raise ValidationError(f"{field_name}은(는) 필수 입력 항목입니다.")
        
        try:
            # 날짜 형식 검증
            parsed_date = datetime.strptime(str(value), "%Y-%m-%d")
            
            # 미래 날짜 검증 (투자일의 경우)
            if parsed_date.date() > datetime.now().date():
                raise ValidationError(f"{field_name}은(는) 오늘 이후의 날짜일 수 없습니다.")
            
            # 너무 과거 날짜 검증 (1900년 이후)
            if parsed_date.year < 1900:
                raise ValidationError(f"{field_name}은(는) 1900년 이후여야 합니다.")
            
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            raise ValidationError(f"{field_name}은(는) YYYY-MM-DD 형식이어야 합니다.")
    
    @staticmethod
    def validate_currency(value: str, field_name: str) -> str:
        """Validate currency."""
        if not value or value not in Validator.CURRENCIES:
            raise ValidationError(f"{field_name}은(는) {', '.join(Validator.CURRENCIES)} 중 하나여야 합니다.")
        return value
    
    @staticmethod
    def validate_category(value: str, field_name: str, category_type: str) -> str:
        """Validate category based on type."""
        categories_map = {
            'income': Validator.INCOME_CATEGORIES,
            'expense': Validator.EXPENSE_CATEGORIES,
            'investment': Validator.INVESTMENT_TYPES
        }
        
        categories = categories_map.get(category_type, [])
        if not categories:
            raise ValidationError(f"알 수 없는 카테고리 유형: {category_type}")
        
        if not value or value not in categories:
            raise ValidationError(f"{field_name}은(는) {', '.join(categories)} 중 하나여야 합니다.")
        return value
    
    @staticmethod
    def validate_exchange_rate(value: Union[str, float, int], field_name: str) -> float:
        """Validate exchange rate."""
        try:
            rate = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}은(는) 유효한 숫자여야 합니다.")
        
        if rate < Validator.MIN_EXCHANGE_RATE or rate > Validator.MAX_EXCHANGE_RATE:
            raise ValidationError(
                f"{field_name}은(는) {Validator.MIN_EXCHANGE_RATE}~{Validator.MAX_EXCHANGE_RATE} 범위여야 합니다."
            )
        
        return round(rate, 2)
    
    @staticmethod
    def validate_symbol(value: str, field_name: str) -> str:
        """Validate stock/crypto symbol."""
        if not value:
            return ""  # 심볼은 선택사항
        
        value = value.strip().upper()
        
        # 기본 형식 검증 (영문자, 숫자, 점, 하이픈만 허용)
        if not re.match(r'^[A-Z0-9.-]+$', value):
            raise ValidationError(f"{field_name}은(는) 영문자, 숫자, 점(.), 하이픈(-)만 사용할 수 있습니다.")
        
        if len(value) > 20:
            raise ValidationError(f"{field_name}은(는) 20자를 초과할 수 없습니다.")
        
        return value


class DataValidator:
    """Data validation for complex objects."""
    
    @staticmethod
    def validate_income_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate income data."""
        validated = {}
        
        validated['date'] = Validator.validate_date(data.get('date'), '수입 날짜')
        validated['category'] = Validator.validate_category(data.get('category'), '수입 분류', 'income')
        validated['amount'] = Validator.validate_amount(data.get('amount'), '수입 금액')
        validated['memo'] = Validator.validate_string(
            data.get('memo', ''), '메모', Validator.MAX_MEMO_LENGTH, required=False
        )
        
        return validated
    
    @staticmethod
    def validate_expense_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate expense data."""
        validated = {}
        
        validated['date'] = Validator.validate_date(data.get('date'), '지출 날짜')
        validated['category'] = Validator.validate_category(data.get('category'), '지출 분류', 'expense')
        validated['amount'] = Validator.validate_amount(data.get('amount'), '지출 금액')
        validated['memo'] = Validator.validate_string(
            data.get('memo', ''), '메모', Validator.MAX_MEMO_LENGTH, required=False
        )
        
        return validated
    
    @staticmethod
    def validate_investment_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate investment data."""
        validated = {}
        
        validated['type'] = Validator.validate_category(data.get('type'), '투자 유형', 'investment')
        validated['symbol'] = Validator.validate_symbol(data.get('symbol', ''), '종목 코드')
        validated['name'] = Validator.validate_string(data.get('name'), '투자 상품명')
        validated['currency'] = Validator.validate_currency(data.get('currency', 'KRW'), '통화')
        validated['amount'] = Validator.validate_amount(data.get('amount'), '투자 금액')
        validated['purchase_date'] = Validator.validate_date(data.get('purchase_date'), '매수일')
        validated['memo'] = Validator.validate_string(
            data.get('memo', ''), '메모', Validator.MAX_MEMO_LENGTH, required=False
        )
        
        # 선택적 필드들
        if data.get('purchase_quantity') is not None:
            validated['purchase_quantity'] = Validator.validate_quantity(
                data.get('purchase_quantity'), '매입 수량'
            )
        
        if data.get('purchase_price') is not None:
            validated['purchase_price'] = Validator.validate_amount(
                data.get('purchase_price'), '매입 가격'
            )
        
        if data.get('current_price') is not None:
            validated['current_price'] = Validator.validate_amount(
                data.get('current_price'), '현재 가격'
            )
        
        if data.get('current_amount') is not None:
            validated['current_amount'] = Validator.validate_amount(
                data.get('current_amount'), '현재 평가금액'
            )
        
        # USD 통화일 경우 환율 필수
        if validated['currency'] == 'USD':
            if data.get('purchase_exchange_rate') is not None:
                validated['purchase_exchange_rate'] = Validator.validate_exchange_rate(
                    data.get('purchase_exchange_rate'), '매입 환율'
                )
            
            if data.get('current_exchange_rate') is not None:
                validated['current_exchange_rate'] = Validator.validate_exchange_rate(
                    data.get('current_exchange_rate'), '현재 환율'
                )
        
        return validated
    
    @staticmethod
    def validate_budget_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate budget data."""
        validated = {}
        
        # 월 형식 검증 (YYYY-MM)
        month = data.get('month')
        if not month or not re.match(r'^\d{4}-\d{2}$', str(month)):
            raise ValidationError('예산 월은 YYYY-MM 형식이어야 합니다.')
        validated['month'] = str(month)
        
        # 카테고리별 예산 검증
        categories = data.get('categories', {})
        if not isinstance(categories, dict):
            raise ValidationError('카테고리 예산 정보가 올바르지 않습니다.')
        
        validated_categories = {}
        total = 0
        
        for category, amount in categories.items():
            if category not in Validator.EXPENSE_CATEGORIES:
                raise ValidationError(f'알 수 없는 예산 카테고리: {category}')
            
            validated_amount = Validator.validate_amount(amount, f'{category} 예산')
            validated_categories[category] = validated_amount
            total += validated_amount
        
        validated['categories'] = validated_categories
        validated['total'] = total
        
        return validated
    
    @staticmethod
    def validate_portfolio_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate portfolio data."""
        validated = {}
        
        for asset_type, asset_data in data.items():
            if not isinstance(asset_data, dict):
                raise ValidationError(f'{asset_type} 자산 정보가 올바르지 않습니다.')
            
            validated_asset = {}
            validated_asset['currency'] = Validator.validate_currency(
                asset_data.get('currency', 'KRW'), f'{asset_type} 통화'
            )
            validated_asset['amount'] = Validator.validate_amount(
                asset_data.get('amount'), f'{asset_type} 금액'
            )
            
            if validated_asset['currency'] == 'USD' and asset_data.get('purchase_exchange_rate'):
                validated_asset['purchase_exchange_rate'] = Validator.validate_exchange_rate(
                    asset_data.get('purchase_exchange_rate'), f'{asset_type} 매입 환율'
                )
            
            validated[asset_type] = validated_asset
        
        return validated


def validate_form_data(data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
    """
    Validate form data based on type.
    
    Args:
        data: Form data to validate
        data_type: Type of data ('income', 'expense', 'investment', 'budget', 'portfolio')
    
    Returns:
        Validated data dictionary
        
    Raises:
        ValidationError: If validation fails
    """
    validators = {
        'income': DataValidator.validate_income_data,
        'expense': DataValidator.validate_expense_data,
        'investment': DataValidator.validate_investment_data,
        'budget': DataValidator.validate_budget_data,
        'portfolio': DataValidator.validate_portfolio_data
    }
    
    validator = validators.get(data_type)
    if not validator:
        raise ValidationError(f'알 수 없는 데이터 유형: {data_type}')
    
    return validator(data)