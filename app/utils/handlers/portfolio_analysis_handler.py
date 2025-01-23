"""
포트폴리오 분석 데이터 처리를 위한 핸들러
"""
import json
import logging
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, date

logger = logging.getLogger(__name__)


class PortfolioAnalysisHandler:
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결 관리자
        """
        self.db = db_connection
        self._init_table()

    def _init_table(self):
        """포트폴리오 분석 테이블 초기화"""
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        total_value_krw REAL NOT NULL,
                        total_return_rate REAL NOT NULL,
                        asset_allocation TEXT NOT NULL,
                        currency_exposure TEXT NOT NULL,
                        risk_metrics TEXT,
                        exchange_gain_loss TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            logger.info("Portfolio analysis table initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing portfolio analysis table: {e}")
            raise

    def analyze_portfolio(self, investments: List[Dict]) -> Dict:
        """포트폴리오 분석 수행
        
        Args:
            investments: 투자 데이터 목록
        
        Returns:
            Dict: 포트폴리오 분석 결과
        """
        total_value_krw = Decimal('0')
        asset_allocation = {}
        currency_exposure = {}
        exchange_gain_loss = {}
        
        # 전체 포트폴리오 가치 계산 (원화 기준)
        for inv in investments:
            amount = Decimal(str(inv['amount']))
            currency = inv['currency']
            
            # 원화 환산 금액 계산
            if currency == 'KRW':
                krw_amount = amount
            else:
                current_rate = Decimal(str(inv['current_exchange_rate']))
                krw_amount = amount * current_rate
            
            total_value_krw += krw_amount
            
            # 자산 유형별 비중 계산
            asset_type = inv['type']
            if asset_type not in asset_allocation:
                asset_allocation[asset_type] = Decimal('0')
            asset_allocation[asset_type] += krw_amount
            
            # 통화별 비중 계산
            if currency not in currency_exposure:
                currency_exposure[currency] = Decimal('0')
            currency_exposure[currency] += krw_amount
            
            # 환차손익 계산
            if currency != 'KRW':
                purchase_rate = Decimal(str(inv['purchase_exchange_rate']))
                original_krw = amount * purchase_rate
                current_krw = amount * current_rate
                gain_loss = current_krw - original_krw
                
                if currency not in exchange_gain_loss:
                    exchange_gain_loss[currency] = Decimal('0')
                exchange_gain_loss[currency] += gain_loss
        
        # 비중을 퍼센트로 변환
        for asset_type in asset_allocation:
            asset_allocation[asset_type] = (
                asset_allocation[asset_type] / total_value_krw * 100
            )
        
        for currency in currency_exposure:
            currency_exposure[currency] = (
                currency_exposure[currency] / total_value_krw * 100
            )
        
        return {
            'date': datetime.now().date().isoformat(),
            'total_value_krw': float(total_value_krw),
            'asset_allocation': {k: float(v) for k, v in asset_allocation.items()},
            'currency_exposure': {k: float(v) for k, v in currency_exposure.items()},
            'exchange_gain_loss': {k: float(v) for k, v in exchange_gain_loss.items()}
        }

    def save(self, data: Dict) -> bool:
        """포트폴리오 분석 데이터 저장
        
        Args:
            data: 저장할 포트폴리오 분석 데이터
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            logger.info(f"Saving portfolio analysis data: {data}")
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO portfolio_analysis (
                        date, total_value_krw, total_return_rate,
                        asset_allocation, currency_exposure,
                        risk_metrics, exchange_gain_loss
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['date'],
                    data['total_value_krw'],
                    data.get('total_return_rate', 0),
                    json.dumps(data['asset_allocation']),
                    json.dumps(data['currency_exposure']),
                    json.dumps(data.get('risk_metrics', {})),
                    json.dumps(data.get('exchange_gain_loss', {}))
                ))
                conn.commit()
            logger.info("Portfolio analysis data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving portfolio analysis data: {e}")
            return False

    def load(self, start_date: Optional[str] = None,
             end_date: Optional[str] = None) -> List[Dict]:
        """포트폴리오 분석 데이터 조회
        
        Args:
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        
        Returns:
            List[Dict]: 포트폴리오 분석 데이터 목록
        """
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, date, total_value_krw, total_return_rate,
                           asset_allocation, currency_exposure,
                           risk_metrics, exchange_gain_loss,
                           created_at, updated_at
                    FROM portfolio_analysis
                """
                params = []
                
                if start_date and end_date:
                    query += " WHERE date BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
                elif start_date:
                    query += " WHERE date >= ?"
                    params.append(start_date)
                elif end_date:
                    query += " WHERE date <= ?"
                    params.append(end_date)
                
                query += " ORDER BY date DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    result.append({
                        "id": row[0],
                        "date": row[1],
                        "total_value_krw": row[2],
                        "total_return_rate": row[3],
                        "asset_allocation": json.loads(row[4]),
                        "currency_exposure": json.loads(row[5]),
                        "risk_metrics": json.loads(row[6]) if row[6] else {},
                        "exchange_gain_loss": json.loads(row[7]) if row[7] else {},
                        "created_at": row[8],
                        "updated_at": row[9]
                    })
                
                return result
        except Exception as e:
            logger.error(f"Error loading portfolio analysis data: {e}")
            return [] 
