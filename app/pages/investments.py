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
                        "현금성 자산", "암호화폐", "기타"
                    ],
                    key="investment_type"
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
                
                investment_amount = st.number_input(
                    "투자 금액",
                    min_value=0,
                    value=0,
                    step=100000,
                    help="투자한 금액을 입력하세요"
                )
            
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
                    "amount": investment_amount,
                    "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                    "memo": investment_memo
                }
                
                if data_handler.save_investment(investment_data):
                    st.success("✅ 투자 정보가 저장되었습니다.")
                else:
                    st.error("❌ 투자 정보 저장에 실패했습니다.")
    
    with tab2:
        st.markdown("### 포트폴리오 성과 분석")
        
        # 투자 데이터 로드
        investment_data = data_handler.load_investment()
        
        if investment_data:
            # 전체 포트폴리오 가치 계산
            total_investment = sum(
                item["amount"] for item in investment_data.values()
            )
            
            # 투자 유형별 분포
            type_distribution = {}
            for item in investment_data.values():
                type_distribution[item["type"]] = type_distribution.get(
                    item["type"], 0
                ) + item["amount"]
            
            # 포트폴리오 요약
            st.metric(
                "💰 총 투자 금액",
                f"₩{total_investment:,.0f}",
                help="전체 포트폴리오 가치"
            )
            
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
                for investment in stock_investments:
                    with st.container():
                        st.markdown(
                            f"#### {investment['name']} "
                            f"({investment['symbol']})"
                        )
                        
                        stock_data = get_stock_data(investment["symbol"])
                        
                        if stock_data is not None:
                            col1, col2, col3 = st.columns(3)
                            
                            # 현재가 및 수익률 계산
                            current_price = stock_data["Close"].iloc[-1]
                            purchase_price = stock_data.loc[
                                investment["purchase_date"]:"Close"
                            ].iloc[0]
                            returns = (
                                (current_price - purchase_price) /
                                purchase_price * 100
                            )
                            
                            with col1:
                                st.metric(
                                    "현재가",
                                    f"₩{current_price:,.0f}",
                                    f"{returns:+.2f}%",
                                    help="현재 주가와 수익률"
                                )
                            
                            with col2:
                                st.metric(
                                    "투자 금액",
                                    f"₩{investment['amount']:,.0f}",
                                    help="초기 투자 금액"
                                )
                            
                            with col3:
                                profit = investment['amount'] * (
                                    returns / 100
                                )
                                st.metric(
                                    "평가 손익",
                                    f"₩{profit:,.0f}",
                                    help="현재까지의 투자 손익"
                                )
                            
                            # 주가 차트
                            performance_chart = (
                                create_investment_performance_chart(
                                    dates=stock_data.index,
                                    performance=stock_data["Close"],
                                    benchmark=None
                                )
                            )
                            st.plotly_chart(
                                performance_chart,
                                use_container_width=True
                            )
            else:
                st.info("💡 주식 투자 내역이 없습니다.")
        else:
            st.info("💡 투자 데이터가 없습니다.")
    
    with tab3:
        st.markdown("### 🌎 시장 동향")
        
        # 주요 지수 모니터링
        indices = {
            "^GSPC": "S&P 500",
            "^KS11": "KOSPI",
            "^KQ11": "KOSDAQ",
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum"
        }
        
        # 기간 선택
        period = st.selectbox(
            "조회 기간",
            ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
            index=2,
            help="시장 동향을 조회할 기간을 선택하세요"
        )
        
        # 지수 데이터 표시
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        col_idx = 0
        
        for symbol, name in indices.items():
            data = get_stock_data(symbol, period=period)
            if data is not None:
                with cols[col_idx % 3]:
                    daily_return = (
                        (data["Close"].iloc[-1] - data["Close"].iloc[-2]) /
                        data["Close"].iloc[-2] * 100
                    )
                    period_return = (
                        (data["Close"].iloc[-1] - data["Close"].iloc[0]) /
                        data["Close"].iloc[0] * 100
                    )
                    
                    st.metric(
                        name,
                        f"{data['Close'].iloc[-1]:,.2f}",
                        f"{daily_return:+.2f}% (일간) "
                        f"{period_return:+.2f}% (기간)",
                        help=f"{name}의 현재가와 수익률"
                    )
                    
                    # 차트 생성
                    fig = create_investment_performance_chart(
                        dates=data.index,
                        performance=data["Close"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                col_idx += 1 
