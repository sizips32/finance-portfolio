import sys
import os

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from scipy.optimize import minimize
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from utils.data_handler import FinanceDataHandler
from utils.visualization import create_pie_chart


def get_current_exchange_rate() -> float:
    """현재 USD/KRW 환율 정보 가져오기"""
    try:
        usd_krw = yf.Ticker("KRW=X")
        current_rate = usd_krw.history(period="1d")['Close'].iloc[-1]
        return current_rate
    except Exception as e:
        st.error(f"환율 데이터 조회 실패: {e}")
        return 1300.0  # 기본값


def convert_to_krw(amount: float, currency: str, exchange_rate: float = None) -> float:
    """외화를 원화로 변환"""
    if currency == "USD":
        if exchange_rate is None:
            exchange_rate = get_current_exchange_rate()
        return amount * exchange_rate
    return amount


def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """주식 데이터 가져오기"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        st.error(f"주식 데이터 조회 실패: {e}")
        return None


def get_daily_returns(symbols: list, period: str = "1y") -> pd.DataFrame:
    """여러 종목의 일간 수익률 데이터 가져오기"""
    returns_data = {}
    
    for symbol in symbols:
        df = get_stock_data(symbol, period)
        if df is not None:
            # 일간 수익률 계산
            returns = df['Close'].pct_change().dropna()
            returns_data[symbol] = returns
    
    if returns_data:
        # 모든 종목의 수익률을 하나의 데이터프레임으로 결합
        returns_df = pd.DataFrame(returns_data)
        return returns_df
    
    return None


def calculate_portfolio_metrics(data: dict, exchange_rate: float = None) -> dict:
    """포트폴리오 지표 계산"""
    if not data:  # 데이터가 비어있는 경우 처리
        return {
            "total": 0,
            "weights": {},
            "total_krw": 0
        }
    
    # 원화로 변환된 총 자산 계산
    total_krw = 0
    for item in data.values():
        amount = float(item.get('amount', 0))
        currency = item.get('currency', 'KRW')
        if currency == 'USD':
            # USD 자산의 경우 원화로 환산
            purchase_rate = float(item.get('purchase_exchange_rate', 1300.0))
            total_krw += convert_to_krw(amount, currency, purchase_rate)
        else:
            total_krw += amount
    
    # 현재 가치 계산 (USD 자산은 현재 환율 적용)
    current_total_krw = 0
    for item in data.values():
        amount = float(item.get('current_amount', item.get('amount', 0)))
        currency = item.get('currency', 'KRW')
        if currency == 'USD':
            current_total_krw += convert_to_krw(amount, currency, exchange_rate)
        else:
            current_total_krw += amount
    
    # 비중 계산
    if current_total_krw == 0:  # 0으로 나누기 방지
        weights = {k: 0 for k in data.keys()}
    else:
        weights = {}
        for k, v in data.items():
            amount = float(v.get('current_amount', v.get('amount', 0)))
            currency = v.get('currency', 'KRW')
            if currency == 'USD':
                krw_amount = convert_to_krw(amount, currency, exchange_rate)
            else:
                krw_amount = amount
            weights[k] = (krw_amount / current_total_krw) * 100
    
    return {
        "total": total_krw,  # 매입금액 기준 총 자산
        "total_krw": current_total_krw,  # 현재가치 기준 총 자산
        "weights": weights
    }


def calculate_portfolio_risk(returns: pd.DataFrame, weights: np.array) -> float:
    """포트폴리오 리스크(표준편차) 계산"""
    cov_matrix = returns.cov() * 252  # 연간 공분산 행렬
    portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
    return np.sqrt(portfolio_var)


def optimize_portfolio(returns: pd.DataFrame, target_return: float = None) -> dict:
    """포트폴리오 최적화"""
    n_assets = returns.shape[1]
    
    # 초기 가중치 설정
    init_weights = np.array([1/n_assets] * n_assets)
    
    # 제약조건 설정
    bounds = tuple((0, 1) for _ in range(n_assets))
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # 가중치 합 = 1
    ]
    
    if target_return is not None:
        mean_returns = returns.mean() * 252  # 연간 수익률
        constraints.append({
            'type': 'eq',
            'fun': lambda x: np.sum(mean_returns * x) - target_return
        })
    
    # 최적화
    result = minimize(
        lambda w: calculate_portfolio_risk(returns, w),
        init_weights,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if result.success:
        optimized_weights = result.x
        optimized_risk = calculate_portfolio_risk(returns, optimized_weights)
        mean_returns = returns.mean() * 252
        expected_return = np.sum(mean_returns * optimized_weights)
        
        return {
            'weights': dict(zip(returns.columns, optimized_weights)),
            'risk': optimized_risk,
            'expected_return': expected_return
        }
    return None


def calculate_investment_metrics(data: dict, exchange_rate: float) -> dict:
    """투자 포트폴리오 지표 계산"""
    if not data:
        return {
            "total_investment": 0,
            "total_value": 0,
            "total_profit": 0,
            "total_profit_rate": 0
        }
    
    total_investment_krw = 0  # 총 투자금액 (현재 환율 기준)
    total_value_krw = 0      # 총 평가금액 (현재 환율 기준)
    
    for item in data.values():
        # 투자금액 계산
        amount = float(item.get('amount', 0))
        currency = item.get('currency', 'KRW')
        if currency == 'USD':
            total_investment_krw += amount * exchange_rate
        else:
            total_investment_krw += amount
        
        # 평가금액 계산
        current_amount = float(item.get('current_amount', amount))
        if currency == 'USD':
            total_value_krw += current_amount * exchange_rate
        else:
            total_value_krw += current_amount
    
    # 수익금액과 수익률 계산
    total_profit = total_value_krw - total_investment_krw
    total_profit_rate = (total_profit / total_investment_krw * 100) if total_investment_krw > 0 else 0
    
    return {
        "total_investment": total_investment_krw,
        "total_value": total_value_krw,
        "total_profit": total_profit,
        "total_profit_rate": total_profit_rate
    }


def calculate_krw_amount(amount: float, currency: str, exchange_rate: float) -> float:
    """금액을 원화로 환산"""
    if currency == "USD":
        return amount * exchange_rate
    return amount


def render_portfolio_page():
    st.title("💼 포트폴리오 관리")
    
    # 데이터 핸들러 초기화
    data_handler = FinanceDataHandler()
    
    # 현재 환율 정보 가져오기
    current_exchange_rate = get_current_exchange_rate()
    
    # 현재 환율 정보 표시
    st.sidebar.markdown("### 💱 환율 정보")
    st.sidebar.metric(
        "USD/KRW",
        f"₩{current_exchange_rate:,.2f}",
        help="실시간 달러/원 환율"
    )
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs([
        "📝 자산 배분",
        "📊 포트폴리오 분석",
        "🎯 포트폴리오 최적화"
    ])
    
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
                    currency = st.selectbox(
                        f"{asset_type} 통화",
                        ["KRW", "USD"],
                        key=f"currency_{asset_type}"
                    )
                    
                    amount = st.number_input(
                        f"{asset_type} 금액 ({currency})",
                        min_value=0.0,
                        value=0.0,
                        step=1000.0,
                        key=f"asset_{asset_type}",
                        help=f"{asset_type}에 투자된 금액을 입력하세요"
                    )
                    
                    if currency == "USD":
                        purchase_rate = st.number_input(
                            f"{asset_type} 매입 환율",
                            min_value=800.0,
                            max_value=2000.0,
                            value=current_exchange_rate,
                            step=0.1,
                            key=f"rate_{asset_type}",
                            help="매입 당시의 환율을 입력하세요"
                        )
                        
                        # 원화 환산 금액 표시
                        krw_amount = amount * purchase_rate
                        st.caption(f"₩{krw_amount:,.0f} (매입 환율 기준)")
                        
                        current_krw = amount * current_exchange_rate
                        st.caption(f"₩{current_krw:,.0f} (현재 환율 기준)")
                    
                    asset_data[asset_type] = {
                        'amount': amount,
                        'currency': currency,
                        'purchase_exchange_rate': purchase_rate if currency == "USD" else None
                    }
            
            # 오른쪽 열에 자산 유형 4~6
            with col2:
                for asset_type in asset_types[3:]:
                    currency = st.selectbox(
                        f"{asset_type} 통화",
                        ["KRW", "USD"],
                        key=f"currency_{asset_type}"
                    )
                    
                    amount = st.number_input(
                        f"{asset_type} 금액 ({currency})",
                        min_value=0.0,
                        value=0.0,
                        step=1000.0,
                        key=f"asset_{asset_type}",
                        help=f"{asset_type}에 투자된 금액을 입력하세요"
                    )
                    
                    if currency == "USD":
                        purchase_rate = st.number_input(
                            f"{asset_type} 매입 환율",
                            min_value=800.0,
                            max_value=2000.0,
                            value=current_exchange_rate,
                            step=0.1,
                            key=f"rate_{asset_type}",
                            help="매입 당시의 환율을 입력하세요"
                        )
                        
                        # 원화 환산 금액 표시
                        krw_amount = amount * purchase_rate
                        st.caption(f"₩{krw_amount:,.0f} (매입 환율 기준)")
                        
                        current_krw = amount * current_exchange_rate
                        st.caption(f"₩{current_krw:,.0f} (현재 환율 기준)")
                    
                    asset_data[asset_type] = {
                        'amount': amount,
                        'currency': currency,
                        'purchase_exchange_rate': purchase_rate if currency == "USD" else None
                    }
            
            # 포트폴리오 지표 계산
            metrics = calculate_portfolio_metrics(asset_data, current_exchange_rate)
            
            # 총 자산 계산 및 표시
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "💰 총 투자금액",
                    f"₩{metrics['total']:,.0f}",
                    help="매입 환율 기준 전체 포트폴리오 가치"
                )
            with col2:
                st.metric(
                    "💵 총 평가금액",
                    f"₩{metrics['total_krw']:,.0f}",
                    help="현재 환율 기준 전체 포트폴리오 가치"
                )
            
            # 저장 버튼
            submit_portfolio = st.form_submit_button(
                "자산 배분 저장",
                use_container_width=True
            )
            
            if submit_portfolio:
                if data_handler.save_portfolio(asset_data):
                    st.success("✅ 자산 배분이 저장되었습니다.")
                else:
                    st.error("❌ 자산 배분 저장에 실패했습니다.")
    
    with tab2:
        st.markdown("### 포트폴리오 분석")
        
        # 자산 데이터 로드
        portfolio_data = data_handler.load_portfolio()
        investment_data = data_handler.load_investment()
        
        if investment_data:
            # 투자 포트폴리오 지표 계산
            investment_metrics = calculate_investment_metrics(
                investment_data,
                current_exchange_rate
            )
            
            # 포트폴리오 요약
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 총 투자금액",
                    f"₩{investment_metrics['total_investment']:,.0f}",
                    help="현재 환율 기준 전체 투자금액"
                )
            
            with col2:
                st.metric(
                    "💵 총 평가금액",
                    f"₩{investment_metrics['total_value']:,.0f}",
                    help="현재 환율 기준 전체 평가금액"
                )
            
            with col3:
                profit = investment_metrics['total_profit']
                profit_rate = investment_metrics['total_profit_rate']
                
                # 수익/손실 표시
                st.metric(
                    "💹 총 손익",
                    f"₩{profit:,.0f}",
                    help="현재 환율 기준 총 손익"
                )
                
                # 수익률 별도 표시
                if profit >= 0:
                    st.markdown("📈 수익률: " + f"+{profit_rate:.1f}%")
                else:
                    st.markdown("📉 수익률: " + f"{profit_rate:.1f}%")
            
            with col4:
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
                labels=list(investment_data.keys()),
                values=[
                    convert_to_krw(
                        float(v.get('current_amount', v.get('amount', 0))),
                        v.get('currency', 'KRW'),
                        current_exchange_rate
                    ) for v in investment_data.values()
                ],
                title="자산 배분 현황 (현재 환율 기준)"
            )
            st.plotly_chart(pie_chart, use_container_width=True)
            
            # 자산 배분 상세
            st.markdown("### 📋 자산 배분 상세")
            
            # 데이터프레임 생성을 위한 데이터 준비
            df_data = []
            for key, value in investment_data.items():
                amount = float(value.get('amount', 0))
                current_amount = float(value.get('current_amount', amount))
                currency = value.get('currency', 'KRW')
                
                # 원화 환산 금액 계산
                krw_amount = convert_to_krw(amount, currency, current_exchange_rate)
                krw_current = convert_to_krw(current_amount, currency, current_exchange_rate)
                
                # 수익률 계산
                profit_rate = ((current_amount / amount) - 1) * 100 if amount > 0 else 0
                
                df_data.append({
                    "자산명": value.get('name', key),
                    "종목코드": value.get('symbol', ''),
                    "통화": currency,
                    "매입금액": f"{currency} {amount:,.2f}",
                    "평가금액": f"{currency} {current_amount:,.2f}",
                    "원화 환산 매입": f"₩{krw_amount:,.0f}",
                    "원화 환산 평가": f"₩{krw_current:,.0f}",
                    "수익률": f"{profit_rate:+.1f}%"
                })
            
            # 데이터프레임 생성
            investment_df = pd.DataFrame(df_data)
            
            # 스타일 함수 정의
            def style_negative_profits(val):
                try:
                    profit = float(val.strip('%').strip('+'))
                    return 'color: red' if profit < 0 else 'color: green' if profit > 0 else ''
                except ValueError:
                    return ''
            
            # 스타일이 적용된 데이터프레임 표시
            styled_df = investment_df.style.applymap(
                style_negative_profits,
                subset=['수익률']
            )
            st.dataframe(styled_df, use_container_width=True)
            
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
                diff = target_weight - current_weight
                
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
            
            # 현재 자산 비중 계산
            current_allocation = {}
            for item in investment_data.values():
                current_amount = float(item.get('current_amount', item.get('amount', 0)))
                currency = item.get('currency', 'KRW')
                inv_type = item.get('type', '기타')
                
                if currency == 'USD':
                    # USD 자산의 경우 원화로 환산
                    current_rate = float(item.get('current_exchange_rate', current_exchange_rate))
                    krw_amount = current_amount * current_rate
                else:
                    krw_amount = current_amount
                
                current_allocation[inv_type] = current_allocation.get(inv_type, 0) + krw_amount
            
            # 전체 포트폴리오 가치 계산
            total_portfolio_value = sum(current_allocation.values())
            
            # 현재 비중을 퍼센트로 변환
            if total_portfolio_value > 0:
                for asset_type in current_allocation:
                    current_allocation[asset_type] = (current_allocation[asset_type] / total_portfolio_value) * 100
            
            # 리밸런싱이 필요한 항목 필터링
            rebalance_needed = []
            for asset_type in asset_types:
                current_weight = current_allocation.get(asset_type, 0)
                target_weight = target_allocation.get(asset_type, 0)
                diff = target_weight - current_weight
                
                rebalance_needed.append({
                    "자산 유형": asset_type,
                    "현재 비중": f"{current_weight:.1f}%",
                    "목표 비중": f"{target_weight:.1f}%",
                    "조정 필요": f"{diff:+.1f}%"
                })
            
            # 리밸런싱 제안 표시
            if rebalance_needed:
                rebalance_df = pd.DataFrame(rebalance_needed)
                st.dataframe(
                    rebalance_df.style.applymap(
                        color_adjustment,
                        subset=["조정 필요"]
                    ),
                    use_container_width=True
                )
                
                st.markdown("#### 💰 금액 기준 리밸런싱 제안")
                for item in rebalance_needed:
                    diff = float(item["조정 필요"].strip("%").strip("+"))
                    if abs(diff) >= 5:  # 5% 이상 차이나는 경우만 표시
                        action = "매수" if diff > 0 else "매도"
                        amount = abs(diff) * total_portfolio_value / 100
                        st.write(
                            f"- {item['자산 유형']}: {action} "
                            f"₩{amount:,.0f} ({diff:+.1f}%)"
                        )
            else:
                st.info("포트폴리오 데이터가 없습니다.")
    
    with tab3:
        st.markdown("### 🎯 포트폴리오 최적화")
        
        # investments.py의 데이터 로드
        investment_data = data_handler.load_investment()
        
        if investment_data:
            # 투자 데이터를 데이터프레임으로 변환
            investments_df = pd.DataFrame.from_dict(
                investment_data,
                orient='index'
            )
            
            # 자산별 현재 비중 계산 (원화 환산 기준)
            total_krw_value = 0
            krw_values = []
            
            for _, row in investments_df.iterrows():
                current_amount = float(row.get('current_amount', row.get('amount', 0)))
                currency = row.get('currency', 'KRW')
                exchange_rate = float(row.get('current_exchange_rate', 1.0))
                
                # 원화로 환산
                krw_value = calculate_krw_amount(current_amount, currency, exchange_rate)
                krw_values.append(krw_value)
                total_krw_value += krw_value
            
            # 원화 환산 비중 계산
            current_weights = pd.Series(krw_values, index=investments_df.index) / total_krw_value
            
            st.markdown("#### 현재 포트폴리오 구성 (원화 환산 기준)")
            weights_df = pd.DataFrame({
                '자산': investments_df['name'],
                '현재 비중': current_weights.map(lambda x: f"{x*100:.1f}%"),
                '원화 환산 금액': [f"₩{v:,.0f}" for v in krw_values]
            })
            st.dataframe(weights_df)
            
            # 최적화 설정
            st.markdown("#### 포트폴리오 최적화 설정")
            
            # 기간 선택
            period_options = {
                "1개월": "1mo",
                "3개월": "3mo",
                "6개월": "6mo",
                "1년": "1y",
                "2년": "2y",
                "5년": "5y"
            }
            selected_period = st.selectbox(
                "분석 기간",
                options=list(period_options.keys()),
                index=3,  # 기본값: 1년
                help="과거 데이터 분석 기간을 선택하세요"
            )
            
            target_return = st.slider(
                "목표 연간 수익률",
                min_value=0.0,
                max_value=30.0,
                value=10.0,
                step=0.5,
                help="원하는 연간 목표 수익률을 설정하세요"
            ) / 100
            
            if st.button("포트폴리오 최적화 실행"):
                with st.spinner("시장 데이터를 가져오는 중..."):
                    # 종목 코드 추출
                    symbols = investments_df['symbol'].dropna().tolist()
                    
                    if not symbols:
                        st.warning(
                            "분석 가능한 종목이 없습니다. "
                            "먼저 종목 코드를 입력해주세요."
                        )
                    else:
                        # 실제 시장 데이터 가져오기
                        returns = get_daily_returns(
                            symbols,
                            period_options[selected_period]
                        )
                        
                        if returns is not None and not returns.empty:
                            # 최적화 실행
                            optimization_result = optimize_portfolio(
                                returns,
                                target_return
                            )
                            
                            if optimization_result:
                                st.markdown("#### 최적화 결과")
                                
                                # 결과 표시
                                result_df = pd.DataFrame({
                                    '자산': list(
                                        optimization_result['weights'].keys()
                                    ),
                                    '최적 비중': [
                                        f"{w*100:.1f}%"
                                        for w in optimization_result[
                                            'weights'
                                        ].values()
                                    ],
                                    '현재 비중': current_weights[
                                        investments_df['symbol'].isin(symbols)
                                    ].map(lambda x: f"{x*100:.1f}%")
                                })
                                
                                st.dataframe(result_df)
                                
                                # 리스크와 기대수익률 표시
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric(
                                        "예상 연간 수익률",
                                        f"{optimization_result['expected_return']*100:.1f}%"
                                    )
                                with col2:
                                    st.metric(
                                        "포트폴리오 리스크",
                                        f"{optimization_result['risk']*100:.1f}%"
                                    )
                                
                                # 상관관계 분석
                                st.markdown("#### 자산 간 상관관계")
                                corr_matrix = returns.corr()
                                st.dataframe(
                                    corr_matrix.style.background_gradient(
                                        cmap='RdYlGn',
                                        vmin=-1,
                                        vmax=1
                                    )
                                )
                                
                                # 리밸런싱 제안
                                st.markdown("#### 📋 리밸런싱 제안")
                                for asset, opt_weight in optimization_result[
                                    'weights'
                                ].items():
                                    current_w = current_weights[
                                        investments_df['symbol'] == asset
                                    ].iloc[0]
                                    diff = (opt_weight - current_w) * 100
                                    if abs(diff) >= 1:  # 1% 이상 차이나는 경우만 표시
                                        action = "매수" if diff > 0 else "매도"
                                        amount = abs(diff) * total_krw_value / 100
                                        st.write(
                                            f"- {asset}: {action} "
                                            f"₩{amount:,.0f} ({diff:+.1f}%)"
                                        )
                            else:
                                st.error(
                                    "포트폴리오 최적화에 실패했습니다. "
                                    "다른 목표 수익률을 시도해보세요."
                                )
                        else:
                            st.error(
                                "시장 데이터를 가져오는데 실패했습니다. "
                                "종목 코드를 확인해주세요."
                            )
        else:
            st.warning("투자 데이터가 없습니다. 먼저 투자 정보를 입력해주세요.") 
