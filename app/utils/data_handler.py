import sqlite3
import json
from datetime import datetime
import os


class FinanceDataHandler:
    def __init__(self):
        self.db_path = "app/data/finance.db"
        self._init_database()
    
    def reset_database(self):
        """데이터베이스 초기화"""
        try:
            # 기존 데이터베이스 파일 삭제
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            
            # 데이터베이스 재생성
            self._init_database()
            return True
        except Exception as e:
            print(f"Error resetting database: {e}")
            return False
    
    def _init_database(self):
        """데이터베이스 및 테이블 초기화"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 수입 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 지출 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 예산 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(month, category)
            )
        """)
        
        # 투자 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                symbol TEXT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 포트폴리오 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_type TEXT NOT NULL,
                amount REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(asset_type)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_income(self, data: dict) -> bool:
        """수입 데이터 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO income (date, category, amount, memo)
                VALUES (?, ?, ?, ?)
            """, (
                data["date"],
                data["category"],
                data["amount"],
                data.get("memo", "")
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving income: {e}")
            return False
    
    def save_expense(self, data: dict) -> bool:
        """지출 데이터 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
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
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving expense: {e}")
            return False
    
    def save_budget(self, data: dict) -> bool:
        """예산 데이터 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 기존 예산 삭제
            cursor.execute(
                "DELETE FROM budget WHERE month = ?",
                (data["month"],)
            )
            
            # 새 예산 입력
            for category, amount in data["categories"].items():
                cursor.execute("""
                    INSERT INTO budget (month, category, amount)
                    VALUES (?, ?, ?)
                """, (data["month"], category, amount))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving budget: {e}")
            return False
    
    def save_investment(self, data: dict) -> bool:
        """투자 데이터 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO investment (
                    type, symbol, name, amount, purchase_date, memo
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["type"],
                data.get("symbol", ""),
                data["name"],
                data["amount"],
                data["purchase_date"],
                data.get("memo", "")
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving investment: {e}")
            return False
    
    def save_portfolio(self, data: dict) -> bool:
        """포트폴리오 데이터 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for asset_type, amount in data.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO portfolio (
                        asset_type, amount, updated_at
                    )
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (asset_type, amount))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving portfolio: {e}")
            return False
    
    def delete_income(self, id: int) -> bool:
        """수입 데이터 삭제"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM income WHERE id = ?",
                (id,)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting income: {e}")
            return False
    
    def delete_expense(self, id: int) -> bool:
        """지출 데이터 삭제"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM expense WHERE id = ?",
                (id,)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
    
    def delete_investment(self, id: int) -> bool:
        """투자 데이터 삭제"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM investment WHERE id = ?",
                (id,)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting investment: {e}")
            return False
    
    def update_income(self, id: int, data: dict) -> bool:
        """수입 데이터 수정"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE income
                SET date = ?, category = ?, amount = ?, memo = ?
                WHERE id = ?
            """, (
                data["date"],
                data["category"],
                data["amount"],
                data.get("memo", ""),
                id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating income: {e}")
            return False
    
    def update_expense(self, id: int, data: dict) -> bool:
        """지출 데이터 수정"""
        try:
            conn = sqlite3.connect(self.db_path)
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
                id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating expense: {e}")
            return False
    
    def update_investment(self, id: int, data: dict) -> bool:
        """투자 데이터 수정"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE investment
                SET type = ?, symbol = ?, name = ?, 
                    amount = ?, purchase_date = ?, memo = ?
                WHERE id = ?
            """, (
                data["type"],
                data.get("symbol", ""),
                data["name"],
                data["amount"],
                data["purchase_date"],
                data.get("memo", ""),
                id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating investment: {e}")
            return False
    
    def load_income(self, start_date=None, end_date=None) -> list:
        """수입 데이터 로드"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT id, date, category, amount, memo FROM income"
            params = []
            
            if start_date and end_date:
                query += " WHERE date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
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
                    "memo": row[4]
                })
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error loading income: {e}")
            return []
    
    def load_expense(self, start_date=None, end_date=None) -> list:
        """지출 데이터 로드"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT id, date, category, amount, memo FROM expense"
            params = []
            
            if start_date and end_date:
                query += " WHERE date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
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
                    "memo": row[4]
                })
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error loading expense: {e}")
            return []
    
    def load_budget(self, month=None) -> dict:
        """예산 데이터 로드"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT month, category, amount
                FROM budget
            """
            params = []
            
            if month:
                query += " WHERE month = ?"
                params.append(month)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            result = {}
            for row in rows:
                month = row[0]
                if month not in result:
                    result[month] = {
                        "categories": {},
                        "total": 0
                    }
                result[month]["categories"][row[1]] = row[2]
                result[month]["total"] += row[2]
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error loading budget: {e}")
            return {}
    
    def load_investment(self) -> dict:
        """투자 데이터 로드"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, type, symbol, name, amount, purchase_date, memo
                FROM investment
                ORDER BY purchase_date DESC
            """)
            rows = cursor.fetchall()
            
            result = {}
            for row in rows:
                result[row[0]] = {
                    "type": row[1],
                    "symbol": row[2],
                    "name": row[3],
                    "amount": row[4],
                    "purchase_date": row[5],
                    "memo": row[6]
                }
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error loading investment: {e}")
            return {}
    
    def load_portfolio(self) -> dict:
        """포트폴리오 데이터 로드"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT asset_type, amount
                FROM portfolio
                ORDER BY asset_type
            """)
            rows = cursor.fetchall()
            
            result = {}
            for row in rows:
                result[row[0]] = row[1]
            
            conn.close()
            return result
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return {}

    def get_monthly_summary(self, year_month: str = None) -> dict:
        """월간 재무 요약 정보 반환"""
        if year_month is None:
            year_month = datetime.now().strftime("%Y-%m")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 월간 수입 합계
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM income
                WHERE date LIKE ?
            """, (f"{year_month}%",))
            total_income = cursor.fetchone()[0]
            
            # 월간 지출 합계
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM expense
                WHERE date LIKE ?
            """, (f"{year_month}%",))
            total_expenses = cursor.fetchone()[0]
            
            # 투자 총액
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM investment
            """)
            total_investments = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "total_investments": total_investments,
                "net_income": total_income - total_expenses
            }
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return {
                "total_income": 0,
                "total_expenses": 0,
                "total_investments": 0,
                "net_income": 0
            } 
