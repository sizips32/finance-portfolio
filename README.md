# Personal Finance Portfolio Web App

## 개요

이 웹 애플리케이션은 개인 재무 관리를 위한 종합적인 포트폴리오 도구입니다. Streamlit을 활용한 대시보드를 통해 수입, 지출, 투자, 자산 배분 등을 한눈에 파악하고 관리할 수 있습니다.

## 주요 기능

- 대시보드: 개인 재무 흐름 요약 및 시각화
- 수입/지출 관리: 상세한 수입과 지출 내역 입력 및 분석
- 예산 설정: 예산 목표 설정 및 추적
- 투자 관리: 투자 항목 입력 및 성과 시각화
- 포트폴리오 관리: 자산 배분 및 전체 포트폴리오 관리

## 기술 스택

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Streamlit
- 데이터 시각화: Plotly, Pandas

## 설치 방법

1. 저장소 클론

```bash
git clone https://github.com/yourusername/finance-portfolio.git
cd finance-portfolio
```

2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

4. 애플리케이션 실행

```bash
streamlit run app/main.py
```

## 프로젝트 구조

```
finance-portfolio/
├── README.md
├── requirements.txt
├── app/
│   ├── main.py
│   ├── pages/
│   ├── utils/
│   └── static/
└── data/
```

## 라이선스

MIT License

## 기여 방법

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request
