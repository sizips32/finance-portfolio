import sys
import os

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from utils.data_handler import FinanceDataHandler
from utils.visualization import (
    create_investment_performance_chart,
    create_pie_chart
)


def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """주식 데이터 가져오기"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        st.error(f"주식 데이터 조회 실패: {e}")
        return None


def get_exchange_rate() -> float:
    """USD/KRW 환율 정보 가져오기 (캐싱 적용)"""
    # 세션 상태에 캐시된 환율이 있는지 확인
    if 'cached_exchange_rate' in st.session_state:
        cached_rate, cached_time = st.session_state.cached_exchange_rate
        # 5분 이내의 캐시된 데이터라면 사용
        if (datetime.now() - cached_time).seconds < 300:
            return cached_rate
    
    try:
        usd_krw = yf.Ticker("KRW=X")
        rate = usd_krw.history(period="1d")["Close"].iloc[-1]
        
        # 성공적으로 가져온 환율을 캐시에 저장
        st.session_state.cached_exchange_rate = (rate, datetime.now())
        return rate
    except Exception as e:
        st.warning(f"환율 데이터 조회 실패: {e}")
        # 캐시된 데이터가 있으면 사용, 없으면 기본값 반환
        if 'cached_exchange_rate' in st.session_state:
            return st.session_state.cached_exchange_rate[0]
        return 1300.0  # 기본값


def render_investments_page():
    st.title("📈 투자 관리")
    
    # 데이터 핸들러 초기화
    data_handler = FinanceDataHandler()
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs([
        "💼 포트폴리오 입력",
        "📊 성과 분석",
        "🌎 시장 동향"
    ])
    
    with tab1:
        st.markdown("### 투자 포트폴리오 입력")
        
        render_investment_form()
    
    with tab2:
        st.markdown("### 포트폴리오 성과 분석")
        
        # 투자 데이터 로드
        investment_data = data_handler.load_investment()
        
        if investment_data:
            # 전체 포트폴리오 가치 계산
            total_krw_investment = 0
            total_krw_evaluation = 0
            
            for item in investment_data.values():
                investment_amount = float(item.get("amount", 0))
                current_amount = float(item.get("current_amount", investment_amount))
                currency = item.get("currency", "KRW")
                
                if currency == "USD":
                    # USD 자산의 경우 원화로 환산
                    purchase_rate = float(item.get("purchase_exchange_rate", 1300.0))
                    current_rate = float(item.get("current_exchange_rate", 1300.0))
                    
                    total_krw_investment += investment_amount * purchase_rate
                    total_krw_evaluation += current_amount * current_rate
                else:
                    # KRW 자산은 그대로 합산
                    total_krw_investment += investment_amount
                    total_krw_evaluation += current_amount
            
            # 전체 수익률 계산
            total_returns = ((total_krw_evaluation - total_krw_investment) / total_krw_investment * 100) if total_krw_investment > 0 else 0
            
            # 포트폴리오 요약
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "💰 총 투자금액",
                    f"₩{total_krw_investment:,.0f}",
                    help="전체 포트폴리오 투자금액 (USD 자산은 매입 환율로 환산)"
                )
            with col2:
                st.metric(
                    "💵 총 평가금액",
                    f"₩{total_krw_evaluation:,.0f}",
                    help="전체 포트폴리오 평가금액 (USD 자산은 현재 환율로 환산)"
                )
            with col3:
                st.metric(
                    "📈 총 수익률",
                    f"{total_returns:,.1f}%",
                    help="원화 기준 전체 포트폴리오 수익률"
                )
            
            # 투자 유형별 분포 (원화 환산 기준)
            type_distribution = {}
            total_krw_value = 0
            
            # 먼저 전체 원화 가치 계산
            for item in investment_data.values():
                current_amount = float(item.get('current_amount', 0))
                currency = item.get('currency', 'KRW')
                
                if currency != "KRW":
                    # 외화 자산의 경우 현재 환율로 원화 환산
                    current_rate = float(item.get('current_exchange_rate', 1300.0))
                    krw_value = current_amount * current_rate
                else:
                    krw_value = current_amount
                
                total_krw_value += krw_value
                
                # 유형별 합계 계산
                inv_type = item.get('type', '기타')
                type_distribution[inv_type] = type_distribution.get(inv_type, 0) + krw_value
            
            # 비중 계산 및 파이 차트 데이터 준비
            if total_krw_value > 0:
                labels = []
                values = []
                percentages = []
                
                for inv_type, krw_amount in type_distribution.items():
                    percentage = (krw_amount / total_krw_value) * 100
                    labels.append(inv_type)
                    values.append(krw_amount)
                    percentages.append(percentage)
                
                # 파이 차트 생성
                st.markdown("#### 📊 투자 유형별 분포")
                
                # 비중 표시
                cols = st.columns(len(labels))
                for i, (label, percentage) in enumerate(zip(labels, percentages)):
                    with cols[i]:
                        st.metric(
                            label,
                            f"{percentage:.1f}%",
                            help=f"총 {values[i]:,.0f} KRW"
                        )
                
                pie_chart = create_pie_chart(
                    labels=labels,
                    values=values,
                    title="자산 유형별 분포 (원화 환산 기준)"
                )
                st.plotly_chart(pie_chart, use_container_width=True)
            
            # 투자 목록 표시
            st.markdown("### 📋 투자 목록")
            
            for investment_id, investment in investment_data.items():
                with st.expander(f"{investment['name']} ({investment['type']})"):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        # 투자 정보 표시
                        currency_symbol = "₩" if investment['currency'] == "KRW" else "$"
                        amount = float(investment['amount'])
                        current_amount = float(investment.get('current_amount', amount))
                        returns = ((current_amount - amount) / amount * 100) if amount > 0 else 0
                        
                        info_cols = st.columns(3)
                        with info_cols[0]:
                            st.metric(
                                "💰 매입금액",
                                f"{currency_symbol}{amount:,.2f}",
                                help="투자 시점의 매입금액"
                            )
                        with info_cols[1]:
                            st.metric(
                                "💵 평가금액",
                                f"{currency_symbol}{current_amount:,.2f}",
                                help="현재 평가금액"
                            )
                        with info_cols[2]:
                            st.metric(
                                "📈 수익률",
                                f"{returns:,.1f}%",
                                help="투자 수익률"
                            )
                    
                    with col_actions:
                        action_cols = st.columns(2)
                        with action_cols[0]:
                            if st.button("📝", key=f"edit_{investment_id}", help="투자 정보 수정"):
                                st.session_state.edit_investment = investment
                                st.session_state.edit_investment_id = investment_id
                                st.session_state.show_edit_form = True
                        
                        with action_cols[1]:
                            if st.button("🗑️", key=f"delete_{investment_id}", help="투자 정보 삭제"):
                                if data_handler.delete_investment(investment_id):
                                    st.success("✅ 투자 정보가 삭제되었습니다.")
                                    st.rerun()
                                else:
                                    st.error("❌ 투자 정보 삭제에 실패했습니다.")
                    
                    # 수정 폼 표시
                    if (hasattr(st.session_state, 'show_edit_form') and 
                        st.session_state.show_edit_form and 
                        st.session_state.edit_investment_id == investment_id):
                        
                        with st.form(key=f"edit_form_{investment_id}"):
                            st.markdown("### ✏️ 투자 정보 수정")
                            
                            edit_type = st.selectbox(
                                "투자 유형",
                                [
                                    "주식", "채권", "펀드", "현금성",
                                    "대체투자", "Gold", "원자재", "기타"
                                ],
                                index=[
                                    "주식", "채권", "펀드", "현금성",
                                    "대체투자", "Gold", "원자재", "기타"
                                ].index(investment['type']),
                                key=f"edit_type_{investment_id}"
                            )
                            
                            edit_name = st.text_input(
                                "상품명",
                                value=investment['name'],
                                key=f"edit_name_{investment_id}"
                            )
                            
                            edit_symbol = st.text_input(
                                "종목 코드",
                                value=investment.get('symbol', ''),
                                key=f"edit_symbol_{investment_id}"
                            )
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                edit_quantity = st.number_input(
                                    "수량",
                                    min_value=0.0,
                                    value=float(investment.get('purchase_quantity', 0)),
                                    step=0.01,
                                    key=f"edit_quantity_{investment_id}"
                                )
                            
                            with col2:
                                edit_price = st.number_input(
                                    "매입 가격",
                                    min_value=0.0,
                                    value=float(investment.get('purchase_price', 0)),
                                    step=0.01,
                                    key=f"edit_price_{investment_id}"
                                )
                            
                            with col3:
                                edit_current_price = st.number_input(
                                    "현재 가격",
                                    min_value=0.0,
                                    value=float(investment.get('current_price', 0)),
                                    step=0.01,
                                    key=f"edit_current_price_{investment_id}"
                                )
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                edit_currency = st.selectbox(
                                    "통화",
                                    ["KRW", "USD", "EUR", "JPY", "CNY"],
                                    index=["KRW", "USD", "EUR", "JPY", "CNY"].index(
                                        investment.get('currency', 'KRW')
                                    ),
                                    key=f"edit_currency_{investment_id}"
                                )
                            
                            if edit_currency != "KRW":
                                with col2:
                                    edit_purchase_rate = st.number_input(
                                        "매입 환율",
                                        min_value=0.0,
                                        value=float(investment.get('purchase_exchange_rate', 1300.0)),
                                        step=0.01,
                                        key=f"edit_purchase_rate_{investment_id}"
                                    )
                                
                                with col3:
                                    edit_current_rate = st.number_input(
                                        "현재 환율",
                                        min_value=0.0,
                                        value=get_exchange_rate() or float(investment.get('current_exchange_rate', 1300.0)),
                                        step=0.01,
                                        key=f"edit_current_rate_{investment_id}"
                                    )
                            
                            edit_date = st.date_input(
                                "매입일",
                                value=datetime.strptime(
                                    investment['purchase_date'],
                                    "%Y-%m-%d"
                                ).date(),
                                key=f"edit_date_{investment_id}"
                            )
                            
                            edit_memo = st.text_area(
                                "메모",
                                value=investment.get('memo', ''),
                                key=f"edit_memo_{investment_id}"
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 수정 완료"):
                                    # 수정할 데이터 생성
                                    update_data = {
                                        "type": edit_type,
                                        "name": edit_name,
                                        "symbol": edit_symbol,
                                        "purchase_quantity": edit_quantity,
                                        "purchase_price": edit_price,
                                        "current_price": edit_current_price,
                                        "currency": edit_currency,
                                        "amount": edit_quantity * edit_price,
                                        "current_amount": edit_quantity * edit_current_price,
                                        "purchase_date": edit_date.strftime("%Y-%m-%d"),
                                        "memo": edit_memo
                                    }
                                    
                                    if edit_currency != "KRW":
                                        update_data.update({
                                            "purchase_exchange_rate": edit_purchase_rate,
                                            "current_exchange_rate": edit_current_rate
                                        })
                                    
                                    if data_handler.update_investment(investment_id, update_data):
                                        st.success("✅ 투자 정보가 수정되었습니다.")
                                        st.session_state.show_edit_form = False
                                        st.rerun()
                                    else:
                                        st.error("❌ 투자 정보 수정에 실패했습니다.")
                            
                            with col2:
                                if st.form_submit_button("❌ 취소"):
                                    st.session_state.show_edit_form = False
                                    st.rerun()
        else:
            st.info("💡 투자 데이터가 없습니다.")
    
    with tab3:
        st.markdown("### 🌎 시장 동향")
        
        # 실시간 환율 표시
        st.markdown("#### 💱 실시간 환율")
        exchange_rate = get_exchange_rate()
        if exchange_rate:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "USD/KRW",
                    f"₩{exchange_rate:,.2f}",
                    help="20분 간격으로 업데이트"
                )
            with col2:
                st.caption("마지막 업데이트: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        st.markdown("---")
        
        # 주요 지수 모니터링
        indices = {
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "KOSPI": "^KS11",
            "KOSDAQ": "^KQ11"
        }
        
        period = st.selectbox(
            "기간 선택",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=0,
            help="데이터를 조회할 기간을 선택하세요"
        )
        
        for name, symbol in indices.items():
            st.markdown(f"#### {name}")
            data = get_stock_data(symbol, period=period)
            
            if data is not None and not data.empty and len(data) > 1:
                try:
                    current = data["Close"].iloc[-1]
                    prev = data["Close"].iloc[-2]
                    change = (current - prev) / prev * 100
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "현재 지수",
                            f"{current:,.2f}"
                        )
                    with col2:
                        st.metric(
                            "일간 변동",
                            f"{change:+.2f}%"
                        )
                        # 변동 방향 표시
                        if change > 0:
                            st.markdown("📈 상승")
                        elif change < 0:
                            st.markdown("📉 하락")
                        else:
                            st.markdown("➖ 보합")
                    
                    # 차트 표시
                    performance_chart = create_investment_performance_chart(
                        dates=data.index,
                        performance=data["Close"],
                        benchmark=None
                    )
                    st.plotly_chart(performance_chart, use_container_width=True)
                except (IndexError, KeyError) as e:
                    st.warning(f"⚠️ {name}({symbol})의 지수 데이터를 처리하는 중 오류가 발생했습니다.")
            else:
                st.warning(f"⚠️ {name}({symbol})의 지수 데이터를 가져올 수 없습니다.")


def render_investment_form():
    """투자 정보 입력 폼 렌더링"""
    with st.form("investment_form"):
        st.subheader("📈 투자 정보 입력")
        
        # 첫 번째 행: 기본 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            inv_type = st.selectbox(
                "투자 유형",
                [
                    "주식", "채권", "펀드", "현금성",
                    "대체투자", "Gold", "원자재", "기타"
                ],
                help="투자 자산의 유형을 선택하세요",
                key="inv_type"
            )
        with col2:
            name = st.text_input(
                "상품명",
                help="투자 상품의 이름을 입력하세요",
                key="name"
            )
        with col3:
            symbol = st.text_input(
                "종목 코드(선택)",
                help="주식/ETF의 경우 종목 코드를 입력하세요",
                key="symbol"
            )
        
        # 두 번째 행: 수량 및 가격 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            quantity = st.number_input(
                "수량",
                min_value=0.0,
                step=0.01,
                help="매입 수량을 입력하세요",
                key="quantity"
            )
        with col2:
            price = st.number_input(
                "매입 가격",
                min_value=0.0,
                step=0.01,
                help="단위당 매입 가격을 입력하세요",
                key="price"
            )
        with col3:
            current_price = st.number_input(
                "현재 가격",
                min_value=0.0,
                step=0.01,
                help="현재 단위당 가격을 입력하세요",
                key="current_price"
            )
        
        # 세 번째 행: 통화 및 환율 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            currency = st.selectbox(
                "통화",
                ["KRW", "USD", "EUR", "JPY", "CNY"],
                help="자산의 거래 통화를 선택하세요",
                key="currency"
            )
        with col2:
            purchase_rate = st.number_input(
                "매입 환율",
                min_value=0.0,
                step=0.01,
                help="외화 자산인 경우 매입 시점의 환율을 입력하세요",
                key="purchase_rate"
            )
        with col3:
            current_rate = st.number_input(
                "현재 환율",
                min_value=0.0,
                value=get_exchange_rate() or 1300.0,
                step=0.01,
                help="외화 자산인 경우 현재 환율을 입력하세요",
                key="current_rate"
            )
        
        # 네 번째 행: 날짜 및 메모
        col1, col2 = st.columns(2)
        with col1:
            purchase_date = st.date_input(
                "매입일",
                help="자산 매입 날짜를 선택하세요",
                key="purchase_date"
            )
        with col2:
            memo = st.text_input(
                "메모",
                help="투자와 관련된 메모를 입력하세요",
                key="memo"
            )
        
        # 계산된 정보 표시
        if currency != "KRW" and quantity > 0 and price > 0:
            total_amount = quantity * price
            if purchase_rate > 0:
                krw_amount = total_amount * purchase_rate
                st.info(f"""
                    💰 매입 금액: {total_amount:,.2f} {currency}
                    원화 환산액: {krw_amount:,.0f} KRW
                """)
        
        # 제출 버튼
        submit = st.form_submit_button("저장")
        
        if submit:
            if not name:
                st.error("상품명은 필수입니다.")
                return
            
            if quantity <= 0 or price <= 0:
                st.error("수량과 가격은 0보다 커야 합니다.")
                return
            
            if currency != "KRW" and purchase_rate <= 0:
                st.error("외화 자산의 경우 매입 환율은 필수입니다.")
                return
            
            # 투자 데이터 생성
            investment_data = {
                "type": inv_type,
                "name": name,
                "symbol": symbol,
                "purchase_quantity": quantity,
                "purchase_price": price,
                "current_price": current_price or price,
                "currency": currency,
                "purchase_exchange_rate": purchase_rate if currency != "KRW" else None,
                "current_exchange_rate": current_rate if currency != "KRW" else None,
                "amount": quantity * price,
                "current_amount": quantity * (current_price or price),
                "purchase_date": purchase_date.isoformat(),
                "memo": memo
            }
            
            # 데이터 저장
            if st.session_state.data_handler.save_investment(investment_data):
                st.success("투자 정보가 저장되었습니다.")
                # 폼 초기화
                for key in st.session_state.keys():
                    if key.startswith("inv_"):
                        del st.session_state[key]
            else:
                st.error("저장 중 오류가 발생했습니다.")
