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
    """USD/KRW 환율 정보 가져오기"""
    try:
        usd_krw = yf.Ticker("KRW=X")
        rate = usd_krw.history(period="1d")["Close"].iloc[-1]
        return rate
    except Exception as e:
        st.error(f"환율 데이터 조회 실패: {e}")
        return None


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
        
        with st.form("investment_form"):
            # 투자 종목 입력
            col1, col2 = st.columns(2)
            
            with col1:
                investment_type = st.selectbox(
                    "투자 유형",
                    [
                        "주식", "채권", "펀드",
                        "현금성 자산", "암호화폐", "원자재",
                        "Gold", "기타"
                    ]
                )
                
                symbol = st.text_input(
                    "종목 코드 (주식/암호화폐)",
                    help="예: 005930.KS (삼성전자), BTC-USD (비트코인)"
                )
            
            with col2:
                investment_name = st.text_input(
                    "투자 상품명",
                    help="투자 상품의 이름을 입력하세요"
                )
                
                purchase_quantity = st.number_input(
                    "매입수량",
                    min_value=0,
                    value=0,
                    step=1,
                    help="매입한 수량을 입력하세요"
                )
            
            col3, col4 = st.columns(2)
            with col3:
                currency = st.selectbox(
                    "통화",
                    ["KRW", "USD"],
                    help="매수가의 통화 단위를 선택하세요"
                )
                
                purchase_price = st.number_input(
                    f"매수가 ({currency})",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    help="주당 매수 가격을 입력하세요",
                    format="%0.2f"
                )
                
                current_price = st.number_input(
                    f"현재가 ({currency})",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    help="현재 주당 가격을 입력하세요",
                    format="%0.2f"
                )
                
                if currency == "USD":
                    purchase_exchange_rate = st.number_input(
                        "매입 시 환율 (USD/KRW)",
                        min_value=0.0,
                        value=1300.0,
                        step=0.1,
                        help="매입 당시의 USD/KRW 환율을 입력하세요",
                        format="%0.1f"
                    )
                    
                    current_exchange_rate = st.number_input(
                        "현재 환율 (USD/KRW)",
                        min_value=0.0,
                        value=1300.0,
                        step=0.1,
                        help="현재 USD/KRW 환율을 입력하세요",
                        format="%0.1f"
                    )
                
                # 매입금액 직접 입력
                currency_symbol = "₩" if currency == "KRW" else "$"
                investment_amount = st.number_input(
                    "매입금액",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    help="총 매입금액을 입력하세요",
                    format="%0.2f"
                )
                
                # 평가금액 직접 입력
                current_amount = st.number_input(
                    "평가금액",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    help="현재 평가금액을 입력하세요",
                    format="%0.2f"
                )
                st.caption(f"현재 평가금액: {currency_symbol}{current_amount:,.2f}")
            
            with col4:
                purchase_date = st.date_input(
                    "매수일",
                    value=datetime.now(),
                    help="투자 시작일을 선택하세요"
                )
            
            investment_memo = st.text_area(
                "메모",
                height=100,
                help="투자와 관련된 메모를 입력하세요"
            )
            
            submit_investment = st.form_submit_button(
                "투자 정보 저장",
                use_container_width=True
            )
            
            if submit_investment:
                investment_data = {
                    "type": investment_type,
                    "symbol": symbol,
                    "name": investment_name,
                    "purchase_quantity": purchase_quantity,
                    "purchase_price": purchase_price,
                    "current_price": current_price,
                    "currency": currency,
                    "amount": investment_amount,
                    "current_amount": current_amount,
                    "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                    "memo": investment_memo
                }
                
                if currency == "USD":
                    investment_data.update({
                        "purchase_exchange_rate": purchase_exchange_rate,
                        "current_exchange_rate": current_exchange_rate
                    })
                
                if data_handler.save_investment(investment_data):
                    st.success("✅ 투자 정보가 저장되었습니다.")
                    st.rerun()
                else:
                    st.error("❌ 투자 정보 저장에 실패했습니다.")
    
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
            for item in investment_data.values():
                investment_amount = float(item.get("amount", 0))
                currency = item.get("currency", "KRW")
                
                if currency == "USD":
                    # USD 자산의 경우 현재 환율로 원화 환산
                    current_rate = float(item.get("current_exchange_rate", 1300.0))
                    krw_amount = investment_amount * current_rate
                else:
                    krw_amount = investment_amount
                
                type_distribution[item["type"]] = type_distribution.get(
                    item["type"], 0
                ) + krw_amount
            
            # 파이 차트 생성
            st.markdown("#### 투자 유형별 분포")
            pie_chart = create_pie_chart(
                labels=list(type_distribution.keys()),
                values=list(type_distribution.values()),
                title="자산 유형별 분포"
            )
            st.plotly_chart(pie_chart, use_container_width=True)
            
            # 주식 투자 성과 분석
            st.markdown("### 📈 주식 투자 성과")
            
            stock_investments = [
                item for item in investment_data.values()
                if item["type"] == "주식" and item["symbol"]
            ]
            
            if stock_investments:
                for investment_id, investment in investment_data.items():
                    with st.container():
                        col_title, col_actions = st.columns([3, 1])
                        
                        with col_title:
                            st.markdown(
                                f"#### {investment['name']} "
                                f"({investment['symbol']})"
                            )
                        
                        with col_actions:
                            col_edit, col_delete = st.columns(2)
                            with col_edit:
                                if st.button("📝", key=f"edit_{investment_id}", help="투자 정보 수정"):
                                    st.session_state.edit_investment = investment
                                    st.session_state.edit_investment_id = investment_id
                                    st.session_state.show_edit_form = True
                            
                            with col_delete:
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
                                st.markdown("### 투자 정보 수정")
                                
                                edit_type = st.selectbox(
                                    "투자 유형",
                                    [
                                        "주식", "채권", "펀드",
                                        "현금성 자산", "암호화폐", "원자재",
                                        "Gold", "기타"
                                    ],
                                    index=["주식", "채권", "펀드", "현금성 자산", "암호화폐", "원자재", "Gold", "기타"].index(
                                        st.session_state.edit_investment['type']
                                    ),
                                    key=f"edit_type_{investment_id}"
                                )
                                
                                edit_symbol = st.text_input(
                                    "종목 코드",
                                    value=st.session_state.edit_investment['symbol'],
                                    key=f"edit_symbol_{investment_id}"
                                )
                                
                                edit_name = st.text_input(
                                    "투자 상품명",
                                    value=st.session_state.edit_investment['name'],
                                    key=f"edit_name_{investment_id}"
                                )
                                
                                edit_quantity = st.number_input(
                                    "매입수량",
                                    min_value=0,
                                    value=int(st.session_state.edit_investment.get('purchase_quantity', 0)),
                                    step=1,
                                    key=f"edit_quantity_{investment_id}"
                                )
                                
                                edit_currency = st.selectbox(
                                    "통화",
                                    ["KRW", "USD"],
                                    index=["KRW", "USD"].index(
                                        st.session_state.edit_investment.get('currency', 'KRW')
                                    ),
                                    key=f"edit_currency_{investment_id}"
                                )
                                
                                edit_price = st.number_input(
                                    f"매수가 ({edit_currency})",
                                    min_value=0.0,
                                    value=float(st.session_state.edit_investment.get('purchase_price', 0)),
                                    step=0.01,
                                    format="%0.2f",
                                    key=f"edit_price_{investment_id}"
                                )
                                
                                if edit_currency == "USD":
                                    edit_purchase_exchange_rate = st.number_input(
                                        "매입 시 환율 (USD/KRW)",
                                        min_value=0.0,
                                        value=float(st.session_state.edit_investment.get('purchase_exchange_rate', 1300.0)),
                                        step=0.1,
                                        format="%0.1f",
                                        key=f"edit_purchase_exchange_rate_{investment_id}"
                                    )
                                    
                                    edit_current_exchange_rate = st.number_input(
                                        "현재 환율 (USD/KRW)",
                                        min_value=0.0,
                                        value=float(st.session_state.edit_investment.get('current_exchange_rate', 1300.0)),
                                        step=0.1,
                                        format="%0.1f",
                                        key=f"edit_current_exchange_rate_{investment_id}"
                                    )
                                
                                # 매입금액 표시
                                edit_amount = st.number_input(
                                    "매입금액",
                                    min_value=0.0,
                                    value=float(st.session_state.edit_investment.get('amount', 0)),
                                    step=1000.0,
                                    format="%0.2f",
                                    key=f"edit_amount_{investment_id}"
                                )
                                
                                # 평가금액 입력
                                edit_current_amount = st.number_input(
                                    "평가금액",
                                    min_value=0.0,
                                    value=float(st.session_state.edit_investment.get('current_amount', 0)),
                                    step=1000.0,
                                    format="%0.2f",
                                    key=f"edit_current_amount_{investment_id}"
                                )
                                
                                # 현재 평가금액 표시
                                currency_symbol = "₩" if edit_currency == "KRW" else "$"
                                st.caption(f"현재 평가금액: {currency_symbol}{edit_current_amount:,.2f}")
                                
                                edit_date = st.date_input(
                                    "매수일",
                                    value=datetime.strptime(
                                        st.session_state.edit_investment['purchase_date'],
                                        "%Y-%m-%d"
                                    ),
                                    key=f"edit_date_{investment_id}"
                                )
                                
                                edit_memo = st.text_area(
                                    "메모",
                                    value=st.session_state.edit_investment.get('memo', ''),
                                    key=f"edit_memo_{investment_id}"
                                )
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.form_submit_button("수정 완료"):
                                        update_data = {
                                            "type": edit_type,
                                            "symbol": edit_symbol,
                                            "name": edit_name,
                                            "purchase_quantity": edit_quantity,
                                            "purchase_price": edit_price,
                                            "current_price": edit_price,  # 현재가도 업데이트
                                            "currency": edit_currency,
                                            "amount": edit_amount,
                                            "current_amount": edit_current_amount,  # 평가금액 추가
                                            "purchase_date": edit_date.strftime("%Y-%m-%d"),
                                            "memo": edit_memo
                                        }
                                        
                                        if edit_currency == "USD":
                                            update_data.update({
                                                "purchase_exchange_rate": edit_purchase_exchange_rate,
                                                "current_exchange_rate": edit_current_exchange_rate
                                            })
                                        
                                        if data_handler.update_investment(
                                            st.session_state.edit_investment_id,
                                            update_data
                                        ):
                                            st.success("✅ 투자 정보가 수정되었습니다.")
                                            st.session_state.show_edit_form = False
                                            st.rerun()
                                        else:
                                            st.error("❌ 투자 정보 수정에 실패했습니다.")
                                
                                with col2:
                                    if st.form_submit_button("취소", type="secondary"):
                                        st.session_state.show_edit_form = False
                                        st.rerun()
                        
                        stock_data = get_stock_data(investment["symbol"])
                        
                        if stock_data is not None and not stock_data.empty and len(stock_data) > 1:
                            col1, col2, col3, col4 = st.columns(4)
                            
                            try:
                                # 현재가 및 수익률 계산
                                currency = investment.get('currency', 'KRW')
                                investment_amount = float(investment.get('amount', 0))
                                current_amount = float(investment.get('current_amount', investment_amount))
                                
                                # 수익률 계산
                                if currency == "USD":
                                    # USD 자산의 경우 원화 환산 수익률 계산
                                    purchase_rate = float(investment.get('purchase_exchange_rate', 1300.0))
                                    current_rate = float(investment.get('current_exchange_rate', 1300.0))
                                    
                                    # 원화 환산 금액
                                    krw_investment = investment_amount * purchase_rate
                                    krw_current = current_amount * current_rate
                                    
                                    # 원화 기준 수익률 계산
                                    returns = ((krw_current - krw_investment) / krw_investment * 100) if krw_investment > 0 else 0
                                    
                                    # 표시할 금액과 환율 변동 효과
                                    display_investment = investment_amount
                                    display_current = current_amount
                                    exchange_effect = ((current_rate - purchase_rate) / purchase_rate * 100) if purchase_rate > 0 else 0
                                else:
                                    # KRW 자산의 경우 단순 수익률 계산
                                    returns = ((current_amount - investment_amount) / investment_amount * 100) if investment_amount > 0 else 0
                                    display_investment = investment_amount
                                    display_current = current_amount
                                
                                with col1:
                                    currency_symbol = "₩" if currency == "KRW" else "$"
                                    st.metric(
                                        "💰 매입금액",
                                        f"{currency_symbol}{display_investment:,.2f}",
                                        help="투자 시점의 매입금액"
                                    )
                                with col2:
                                    st.metric(
                                        "💵 평가금액",
                                        f"{currency_symbol}{display_current:,.2f}",
                                        help="현재 평가금액"
                                    )
                                with col3:
                                    st.metric(
                                        "📈 수익률",
                                        f"{returns:,.1f}%",
                                        help="원화 기준 수익률" if currency == "USD" else "투자 수익률"
                                    )
                                if currency == "USD":
                                    with col4:
                                        st.metric(
                                            "💱 현재 환율",
                                            f"₩{current_rate:,.1f}",
                                            f"{exchange_effect:+.1f}%",
                                            help="환율 변동률"
                                        )
                                
                                # 주가 차트 표시
                                performance_chart = create_investment_performance_chart(
                                    dates=stock_data.index,
                                    performance=stock_data["Close"],
                                    benchmark=None
                                )
                                st.plotly_chart(
                                    performance_chart,
                                    use_container_width=True
                                )
                            except (IndexError, KeyError) as e:
                                st.warning(f"⚠️ {investment['name']}({investment['symbol']})의 주가 데이터를 처리하는 중 오류가 발생했습니다.")
                        else:
                            st.warning(f"⚠️ {investment['name']}({investment['symbol']})의 주가 데이터를 가져올 수 없습니다.")
            else:
                st.info("💡 주식 투자 내역이 없습니다.")
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
