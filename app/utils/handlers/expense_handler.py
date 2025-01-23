"""
지출 데이터 처리를 위한 핸들러
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExpenseHandler:
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결 관리자
        """
        self.db = db_connection

    def save(self, data: Dict) -> bool:
        """지출 데이터 저장
        
        Args:
            data: 저장할 지출 데이터
                {
                    'date': str,
                    'category': str,
                    'amount': float,
                    'memo': str
                }
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            logger.info(f"Saving expense data: {data}")
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO expense (date, category, amount, memo)
                    VALUES (?, ?, ?, ?)
                """, (
                    data["date"],
                    data["category"],
                    data["amount"],
                    data.get("memo", "")
                ))
                conn.commit()
            logger.info("Expense data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving expense data: {e}")
            return False

    def load(self, start_date: Optional[str] = None,
             end_date: Optional[str] = None) -> List[Dict]:
        """지출 데이터 조회
        
        Args:
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        
        Returns:
            List[Dict]: 지출 데이터 목록
        """
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM expense"
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
                        "category": row[2],
                        "amount": row[3],
                        "memo": row[4],
                        "created_at": row[5]
                    })
                
                return result
        except Exception as e:
            logger.error(f"Error loading expense data: {e}")
            return []

    def delete(self, expense_id: int) -> bool:
        """지출 데이터 삭제
        
        Args:
            expense_id: 삭제할 지출 데이터 ID
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM expense WHERE id = ?",
                    (expense_id,)
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting expense data: {e}")
            return False

    def update(self, expense_id: int, data: Dict) -> bool:
        """지출 데이터 수정
        
        Args:
            expense_id: 수정할 지출 데이터 ID
            data: 수정할 데이터
                {
                    'date': str,
                    'category': str,
                    'amount': float,
                    'memo': str
                }
        
        Returns:
            bool: 수정 성공 여부
        """
        try:
            with self.db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE expense
                    SET date = ?, category = ?, amount = ?, memo = ?
                    WHERE id = ?
                """, (
                    data["date"],
                    data["category"],
                    data["amount"],
                    data.get("memo", ""),
                    expense_id
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating expense data: {e}")
            return False 
