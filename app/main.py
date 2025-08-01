import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import pandas as pd
from pages.income_expense import render_income_expense_page
from pages.budget import render_budget_page
from pages.investments import render_investments_page
from pages.portfolio import render_portfolio_page
from utils.data_handler import FinanceDataHandler
from config.settings import Settings, UIConfig
from utils.logger import setup_logger
from utils.error_handler import ErrorHandler

# 로깅 설정
logger = setup_logger(
    name="finance_app",
    log_level=Settings.LOG_LEVEL,
    log_file=Settings.LOG_FILE
)

# 페이지 기본 설정
st.set_page_config(
    page_title=Settings.PAGE_TITLE,
    page_icon=Settings.PAGE_ICON,
    layout=Settings.LAYOUT,
    initial_sidebar_state=Settings.SIDEBAR_STATE
)

# 데이터 핸들러 초기화
# 데이터 핸들러를 반환하는 함수입니다.
def get_data_handler() -> FinanceDataHandler:
    """데이터 핸들러 인스턴스 반환"""
    if 'data_handler' not in st.session_state:
        st.session_state.data_handler = FinanceDataHandler()
    return st.session_state.data_handler

# 사이드바 네비게이션을 설정하는 함수입니다.
def sidebar_nav():
    menu_config = UIConfig.get_menu_config()
    
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=menu_config['options'],
            icons=menu_config['icons'],
            menu_icon="cast",
            default_index=0,
        )
    
    return selected

# 메인 대시보드를 렌더링하는 함수입니다.
def main_dashboard():
    st.title("Personal Finance Dashboard")
    
    data_handler = get_data_handler()
    summary = data_handler.get_monthly_summary()
    
    # 상단 컨테이너 - 메트릭 표시
    with st.container():
        st.markdown("### 📊 월간 재무 현황")
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
                st.markdown("📈 흑자", help="수입이 지출보다 많습니다")
            elif net_income < 0:
                st.markdown("📉 적자", help="지출이 수입보다 많습니다")
            else:
                st.markdown("➖ 수지균형", help="수입과 지출이 같습니다")
    
    st.markdown("---")
    
    # 중간 컨테이너 - 자산 분배 현황
    with st.container():
        portfolio_data = data_handler.load_portfolio()
        
        if portfolio_data:
            col1, col2 = st.columns([2, 1])  # 2:1 비율로 분할
            
            with col1:
                st.markdown("### 📈 자산 분배 현황")
                # 원화로 환산된 자산 금액 계산
                asset_values = {}
                for asset_type, details in portfolio_data.items():
                    amount = float(details.get('amount', 0))
                    currency = details.get('currency', 'KRW')
                    
                    if currency == 'USD':
                        # USD 자산은 현재 환율로 환산
                        exchange_rate = data_handler.get_current_exchange_rate()
                        krw_amount = amount * exchange_rate
                    else:
                        krw_amount = amount
                    
                    asset_values[asset_type] = krw_amount
                
                # 총 자산 계산
                total_assets = sum(asset_values.values())
                
                # 비중 계산 (소수점 1자리까지)
                weights = {
                    k: round(v / total_assets * 100, 1)
                    for k, v in asset_values.items()
                }
                
                # 파이 차트 생성
                fig = go.Figure(data=[go.Pie(
                    labels=list(weights.keys()),
                    values=list(weights.values()),
                    hole=.3,
                    textinfo='label+percent',
                    textposition='inside',
                    showlegend=True
                )])
                
                fig.update_layout(
                    margin=dict(t=0, l=0, r=0, b=0),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    height=350
                )
                
                # 차트 표시
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 💰 자산 현황")
                # 총 자산 표시
                st.metric(
                    "총 자산",
                    f"₩{total_assets:,.0f}",
                    help="전체 자산의 원화 환산 금액"
                )
                
                # 자산 금액 테이블 표시
                asset_df = pd.DataFrame({
                    '자산 유형': list(asset_values.keys()),
                    '평가금액': [f"₩{v:,.0f}" for v in asset_values.values()],
                    '비중': [f"{weights[k]:.1f}%" for k in asset_values.keys()]
                }).set_index('자산 유형')
                
                st.dataframe(
                    asset_df,
                    use_container_width=True,
                    height=250
                )
        else:
            st.info("포트폴리오 데이터가 없습니다. 먼저 자산을 입력해주세요.")
    
    st.markdown("---")
    
    # 하단 컨테이너 - 수입/지출 내역
    with st.container():
        st.markdown("### 📋 최근 거래 내역")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📥 최근 수입")
            income_data = data_handler.load_income()
            if income_data:
                income_df = pd.DataFrame(income_data)
                st.dataframe(
                    income_df.head(),
                    use_container_width=True,
                    height=200
                )
            else:
                st.info("수입 데이터가 없습니다.")
        
        with col2:
            st.markdown("#### 📤 최근 지출")
            expense_data = data_handler.load_expense()
            if expense_data:
                expense_df = pd.DataFrame(expense_data)
                st.dataframe(
                    expense_df.head(),
                    use_container_width=True,
                    height=200
                )
            else:
                st.info("지출 데이터가 없습니다.")

# 애플리케이션의 진입점입니다.
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
