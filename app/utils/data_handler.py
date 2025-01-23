from contextlib import contextmanager
import sqlite3
from datetime import datetime
import os
import logging

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 파일 핸들러 설정
log_dir = "app/logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(f"{log_dir}/finance.log")
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)

class FinanceDataHandler:
    def __init__(self):
        self.db_path = "app/data/finance.db"
        self._init_database()
        self._migrate_database()
    
    @contextmanager
    def get_db_connection(self):
        """데이터베이스 연결을 관리하는 컨텍스트 매니저"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """데이터베이스 및 테이블 초기화"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            logger.info("Initializing database tables...")
            
            with self.get_db_connection() as conn:
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
                logger.debug("Income table created/verified")
                
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
                        purchase_quantity REAL,
                        purchase_price REAL,
                        current_price REAL,
                        currency TEXT DEFAULT 'KRW',
                        amount REAL NOT NULL,
                        current_amount REAL,
                        purchase_exchange_rate REAL,
                        current_exchange_rate REAL,
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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(asset_type)
                    )
                """)
                
                conn.commit()
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _migrate_database(self):
        """데이터베이스 마이그레이션"""
        try:
            logger.info("Starting database migration...")
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # investment 테이블 마이그레이션
                cursor.execute("PRAGMA table_info(investment)")
                columns = [column[1] for column in cursor.fetchall()]
                
                migrations_applied = 0
                
                # updated_at 컬럼 추가
                if 'updated_at' not in columns:
                    cursor.execute("""
                        ALTER TABLE investment
                        ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    """)
                    migrations_applied += 1
                    logger.debug("Added updated_at column to investment table")
                
                # portfolio 테이블 마이그레이션
                cursor.execute("PRAGMA table_info(portfolio)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # currency 컬럼 추가
                if 'currency' not in columns:
                    cursor.execute("""
                        ALTER TABLE portfolio
                        ADD COLUMN currency TEXT DEFAULT 'KRW'
                    """)
                
                # purchase_exchange_rate 컬럼 추가
                if 'purchase_exchange_rate' not in columns:
                    cursor.execute("""
                        ALTER TABLE portfolio
                        ADD COLUMN purchase_exchange_rate REAL
                    """)
                
                # updated_at 컬럼 추가
                if 'updated_at' not in columns:
                    cursor.execute("""
                        ALTER TABLE portfolio
                        ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    """)
                
                conn.commit()
                logger.info(f"Database migration completed. Applied {migrations_applied} changes.")
        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            raise
    
    def save_income(self, data: dict) -> bool:
        """수입 데이터 저장"""
        try:
            logger.info(f"Saving income data: {data}")
            with self.get_db_connection() as conn:
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
            logger.info("Income data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving income data: {e}")
            return False
    
    def save_expense(self, data: dict) -> bool:
        """지출 데이터 저장"""
        try:
            with self.get_db_connection() as conn:
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
            return True
        except Exception as e:
            print(f"Error saving expense: {e}")
            return False
    
    def save_budget(self, data: dict) -> bool:
        """예산 데이터 저장"""
        try:
            with self.get_db_connection() as conn:
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
            return True
        except Exception as e:
            print(f"Error saving budget: {e}")
            return False
    
    def save_investment(self, data: dict) -> bool:
        """투자 데이터 저장 또는 업데이트"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 동일한 종목이 있는지 확인
                cursor.execute("""
                    SELECT id FROM investment
                    WHERE symbol = ? AND type = ?
                """, (data.get("symbol", ""), data["type"]))
                
                existing_id = cursor.fetchone()
                
                if existing_id:
                    # 기존 데이터 업데이트
                    cursor.execute("""
                        UPDATE investment SET
                            name = ?,
                            purchase_quantity = ?,
                            purchase_price = ?,
                            current_price = ?,
                            currency = ?,
                            amount = ?,
                            current_amount = ?,
                            purchase_exchange_rate = ?,
                            current_exchange_rate = ?,
                            purchase_date = ?,
                            memo = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (
                        data["name"],
                        data.get("purchase_quantity", 0),
                        data.get("purchase_price", 0),
                        data.get("current_price", 0),
                        data.get("currency", "KRW"),
                        data["amount"],
                        data.get("current_amount", data["amount"]),
                        data.get("purchase_exchange_rate", None),
                        data.get("current_exchange_rate", None),
                        data["purchase_date"],
                        data.get("memo", ""),
                        existing_id[0]
                    ))
                else:
                    # 새로운 데이터 추가
                    cursor.execute("""
                        INSERT INTO investment (
                            type, symbol, name, purchase_quantity, purchase_price,
                            current_price, currency, amount, current_amount,
                            purchase_exchange_rate, current_exchange_rate,
                            purchase_date, memo
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data["type"],
                        data.get("symbol", ""),
                        data["name"],
                        data.get("purchase_quantity", 0),
                        data.get("purchase_price", 0),
                        data.get("current_price", 0),
                        data.get("currency", "KRW"),
                        data["amount"],
                        data.get("current_amount", data["amount"]),
                        data.get("purchase_exchange_rate", None),
                        data.get("current_exchange_rate", None),
                        data["purchase_date"],
                        data.get("memo", "")
                    ))
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving investment: {e}")
            return False
    
    def save_portfolio(self, data: dict) -> bool:
        """포트폴리오 데이터 저장"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                for asset_type, asset_data in data.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO portfolio (
                            asset_type, currency, amount,
                            purchase_exchange_rate, updated_at
                        )
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        asset_type,
                        asset_data.get('currency', 'KRW'),
                        asset_data['amount'],
                        asset_data.get('purchase_exchange_rate', None)
                    ))
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving portfolio: {e}")
            return False
    
    def delete_income(self, id: int) -> bool:
        """수입 데이터 삭제"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM income WHERE id = ?",
                    (id,)
                )
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting income: {e}")
            return False
    
    def delete_expense(self, id: int) -> bool:
        """지출 데이터 삭제"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM expense WHERE id = ?",
                    (id,)
                )
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
    
    def delete_investment(self, id: int) -> bool:
        """투자 데이터 삭제"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "DELETE FROM investment WHERE id = ?",
                    (id,)
                )
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting investment: {e}")
            return False
    
    def update_income(self, id: int, data: dict) -> bool:
        """수입 데이터 수정"""
        try:
            with self.get_db_connection() as conn:
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
            return True
        except Exception as e:
            print(f"Error updating income: {e}")
            return False
    
    def update_expense(self, id: int, data: dict) -> bool:
        """지출 데이터 수정"""
        try:
            with self.get_db_connection() as conn:
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
            return True
        except Exception as e:
            print(f"Error updating expense: {e}")
            return False
    
    def update_investment(self, id: int, data: dict) -> bool:
        """투자 데이터 수정"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE investment
                    SET type = ?, symbol = ?, name = ?, 
                        purchase_quantity = ?, purchase_price = ?,
                        current_price = ?, currency = ?, 
                        amount = ?, current_amount = ?,
                        purchase_exchange_rate = ?, current_exchange_rate = ?,
                        purchase_date = ?, memo = ?
                    WHERE id = ?
                """, (
                    data["type"],
                    data.get("symbol", ""),
                    data["name"],
                    data.get("purchase_quantity", 0),
                    data.get("purchase_price", 0),
                    data.get("current_price", 0),
                    data.get("currency", "KRW"),
                    data["amount"],
                    data.get("current_amount", data["amount"]),
                    data.get("purchase_exchange_rate", None),
                    data.get("current_exchange_rate", None),
                    data["purchase_date"],
                    data.get("memo", ""),
                    id
                ))
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error updating investment: {e}")
            return False
    
    def update_investment_price(
        self,
        id: int,
        current_price: float,
        current_amount: float
    ) -> bool:
        """투자 자산의 현재 가격 업데이트"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE investment SET
                        current_price = ?,
                        current_amount = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (current_price, current_amount, id))
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error updating investment price: {e}")
            return False
    
    def load_income(self, start_date=None, end_date=None) -> list:
        """수입 데이터 로드"""
        try:
            with self.get_db_connection() as conn:
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
            
            return result
        except Exception as e:
            print(f"Error loading income: {e}")
            return []
    
    def load_expense(self, start_date=None, end_date=None) -> list:
        """지출 데이터 로드"""
        try:
            with self.get_db_connection() as conn:
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
            
            return result
        except Exception as e:
            print(f"Error loading expense: {e}")
            return []
    
    def load_budget(self, month=None) -> dict:
        """예산 데이터 로드"""
        try:
            with self.get_db_connection() as conn:
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
            
            return result
        except Exception as e:
            print(f"Error loading budget: {e}")
            return {}
    
    def load_investment(self) -> dict:
        """투자 데이터 로드"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        id, type, symbol, name, purchase_quantity,
                        purchase_price, current_price, currency,
                        amount, current_amount, purchase_exchange_rate,
                        current_exchange_rate, purchase_date, memo,
                        created_at, updated_at
                    FROM investment
                    ORDER BY type, name
                """)
                
                columns = [
                    'id', 'type', 'symbol', 'name', 'purchase_quantity',
                    'purchase_price', 'current_price', 'currency',
                    'amount', 'current_amount', 'purchase_exchange_rate',
                    'current_exchange_rate', 'purchase_date', 'memo',
                    'created_at', 'updated_at'
                ]
                
                result = {}
                for row in cursor.fetchall():
                    data = dict(zip(columns, row))
                    result[str(data['id'])] = data
            
            return result
        except Exception as e:
            print(f"Error loading investment data: {e}")
            return {}
    
    def load_portfolio(self) -> dict:
        """포트폴리오 데이터 로드"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        asset_type, currency, amount,
                        purchase_exchange_rate, updated_at
                    FROM portfolio
                    ORDER BY asset_type
                """)
                
                result = {}
                for row in cursor.fetchall():
                    asset_type, currency, amount, exchange_rate, updated_at = row
                    result[asset_type] = {
                        'currency': currency,
                        'amount': amount,
                        'purchase_exchange_rate': exchange_rate,
                        'updated_at': updated_at
                    }
            
            return result
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
            return {}

    def get_monthly_summary(self, year_month: str = None) -> dict:
        """월간 재무 요약 정보 반환"""
        if year_month is None:
            year_month = datetime.now().strftime("%Y-%m")
        
        try:
            with self.get_db_connection() as conn:
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
