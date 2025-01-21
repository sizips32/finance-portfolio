import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_handler import FinanceDataHandler
from utils.visualization import create_budget_progress_chart


def render_budget_page():
    st.title("💵 예산 관리")
    
    # 데이터 핸들러 초기화
    data_handler = FinanceDataHandler()
    
    # 탭 생성
    tab1, tab2 = st.tabs(["📝 예산 설정", "📊 예산 현황"])
    
    with tab1:
        st.markdown("### 월간 예산 설정")
        
        with st.form("budget_form"):
            # 예산 기간 선택
            budget_month = st.date_input(
                "예산 설정 월",
                value=datetime.now(),
                key="budget_month",
                help="예산을 설정할 월을 선택하세요"
            )
            
            st.markdown("#### 카테고리별 예산 입력")
            
            # 카테고리별 예산 입력을 2열로 구성
            col1, col2 = st.columns(2)
            
            # 카테고리 목록
            categories = [
                "식비", "교통", "주거", "통신",
                "의료", "교육", "여가", "기타"
            ]
            
            # 예산 데이터 저장용 딕셔너리
            budget_data = {}
            
            # 왼쪽 열에 카테고리 1~4
            with col1:
                for category in categories[:4]:
                    budget_data[category] = st.number_input(
                        f"{category} 예산",
                        min_value=0,
                        value=0,
                        step=10000,
                        key=f"budget_{category}",
                        help=f"{category}에 대한 월간 예산을 입력하세요"
                    )
            
            # 오른쪽 열에 카테고리 5~8
            with col2:
                for category in categories[4:]:
                    budget_data[category] = st.number_input(
                        f"{category} 예산",
                        min_value=0,
                        value=0,
                        step=10000,
                        key=f"budget_{category}",
                        help=f"{category}에 대한 월간 예산을 입력하세요"
                    )
            
            # 총 예산 계산 및 표시
            total_budget = sum(budget_data.values())
            st.metric(
                "총 예산",
                f"₩{total_budget:,.0f}",
                help="설정된 전체 예산 금액"
            )
            
            # 저장 버튼
            submit_budget = st.form_submit_button(
                "예산 저장",
                use_container_width=True
            )
            
            if submit_budget:
                budget_info = {
                    "month": budget_month.strftime("%Y-%m"),
                    "categories": budget_data,
                    "total": total_budget
                }
                
                if data_handler.save_budget(budget_info):
                    st.success("✅ 예산이 저장되었습니다.")
                else:
                    st.error("❌ 예산 저장에 실패했습니다.")
    
    with tab2:
        st.markdown("### 예산 집행 현황")
        
        # 조회 월 선택
        view_month = st.date_input(
            "조회 월",
            value=datetime.now(),
            key="view_month",
            help="예산 현황을 조회할 월을 선택하세요"
        )
        
        # 예산 및 지출 데이터 로드
        budget_data = data_handler.load_budget()
        expense_data = data_handler.load_expense()
        
        if budget_data and expense_data:
            # 예산 데이터 처리
            month_key = view_month.strftime("%Y-%m")
            
            if month_key in budget_data:
                planned_budget = budget_data[month_key]["categories"]
                total_budget = budget_data[month_key]["total"]
                
                # 지출 데이터 처리
                expense_df = pd.DataFrame(expense_data)
                expense_df["month"] = pd.to_datetime(
                    expense_df["date"]
                ).dt.strftime("%Y-%m")
                
                # 해당 월의 지출만 필터링
                month_expenses = expense_df[
                    expense_df["month"] == month_key
                ]
                actual_expenses = month_expenses.groupby(
                    "category"
                )["amount"].sum()
                
                # 총 지출 계산
                total_expense = actual_expenses.sum()
                
                # 예산 진행 상황 요약
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "💰 총 예산",
                        f"₩{total_budget:,.0f}",
                        help="이번 달 전체 예산"
                    )
                
                with col2:
                    st.metric(
                        "💸 총 지출",
                        f"₩{total_expense:,.0f}",
                        help="이번 달 전체 지출"
                    )
                
                with col3:
                    remaining = total_budget - total_expense
                    progress = (total_expense / total_budget * 100)
                    st.metric(
                        "✨ 남은 예산",
                        f"₩{remaining:,.0f}",
                        f"진행률 {progress:.1f}%",
                        help="남은 예산과 예산 진행률"
                    )
                
                # 차트 데이터 준비
                categories = list(planned_budget.keys())
                planned_values = [
                    planned_budget[cat] for cat in categories
                ]
                actual_values = [
                    actual_expenses.get(cat, 0) for cat in categories
                ]
                
                # 차트 생성
                st.markdown("### 📊 카테고리별 예산 현황")
                chart = create_budget_progress_chart(
                    categories=categories,
                    planned=planned_values,
                    actual=actual_values
                )
                st.plotly_chart(chart, use_container_width=True)
                
                # 상세 현황 테이블
                st.markdown("### 📋 카테고리별 상세 현황")
                
                progress_df = pd.DataFrame({
                    "카테고리": categories,
                    "계획 예산": planned_values,
                    "실제 지출": actual_values,
                    "잔액": [p - a for p, a in zip(
                        planned_values, actual_values
                    )]
                })
                
                # 진행률 계산
                progress_df["진행률"] = (
                    progress_df["실제 지출"] /
                    progress_df["계획 예산"] * 100
                ).round(1)
                
                # 스타일링 함수
                def color_progress(val):
                    try:
                        num = float(val.strip("%"))
                        if num > 100:
                            return "color: red"
                        elif num > 80:
                            return "color: orange"
                        return "color: green"
                    except ValueError:
                        return ""
                
                # 스타일이 적용된 데이터프레임 표시
                st.dataframe(
                    progress_df.style.format({
                        "계획 예산": "{:,.0f}원",
                        "실제 지출": "{:,.0f}원",
                        "잔액": "{:,.0f}원",
                        "진행률": "{:.1f}%"
                    }).applymap(
                        color_progress,
                        subset=["진행률"]
                    ),
                    use_container_width=True
                )
                
                # 경고 메시지
                st.markdown("### ⚠️ 주의 필요 항목")
                warning_items = progress_df[
                    progress_df["진행률"] > 80
                ]
                
                if not warning_items.empty:
                    for _, item in warning_items.iterrows():
                        progress = item["진행률"]
                        if progress > 100:
                            st.error(
                                f"🚨 {item['카테고리']}: "
                                f"예산 초과 ({progress:.1f}%)"
                            )
                        else:
                            st.warning(
                                f"⚠️ {item['카테고리']}: "
                                f"예산 주의 ({progress:.1f}%)"
                            )
                else:
                    st.success("✅ 모든 카테고리가 예산 내에서 잘 관리되고 있습니다.")
            else:
                st.warning(f"⚠️ {month_key} 월의 예산 데이터가 없습니다.")
        else:
            st.info("💡 예산 또는 지출 데이터가 없습니다.") 
