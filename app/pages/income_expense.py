import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.data_handler import FinanceDataHandler
from utils.visualization import create_income_expense_chart, create_pie_chart


def render_income_expense_page():
    st.title("💰 수입/지출 관리")
    
    # 데이터 핸들러 초기화
    data_handler = FinanceDataHandler()
    
    # 탭 생성
    tab1, tab2 = st.tabs(["💳 입력", "📊 분석"])
    
    with tab1:
        # 입력 폼을 카드 스타일로 표시
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container():
                st.markdown("### ⬆️ 수입 입력")
                with st.form("income_form"):
                    income_date = st.date_input(
                        "수입 날짜",
                        value=datetime.now(),
                        key="income_date"
                    )
                    
                    income_category = st.selectbox(
                        "수입 분류",
                        ["급여", "투자수익", "부수입", "기타"],
                        key="income_category"
                    )
                    
                    income_amount = st.number_input(
                        "금액",
                        min_value=0,
                        value=0,
                        step=10000,
                        key="income_amount",
                        help="수입 금액을 입력하세요"
                    )
                    
                    income_memo = st.text_area(
                        "메모",
                        key="income_memo",
                        height=100
                    )
                    
                    submit_income = st.form_submit_button(
                        "수입 저장",
                        use_container_width=True
                    )
                    
                    if submit_income:
                        income_data = {
                            "date": income_date.strftime("%Y-%m-%d"),
                            "category": income_category,
                            "amount": income_amount,
                            "memo": income_memo
                        }
                        if data_handler.save_income(income_data):
                            st.success("✅ 수입이 저장되었습니다.")
                        else:
                            st.error("❌ 수입 저장에 실패했습니다.")
        
        with col2:
            with st.container():
                st.markdown("### ⬇️ 지출 입력")
                with st.form("expense_form"):
                    expense_date = st.date_input(
                        "지출 날짜",
                        value=datetime.now(),
                        key="expense_date"
                    )
                    
                    expense_category = st.selectbox(
                        "지출 분류",
                        [
                            "식비", "교통", "주거", "통신",
                            "의료", "교육", "여가", "기타"
                        ],
                        key="expense_category"
                    )
                    
                    expense_amount = st.number_input(
                        "금액",
                        min_value=0,
                        value=0,
                        step=1000,
                        key="expense_amount",
                        help="지출 금액을 입력하세요"
                    )
                    
                    expense_memo = st.text_area(
                        "메모",
                        key="expense_memo",
                        height=100
                    )
                    
                    submit_expense = st.form_submit_button(
                        "지출 저장",
                        use_container_width=True
                    )
                    
                    if submit_expense:
                        expense_data = {
                            "date": expense_date.strftime("%Y-%m-%d"),
                            "category": expense_category,
                            "amount": expense_amount,
                            "memo": expense_memo
                        }
                        if data_handler.save_expense(expense_data):
                            st.success("✅ 지출이 저장되었습니다.")
                        else:
                            st.error("❌ 지출 저장에 실패했습니다.")
    
    with tab2:
        st.markdown("### 📈 수입/지출 분석")
        
        # 기간 선택
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "시작일",
                value=datetime.now() - timedelta(days=30)
            )
        with col2:
            end_date = st.date_input(
                "종료일",
                value=datetime.now()
            )
        
        # 데이터 로드
        income_data = data_handler.load_income()
        expense_data = data_handler.load_expense()
        
        if income_data and expense_data:
            # 데이터프레임 생성
            income_df = pd.DataFrame(income_data)
            expense_df = pd.DataFrame(expense_data)
            
            # 요약 통계
            col1, col2, col3 = st.columns(3)
            
            total_income = income_df["amount"].sum()
            total_expense = expense_df["amount"].sum()
            balance = total_income - total_expense
            
            with col1:
                st.metric(
                    "📈 총 수입",
                    f"₩{total_income:,.0f}",
                    delta=f"₩{total_income/30:,.0f}/일"
                )
            
            with col2:
                st.metric(
                    "📉 총 지출",
                    f"₩{total_expense:,.0f}",
                    delta=f"₩{total_expense/30:,.0f}/일"
                )
            
            with col3:
                st.metric(
                    "💰 수지 균형",
                    f"₩{balance:,.0f}",
                    delta="흑자" if balance > 0 else "적자"
                )
            
            # 차트 섹션
            st.markdown("### 📊 차트 분석")
            
            # 수입/지출 트렌드
            dates = pd.date_range(start=start_date, end=end_date)
            income_series = income_df.groupby("date")["amount"].sum()
            expense_series = expense_df.groupby("date")["amount"].sum()
            
            trend_chart = create_income_expense_chart(
                dates=dates,
                income=income_series.values,
                expenses=expense_series.values
            )
            st.plotly_chart(trend_chart, use_container_width=True)
            
            # 카테고리별 분석
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 수입 카테고리 분석")
                income_by_category = income_df.groupby(
                    "category"
                )["amount"].sum()
                
                income_pie = create_pie_chart(
                    labels=income_by_category.index.tolist(),
                    values=income_by_category.values.tolist(),
                    title="수입 카테고리 분포"
                )
                st.plotly_chart(income_pie, use_container_width=True)
            
            with col2:
                st.markdown("#### 지출 카테고리 분석")
                expense_by_category = expense_df.groupby(
                    "category"
                )["amount"].sum()
                
                expense_pie = create_pie_chart(
                    labels=expense_by_category.index.tolist(),
                    values=expense_by_category.values.tolist(),
                    title="지출 카테고리 분포"
                )
                st.plotly_chart(expense_pie, use_container_width=True)
            
            # 상세 내역 테이블
            st.markdown("### 📋 상세 내역")
            
            show_details = st.checkbox("상세 내역 보기")
            
            if show_details:
                tab1, tab2 = st.tabs(["수입 내역", "지출 내역"])
                
                with tab1:
                    if not income_df.empty:
                        income_df_display = income_df.copy()
                        income_df_display["date"] = pd.to_datetime(
                            income_df_display["date"]
                        )
                        income_df_display = income_df_display.sort_values(
                            "date",
                            ascending=False
                        )
                        st.dataframe(
                            income_df_display,
                            use_container_width=True
                        )
                    else:
                        st.info("수입 내역이 없습니다.")
                
                with tab2:
                    if not expense_df.empty:
                        expense_df_display = expense_df.copy()
                        expense_df_display["date"] = pd.to_datetime(
                            expense_df_display["date"]
                        )
                        expense_df_display = expense_df_display.sort_values(
                            "date",
                            ascending=False
                        )
                        st.dataframe(
                            expense_df_display,
                            use_container_width=True
                        )
                    else:
                        st.info("지출 내역이 없습니다.")
        else:
            st.info("💡 데이터가 없습니다. 먼저 수입/지출을 입력해주세요.") 
