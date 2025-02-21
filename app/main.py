import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import pandas as pd
from pages.income_expense import render_income_expense_page
from pages.budget import render_budget_page
from pages.investments import render_investments_page
from pages.portfolio import render_portfolio_page
from utils.data_handler import FinanceDataHandler

# 페이지 기본 설정
st.set_page_config(
    page_title="Personal Finance Portfolio",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 핸들러 초기화
def get_data_handler() -> FinanceDataHandler:
    """데이터 핸들러 인스턴스 반환"""
    if 'data_handler' not in st.session_state:
        st.session_state.data_handler = FinanceDataHandler()
    return st.session_state.data_handler

# 사이드바 네비게이션
def sidebar_nav():
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=[
                "Dashboard", "Income/Expense", "Budget",
                "Investments", "Portfolio"
            ],
            icons=[
                "house", "currency-exchange", "piggy-bank",
                "graph-up", "briefcase"
            ],
            menu_icon="cast",
            default_index=0,
        )
    
    return selected

# 메인 대시보드
def main_dashboard():
    st.title("Personal Finance Dashboard")
    
    data_handler = get_data_handler()
    summary = data_handler.get_monthly_summary()
    
    # 메트릭 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="이번 달 수입",
            value=f"₩{summary['total_income']:,.0f}",
            help="이번 달 총 수입"
        )
    with col2:
        st.metric(
            label="이번 달 지출",
            value=f"₩{summary['total_expenses']:,.0f}",
            help="이번 달 총 지출"
        )
    with col3:
        net_income = summary['net_income']
        st.metric(
            label="순수입",
            value=f"₩{net_income:,.0f}",
            help="이번 달 수입 - 지출"
        )
        # 순수입이 양수/음수인 경우에 따라 다른 아이콘 표시
        if net_income > 0:
            st.markdown("📈 흑자")
        elif net_income < 0:
            st.markdown("📉 적자")
        else:
            st.markdown("➖ 수지균형")
    
    # 자산 분배 차트
    portfolio_data = data_handler.load_portfolio()
    
    if portfolio_data:
        fig = go.Figure(data=[go.Pie(
            labels=list(portfolio_data.keys()),
            values=list(portfolio_data.values()),
            hole=.3
        )])
        fig.update_layout(
            title="자산 분배 현황",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("포트폴리오 데이터가 없습니다. 먼저 자산을 입력해주세요.")
    
    # 수입/지출 내역
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 최근 수입")
        income_data = data_handler.load_income()
        if income_data:
            income_df = pd.DataFrame(income_data)
            st.dataframe(
                income_df.head(),
                use_container_width=True
            )
        else:
            st.info("수입 데이터가 없습니다.")
    
    with col2:
        st.markdown("### 📤 최근 지출")
        expense_data = data_handler.load_expense()
        if expense_data:
            expense_df = pd.DataFrame(expense_data)
            st.dataframe(
                expense_df.head(),
                use_container_width=True
            )
        else:
            st.info("지출 데이터가 없습니다.")

def main():
    selected = sidebar_nav()
    
    if selected == "Dashboard":
        main_dashboard()
    elif selected == "Income/Expense":
        render_income_expense_page()
    elif selected == "Budget":
        render_budget_page()
    elif selected == "Investments":
        render_investments_page()
    elif selected == "Portfolio":
        render_portfolio_page()

if __name__ == "__main__":
    main() 
