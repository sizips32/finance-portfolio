"""
데이터 모델 및 검증 클래스
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class IncomeData:
    """수입 데이터 모델"""
    date: date
    category: str
    amount: Decimal
    memo: Optional[str] = None

    def validate(self) -> bool:
        """데이터 유효성 검증
        
        Returns:
            bool: 유효성 검증 결과
        
        Raises:
            ValueError: 유효하지 않은 데이터
        """
        if not self.date:
            raise ValueError("날짜는 필수입니다.")
        if not self.category:
            raise ValueError("카테고리는 필수입니다.")
        if not self.amount or self.amount <= 0:
            raise ValueError("금액은 0보다 커야 합니다.")
        return True


@dataclass
class ExpenseData:
    """지출 데이터 모델"""
    date: date
    category: str
    amount: Decimal
    memo: Optional[str] = None

    def validate(self) -> bool:
        """데이터 유효성 검증
        
        Returns:
            bool: 유효성 검증 결과
        
        Raises:
            ValueError: 유효하지 않은 데이터
        """
        if not self.date:
            raise ValueError("날짜는 필수입니다.")
        if not self.category:
            raise ValueError("카테고리는 필수입니다.")
        if not self.amount or self.amount <= 0:
            raise ValueError("금액은 0보다 커야 합니다.")
        return True


@dataclass
class InvestmentData:
    """투자 데이터 모델"""
    type: str
    name: str
    amount: Decimal  # 매입금액 (원화 기준)
    purchase_date: date
    symbol: Optional[str] = None
    purchase_quantity: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None  # 현지 통화 기준
    current_price: Optional[Decimal] = None  # 현지 통화 기준
    currency: str = "KRW"
    purchase_exchange_rate: Optional[Decimal] = None  # 매입 시 환율
    current_exchange_rate: Optional[Decimal] = None  # 현재 환율
    krw_amount: Optional[Decimal] = None  # 원화 환산 금액
    exchange_gain_loss: Optional[Decimal] = None  # 환차손익
    memo: Optional[str] = None

    def validate(self) -> bool:
        """데이터 유효성 검증"""
        if not self.type:
            raise ValueError("투자 유형은 필수입니다.")
        if not self.name:
            raise ValueError("투자 상품명은 필수입니다.")
        if not self.amount or self.amount <= 0:
            raise ValueError("투자 금액은 0보다 커야 합니다.")
        if not self.purchase_date:
            raise ValueError("매수일은 필수입니다.")
        if self.purchase_quantity and self.purchase_quantity <= 0:
            raise ValueError("매수 수량은 0보다 커야 합니다.")
        if self.purchase_price and self.purchase_price <= 0:
            raise ValueError("매수 가격은 0보다 커야 합니다.")
        if self.current_price and self.current_price < 0:
            raise ValueError("현재 가격은 0 이상이어야 합니다.")
        if self.currency != "KRW" and not self.purchase_exchange_rate:
            raise ValueError("외화 자산의 경우 매입 환율은 필수입니다.")
        if self.purchase_exchange_rate and self.purchase_exchange_rate <= 0:
            raise ValueError("환율은 0보다 커야 합니다.")
        return True

    def calculate_krw_amount(self) -> Decimal:
        """원화 환산 금액 계산"""
        if self.currency == "KRW":
            return self.amount
        
        if not self.current_exchange_rate:
            return Decimal('0')
        
        return self.amount * self.current_exchange_rate

    def calculate_exchange_gain_loss(self) -> Decimal:
        """환차손익 계산"""
        if self.currency == "KRW":
            return Decimal('0')
        
        if not (self.purchase_exchange_rate and self.current_exchange_rate):
            return Decimal('0')
        
        original_krw = self.amount * self.purchase_exchange_rate
        current_krw = self.amount * self.current_exchange_rate
        return current_krw - original_krw


@dataclass
class PortfolioData:
    """포트폴리오 데이터 모델"""
    asset_type: str
    amount: Decimal
    currency: str = "KRW"

    def validate(self) -> bool:
        """데이터 유효성 검증
        
        Returns:
            bool: 유효성 검증 결과
        
        Raises:
            ValueError: 유효하지 않은 데이터
        """
        if not self.asset_type:
            raise ValueError("자산 유형은 필수입니다.")
        if not self.amount or self.amount < 0:
            raise ValueError("자산 금액은 0 이상이어야 합니다.")
        return True


@dataclass
class PerformanceData:
    """성과 분석 데이터 모델"""
    date: date
    portfolio_value: Decimal
    investment_return: Decimal
    benchmark_return: Optional[Decimal] = None
    risk_metrics: Optional[dict] = None
    memo: Optional[str] = None

    def validate(self) -> bool:
        """데이터 유효성 검증
        
        Returns:
            bool: 유효성 검증 결과
        
        Raises:
            ValueError: 유효하지 않은 데이터
        """
        if not self.date:
            raise ValueError("날짜는 필수입니다.")
        if not self.portfolio_value or self.portfolio_value < 0:
            raise ValueError("포트폴리오 가치는 0 이상이어야 합니다.")
        if self.benchmark_return and not isinstance(self.benchmark_return, Decimal):
            raise ValueError("벤치마크 수익률은 Decimal 타입이어야 합니다.")
        if self.risk_metrics and not isinstance(self.risk_metrics, dict):
            raise ValueError("위험 지표는 딕셔너리 타입이어야 합니다.")
        return True


@dataclass
class PortfolioAnalysis:
    """포트폴리오 분석 데이터 모델"""
    date: date
    total_value_krw: Decimal
    total_return_rate: Decimal
    asset_allocation: dict  # 자산별 비중
    currency_exposure: dict  # 통화별 비중
    risk_metrics: Optional[dict] = None
    exchange_gain_loss: Optional[dict] = None  # 통화별 환차손익

    def validate(self) -> bool:
        """데이터 유효성 검증"""
        if not self.date:
            raise ValueError("날짜는 필수입니다.")
        if not self.total_value_krw or self.total_value_krw < 0:
            raise ValueError("총 자산 가치는 0 이상이어야 합니다.")
        if not isinstance(self.asset_allocation, dict):
            raise ValueError("자산 배분은 딕셔너리 형태여야 합니다.")
        if not isinstance(self.currency_exposure, dict):
            raise ValueError("통화 익스포저는 딕셔너리 형태여야 합니다.")
        return True 
