import streamlit as st
import pandas as pd
from utils.data_handler import FinanceDataHandler
from utils.visualization import create_pie_chart


def calculate_portfolio_metrics(data: dict) -> dict:
    """포트폴리오 지표 계산"""
    total_assets = sum(data.values())
    weights = {k: v/total_assets * 100 for k, v in data.items()}
    return {
        "total": total_assets,
        "weights": weights
    }


def render_portfolio_page():
    st.title("💼 포트폴리오 관리")
    
    # 데이터 핸들러 초기화
    data_handler = FinanceDataHandler()
    
    # 탭 생성
    tab1, tab2 = st.tabs(["📝 자산 배분", "📊 포트폴리오 분석"])
    
    with tab1:
        st.markdown("### 자산 배분 설정")
        
        with st.form("portfolio_form"):
            # 자산 유형별 금액 입력을 2열로 구성
            col1, col2 = st.columns(2)
            
            # 자산 유형 목록
            asset_types = [
                "주식", "채권", "현금성 자산",
                "부동산", "원자재", "대체투자"
            ]
            
            # 자산 데이터 저장용 딕셔너리
            asset_data = {}
            
            # 왼쪽 열에 자산 유형 1~3
            with col1:
                for asset_type in asset_types[:3]:
                    asset_data[asset_type] = st.number_input(
                        f"{asset_type} 금액",
                        min_value=0,
                        value=0,
                        step=1000000,
                        key=f"asset_{asset_type}",
                        help=f"{asset_type}에 투자된 금액을 입력하세요"
                    )
            
            # 오른쪽 열에 자산 유형 4~6
            with col2:
                for asset_type in asset_types[3:]:
                    asset_data[asset_type] = st.number_input(
                        f"{asset_type} 금액",
                        min_value=0,
                        value=0,
                        step=1000000,
                        key=f"asset_{asset_type}",
                        help=f"{asset_type}에 투자된 금액을 입력하세요"
                    )
            
            # 총 자산 계산 및 표시
            total_assets = sum(asset_data.values())
            st.metric(
                "💰 총 자산",
                f"₩{total_assets:,.0f}",
                help="전체 포트폴리오 가치"
            )
            
            # 저장 버튼
            submit_portfolio = st.form_submit_button(
                "자산 배분 저장",
                use_container_width=True
            )
            
            if submit_portfolio:
                if data_handler.save_investment(asset_data):
                    st.success("✅ 자산 배분이 저장되었습니다.")
                else:
                    st.error("❌ 자산 배분 저장에 실패했습니다.")
    
    with tab2:
        st.markdown("### 포트폴리오 분석")
        
        # 자산 데이터 로드
        portfolio_data = data_handler.load_investment()
        
        if portfolio_data:
            # 포트폴리오 지표 계산
            metrics = calculate_portfolio_metrics(portfolio_data)
            
            # 포트폴리오 요약
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "💰 총 자산",
                    f"₩{metrics['total']:,.0f}",
                    help="전체 포트폴리오 가치"
                )
            
            with col2:
                largest_asset = max(
                    metrics['weights'].items(),
                    key=lambda x: x[1]
                )
                st.metric(
                    "📊 최대 비중 자산",
                    f"{largest_asset[0]}",
                    f"{largest_asset[1]:.1f}%",
                    help="가장 큰 비중을 차지하는 자산"
                )
            
            # 자산 배분 차트
            st.markdown("### 📊 자산 배분 현황")
            pie_chart = create_pie_chart(
                labels=list(portfolio_data.keys()),
                values=list(portfolio_data.values()),
                title="자산 배분 현황"
            )
            st.plotly_chart(pie_chart, use_container_width=True)
            
            # 자산 배분 상세
            st.markdown("### 📋 자산 배분 상세")
            portfolio_df = pd.DataFrame({
                "자산 유형": portfolio_data.keys(),
                "금액": portfolio_data.values(),
                "비중": [
                    f"{v:.1f}%" for v in metrics["weights"].values()
                ]
            })
            
            # 스타일이 적용된 데이터프레임 표시
            st.dataframe(
                portfolio_df.style.format({
                    "금액": "{:,.0f}원"
                }),
                use_container_width=True
            )
            
            # 투자 제안
            st.markdown("### 💡 투자 제안")
            
            # 목표 자산 배분 (보수적 포트폴리오)
            conservative = {
                "주식": 30,
                "채권": 40,
                "현금성 자산": 15,
                "부동산": 10,
                "원자재": 3,
                "대체투자": 2
            }
            
            # 목표 자산 배분 (공격적 포트폴리오)
            aggressive = {
                "주식": 60,
                "채권": 20,
                "현금성 자산": 5,
                "부동산": 10,
                "원자재": 3,
                "대체투자": 2
            }
            
            # 포트폴리오 성향 선택
            portfolio_type = st.radio(
                "포트폴리오 성향",
                ["보수적", "공격적"],
                horizontal=True,
                help="원하는 포트폴리오 성향을 선택하세요"
            )
            
            target_allocation = (
                conservative if portfolio_type == "보수적"
                else aggressive
            )
            
            # 현재 vs 목표 자산 배분 비교
            comparison_data = []
            for asset_type in asset_types:
                current_weight = metrics["weights"].get(asset_type, 0)
                target_weight = target_allocation.get(asset_type, 0)
                diff = current_weight - target_weight
                
                comparison_data.append({
                    "자산 유형": asset_type,
                    "현재 비중": f"{current_weight:.1f}%",
                    "목표 비중": f"{target_weight:.1f}%",
                    "조정 필요": f"{diff:+.1f}%"
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # 스타일링 함수
            def color_adjustment(val):
                try:
                    num = float(val.strip("%").strip("+"))
                    if abs(num) < 1:
                        return "color: green"
                    elif abs(num) < 5:
                        return "color: orange"
                    return "color: red"
                except ValueError:
                    return ""
            
            # 스타일이 적용된 데이터프레임 표시
            st.dataframe(
                comparison_df.style.applymap(
                    color_adjustment,
                    subset=["조정 필요"]
                ),
                use_container_width=True
            )
            
            # 리밸런싱 제안
            st.markdown("### ⚖️ 리밸런싱 제안")
            
            # 리밸런싱이 필요한 항목 필터링
            rebalance_needed = [
                item for item in comparison_data
                if abs(float(
                    item["조정 필요"].strip("%").strip("+")
                )) >= 5
            ]
            
            if rebalance_needed:
                for item in rebalance_needed:
                    diff = float(
                        item["조정 필요"].strip("%").strip("+")
                    )
                    action = "매도" if diff > 0 else "매수"
                    amount = abs(diff) * metrics["total"] / 100
                    
                    if diff > 0:
                        st.error(
                            f"🔻 {item['자산 유형']}: {action} 필요 "
                            f"(약 ₩{amount:,.0f}, {abs(diff):.1f}%)"
                        )
                    else:
                        st.success(
                            f"🔺 {item['자산 유형']}: {action} 필요 "
                            f"(약 ₩{amount:,.0f}, {abs(diff):.1f}%)"
                        )
            else:
                st.success(
                    "✅ 현재 포트폴리오가 목표 배분에 잘 맞춰져 있습니다."
                )
        else:
            st.info("💡 포트폴리오 데이터가 없습니다.") 
