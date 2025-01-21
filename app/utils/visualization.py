import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import pandas as pd


def create_pie_chart(
    labels: List[str],
    values: List[float],
    title: str = "자산 분배"
) -> go.Figure:
    """원형 차트 생성"""
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3
    )])
    fig.update_layout(title=title)
    return fig


def create_line_chart(
    dates: List,
    values: List[float],
    title: str = "추세",
    name: str = "값"
) -> go.Figure:
    """선 그래프 생성"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        name=name
    ))
    fig.update_layout(title=title)
    return fig


def create_bar_chart(
    categories: List[str],
    values: List[float],
    title: str = "카테고리별 분석"
) -> go.Figure:
    """막대 그래프 생성"""
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values
    )])
    fig.update_layout(title=title)
    return fig


def create_income_expense_chart(
    dates: List,
    income: List[float],
    expenses: List[float]
) -> go.Figure:
    """수입/지출 비교 차트 생성"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=income,
        name="수입"
    ))
    fig.add_trace(go.Scatter(
        x=dates,
        y=expenses,
        name="지출"
    ))
    fig.update_layout(
        title="수입/지출 추이",
        yaxis_title="금액 (원)",
        xaxis_title="날짜"
    )
    return fig


def create_budget_progress_chart(
    categories: List[str],
    planned: List[float],
    actual: List[float]
) -> go.Figure:
    """예산 진행 상황 차트 생성"""
    fig = go.Figure(data=[
        go.Bar(name="계획", x=categories, y=planned),
        go.Bar(name="실제", x=categories, y=actual)
    ])
    fig.update_layout(
        title="예산 진행 상황",
        barmode="group",
        yaxis_title="금액 (원)"
    )
    return fig


def create_investment_performance_chart(
    dates: List,
    performance: List[float],
    benchmark: List[float] = None
) -> go.Figure:
    """투자 성과 차트 생성"""
    fig = go.Figure()
    
    # 투자 성과 라인
    fig.add_trace(go.Scatter(
        x=dates,
        y=performance,
        name="포트폴리오 성과"
    ))
    
    # 벤치마크가 있는 경우 추가
    if benchmark is not None:
        fig.add_trace(go.Scatter(
            x=dates,
            y=benchmark,
            name="벤치마크",
            line=dict(dash="dash")
        ))
    
    fig.update_layout(
        title="투자 성과 추이",
        yaxis_title="수익률 (%)",
        xaxis_title="날짜"
    )
    return fig 
