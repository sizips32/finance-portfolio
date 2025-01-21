import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import pandas as pd
from pages.income_expense import render_income_expense_page
from pages.budget import render_budget_page
from pages.investments import render_investments_page
from pages.portfolio import render_portfolio_page

# 페이지 기본 설정
st.set_page_config(
    page_title="Personal Finance Portfolio",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    # 샘플 데이터 생성 (실제 구현시 데이터베이스에서 가져올 예정)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Assets",
            value="₩50,000,000",
            delta="1,200,000",
            help="총 자산"
        )
    with col2:
        st.metric(
            label="Monthly Income",
            value="₩5,000,000",
            delta="200,000",
            help="월간 수입"
        )
    with col3:
        st.metric(
            label="Monthly Expenses",
            value="₩3,000,000",
            delta="-150,000",
            help="월간 지출"
        )
    
    # 자산 분배 차트
    fig = go.Figure(data=[go.Pie(
        labels=['주식', '채권', '현금', '부동산'],
        values=[35, 25, 20, 20],
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
    
    # 수입/지출 트렌드
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='ME')
    income = [5000000, 5200000, 5000000]
    expenses = [3000000, 3150000, 3000000]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=dates,
        y=income,
        name="수입",
        line=dict(color='#28a745', width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=dates,
        y=expenses,
        name="지출",
        line=dict(color='#dc3545', width=2)
    ))
    fig2.update_layout(
        title="수입/지출 트렌드",
        xaxis_title="날짜",
        yaxis_title="금액 (원)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # 최근 거래 내역
    st.markdown("### 📋 최근 거래 내역")
    
    transactions = pd.DataFrame({
        "날짜": ["2024-03-15", "2024-03-14", "2024-03-13", "2024-03-12"],
        "구분": ["지출", "수입", "지출", "지출"],
        "카테고리": ["식비", "급여", "교통", "여가"],
        "금액": [-50000, 5000000, -30000, -100000],
        "메모": ["점심식사", "3월 급여", "택시비", "영화관람"]
    })
    
    # 금액에 따라 색상 지정
    def color_amount(val):
        color = '#28a745' if val > 0 else '#dc3545'
        return f'color: {color}'
    
    # 금액 포맷팅
    def format_amount(val):
        return f"₩{abs(val):,.0f}"
    
    # 스타일이 적용된 데이터프레임 표시
    st.dataframe(
        transactions.style.format({
            "금액": format_amount
        }).map(
            color_amount,
            subset=["금액"]
        ),
        use_container_width=True
    )

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
