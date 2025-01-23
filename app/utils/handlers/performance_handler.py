"""
성과 분석 데이터 처리를 위한 핸들러
"""
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PerformanceHandler:
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결 관리자
        """
        self.db = db_connection
        self._init_table()

    def _init_table(self):
        """성과 분석 테이블 초기화"""
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        portfolio_value REAL NOT NULL,
                        investment_return REAL NOT NULL,
                        benchmark_return REAL,
                        risk_metrics TEXT,
                        memo TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            logger.info("Performance table initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing performance table: {e}")
            raise

    def save(self, data: Dict) -> bool:
        """성과 분석 데이터 저장
        
        Args:
            data: 저장할 성과 분석 데이터
                {
                    'date': str,
                    'portfolio_value': float,
                    'investment_return': float,
                    'benchmark_return': float,
                    'risk_metrics': dict,
                    'memo': str
                }
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            logger.info(f"Saving performance data: {data}")
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO performance (
                        date, portfolio_value, investment_return,
                        benchmark_return, risk_metrics, memo
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    data["date"],
                    data["portfolio_value"],
                    data["investment_return"],
                    data.get("benchmark_return"),
                    json.dumps(data.get("risk_metrics", {})),
                    data.get("memo", "")
                ))
                conn.commit()
            logger.info("Performance data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")
            return False

    def load(self, start_date: Optional[str] = None,
             end_date: Optional[str] = None) -> List[Dict]:
        """성과 분석 데이터 조회
        
        Args:
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        
        Returns:
            List[Dict]: 성과 분석 데이터 목록
        """
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, date, portfolio_value, investment_return,
                           benchmark_return, risk_metrics, memo,
                           created_at, updated_at
                    FROM performance
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
                        "portfolio_value": row[2],
                        "investment_return": row[3],
                        "benchmark_return": row[4],
                        "risk_metrics": json.loads(row[5]) if row[5] else {},
                        "memo": row[6],
                        "created_at": row[7],
                        "updated_at": row[8]
                    })
                
                return result
        except Exception as e:
            logger.error(f"Error loading performance data: {e}")
            return []

    def delete(self, performance_id: int) -> bool:
        """성과 분석 데이터 삭제
        
        Args:
            performance_id: 삭제할 성과 분석 데이터 ID
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM performance WHERE id = ?",
                    (performance_id,)
                )
                conn.commit()
            logger.info(f"Performance data {performance_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting performance data: {e}")
            return False

    def update(self, performance_id: int, data: Dict) -> bool:
        """성과 분석 데이터 수정
        
        Args:
            performance_id: 수정할 성과 분석 데이터 ID
            data: 수정할 데이터
                {
                    'date': str,
                    'portfolio_value': float,
                    'investment_return': float,
                    'benchmark_return': float,
                    'risk_metrics': dict,
                    'memo': str
                }
        
        Returns:
            bool: 수정 성공 여부
        """
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE performance
                    SET date = ?,
                        portfolio_value = ?,
                        investment_return = ?,
                        benchmark_return = ?,
                        risk_metrics = ?,
                        memo = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    data["date"],
                    data["portfolio_value"],
                    data["investment_return"],
                    data.get("benchmark_return"),
                    json.dumps(data.get("risk_metrics", {})),
                    data.get("memo", ""),
                    performance_id
                ))
                conn.commit()
            logger.info(f"Performance data {performance_id} updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating performance data: {e}")
            return False 
