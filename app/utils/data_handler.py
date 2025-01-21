import pandas as pd
from pathlib import Path
from typing import Dict, List, Union, Optional
import json


class FinanceDataHandler:
    def __init__(self, data_dir: str = "data"):
        """데이터 핸들러 초기화"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 기본 파일 경로 설정
        self.income_file = self.data_dir / "income.json"
        self.expenses_file = self.data_dir / "expenses.json"
        self.investments_file = self.data_dir / "investments.json"
        self.budget_file = self.data_dir / "budget.json"
        
        # 필요한 파일들이 없다면 생성
        self._initialize_files()
    
    def _initialize_files(self):
        """필요한 데이터 파일들을 초기화"""
        files = [
            self.income_file,
            self.expenses_file,
            self.investments_file,
            self.budget_file
        ]
        
        for file in files:
            if not file.exists():
                file.write_text("{}")
    
    def save_income(self, data: Dict) -> bool:
        """수입 데이터 저장"""
        try:
            with open(self.income_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving income data: {e}")
            return False
    
    def save_expense(self, data: Dict) -> bool:
        """지출 데이터 저장"""
        try:
            with open(self.expenses_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving expense data: {e}")
            return False
    
    def save_investment(self, data: Dict) -> bool:
        """투자 데이터 저장"""
        try:
            with open(self.investments_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving investment data: {e}")
            return False
    
    def save_budget(self, data: Dict) -> bool:
        """예산 데이터 저장"""
        try:
            with open(self.budget_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving budget data: {e}")
            return False
    
    def load_income(self) -> Dict:
        """수입 데이터 로드"""
        try:
            with open(self.income_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading income data: {e}")
            return {}
    
    def load_expense(self) -> Dict:
        """지출 데이터 로드"""
        try:
            with open(self.expenses_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading expense data: {e}")
            return {}
    
    def load_investment(self) -> Dict:
        """투자 데이터 로드"""
        try:
            with open(self.investments_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading investment data: {e}")
            return {}
    
    def load_budget(self) -> Dict:
        """예산 데이터 로드"""
        try:
            with open(self.budget_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading budget data: {e}")
            return {}
    
    def get_monthly_summary(self) -> Dict:
        """월간 재무 요약 정보 반환"""
        income = self.load_income()
        expenses = self.load_expense()
        investments = self.load_investment()
        
        # 여기에 월간 요약 계산 로직 추가
        return {
            "total_income": sum(income.values()) if income else 0,
            "total_expenses": sum(expenses.values()) if expenses else 0,
            "total_investments": sum(investments.values()) if investments else 0
        } 
