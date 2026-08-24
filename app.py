import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io

# --- 폰트 및 모의고사 스타일 기본 설정 ---
# 수학 기호(x, y 등)를 교과서/모의고사(TeX) 스타일로 변경
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Hancom Batang' # 한컴바탕 우선 적용 (없으면 기본 바탕체)
plt.rcParams['font.size'] = 11

st.set_page_config(page_title="고등 수학 모의고사 그래프 생성기", page_icon="📐", layout="wide")

st.title("📐 고등 수학 모의고사 흑백 그래프 생성기")
st.write("시험지(한글, 워드)에 바로 복사해서 쓸 수 있는 고품질 흑백 그래프입니다.")

# 1. 카테고리 선택
categories = [
    "일차함수", "이차함수", "유리함수", "무리함수", 
    "지수함수", "로그함수", 
    "삼각함수: 사인(sin)", "삼각함수: 코사인(cos)", "삼각함수: 탄젠트(tan)",
    "미적분: 다항함수 (구간별 정의/불연속)", "미적분: 초월함수 (구간별 정의/불연속)", 
    "정적분함수 (넓이 색칠)"
]
category = st.selectbox("과목 및 단원 선택", categories)

# 수식 안전 평가 함수 (파이썬 코드를 numpy 수식으로 변환)
def safe_eval(expr_str, x_array):
    expr = expr_str.replace('^', '**')
    allowed = {
        'x': x_array, 'np': np, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'exp': np.exp, 'log': np.log, 'ln': np.log, 'sqrt': np.sqrt,
        'pi': np.pi, 'e': np.e, 'abs': np.abs
    }
    try:
        return eval(expr, {"__builtins__": {}}, allowed)
    except Exception as e:
        return np.zeros_like(x_array)

st.subheader("그래프 세부 설정")
col_left, col_right = st.columns([1, 1.5])

with col_left:
    fig, ax = plt.subplots(figsize=(5, 5))
    x_min, x_max = -5.0, 5.0  # 기본 x축 범위
    x = np.linspace(x_min, x_max, 1000)
    y = np.full_like(x, np.nan) # 기본 y값은 빈 값으로 시작

    # --- 카테고리별 함수 설정 ---
    if category == "일차함수":
        a = st.number_input("기울기 (a)", value=1.0)
        b = st.number_input("y절편 (b)", value=0.0)
        y = a * x + b
        ax.plot(x, y, 'black', linewidth=1.5)

    elif category == "이차함수":
        a = st.number_input("최고차항 (a)", value=1.0)
        p = st.number_input("꼭짓점 x (p)", value=0.0)
        q = st.number_input("꼭짓점 y (q)", value=0.0)
        y = a * (x - p)**2 + q
        ax.plot(x, y, 'black', linewidth=1.5)

    elif category == "유리함수":
        k = st.number_input("분자 (k)", value=1.0)
        p = st.number_input("x 점근선 (p)", value=1.0)
        q = st.number_input("y 점근선 (q)", value=1.0)
        
        y = k / (x - p) + q
        y[np.abs(x - p) < 0.1] = np.nan # 점근선에서 선이 이어지는 현상 방지
        ax.plot(x, y, 'black', linewidth=1.5)
        
        if st.checkbox("점근선 표시", value=True):
            ax.axvline(x=p, color='black', linestyle='--', linewidth=1)
            ax.axhline(y=q, color='black', linestyle='--', linewidth=1)

    elif category == "무리함수":
        a = st.number_input("계수 a", value=1.0)
        b = st.number_input("부호 b", value=1.0)
        p = st.number_input("시작점 x (p)", value=0.0)
        q = st.number_input("시작점 y (q)", value=0.0)
        
        valid_x = b * (x - p) >= 0
        y[valid_x] = a * np.sqrt(b * (x[valid_x] - p)) + q
        ax.plot(x, y, 'black', linewidth=1.5)
        ax.plot(p, q, 'ko', markersize=4)

    elif category == "지수함수":
        a = st.number_input("밑", value=2.0)
        y = a ** x
        ax.plot(x, y, 'black', linewidth=1.5)

    elif category == "로그함수":
        a = st.number_input("밑 (a > 0, a != 1)", value=2.0)
        valid_x = x > 0
        y[valid_x] = np.log(x[valid_x]) / np.log(a)
        ax.plot(x, y, 'black', linewidth=1.5)
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1) # 점근선

    elif "삼각함수" in category:
        a = st.number_input("진폭 (a)", value=1.0)
        b = st.number_input("주기 관련 (b)", value=1.0)
        if "사인" in category:
            y = a * np.sin(b * x)
        elif "코사인" in category:
            y = a * np.cos(b * x)
        elif "탄젠트" in category:
            y = a * np.np.tan(b * x)
            # 탄젠트 점근선 끊기
            y[np.abs(np.cos(b * x)) < 0.1] = np.nan
        ax.plot(x, y, 'black', linewidth=1.5)

    elif "미적분" in category:
        st.write("💡 **구간별 함수 (불연속 함수) 설정**")
        num_pieces = st.slider("구간 개수", 1, 4, 2)
        
        for i in range(num_pieces):
            st.markdown(f"**구간 {i+1}**")
            c1, c2 = st.columns(2)
            with c1:
                cond = st.text_input(f"조건 (예: x < 0, x >= 0)", value="x < 0" if i==0 else "x >= 0", key=f"cond_{i}")
            with c2:
                expr = st.text_input(f"함수식 (예: x**2, sin(x))", value="x**2" if i==0 else "x+1", key=f"expr_{i}")
            
            # 조건 파싱 및 함수 적용
            try:
                condition_mask = eval(cond, {"x": x, "np": np})
                y[condition_mask] = safe_eval(expr, x[condition_mask])
            except:
                pass
        
        ax.plot(x, y, 'black', linewidth=1.5)

    elif category == "정적분함수 (넓이 색칠)":
        expr = st.text_input("함수식 입력 (예: -x**2 + 4, x**3 - x)", value="-x**2 + 4")
        y = safe_eval(expr, x)
        ax.plot(x, y, 'black', linewidth=1.5)
        
        st.write("💡 **적분 구간 설정**")
        c1, c2 = st.columns(2)
        with c1:
            a_val = st.number_input("아래끝 (a)", value=-1.0)
        with c2:
            b_val = st.number_input("위끝 (b)", value=2.0)
        
        # 색칠하기 로직
        x_fill = np.linspace(a_val, b_val, 200)
        y_fill = safe_eval(expr, x_fill)
        ax.fill_between(x_fill, y_fill, 0, color='gray', alpha=0.3)
        
        # a, b 텍스트 표시
        ax.text(a_val, -0.5, f"{a_val:g}", ha='center', va='top', fontsize=11)
        ax.text(b_val, -0.5, f"{b_val:g}", ha='center', va='top', fontsize=11)

    # --- 공통 축 디자인 (모의고사 스타일 완벽 재현) ---
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

    # x, y 폰트를 수학 기호체(TeX)로 예쁘게 출력
    ax.text(1.05, 0, r'$x$', transform=ax.get_yaxis_transform(), ha='left', va='center', fontsize=13)
    ax.text(0, 1.05, r'$y$', transform=ax.get_xaxis_transform(), ha='center', va='bottom', fontsize=13)
    ax.text(-0.05, -0.05, r'$O$', transform=ax.transAxes, ha='right', va='top', fontsize=12)

    # 기본 눈금 제거 및 범위 최적화
    ax.set_xticks([])
    ax.set_yticks([])
    
    # y축 범위 자동 조절 (극한값 튀는 현상 방지)
    valid_y = y[~np.isnan(y)]
    if len(valid_y) > 0:
        ymin, ymax = np.min(valid_y), np.max(valid_y)
        if ymax - ymin > 20: # 변동이 너무 큰 경우 (유리/탄젠트 등)
            ax.set_ylim(-10, 10)

with col_right:
    st.pyplot(fig)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=400, bbox_inches="tight", transparent=True)
    st.download_button(
        label="📥 시험지용 고화질 그래프 다운로드 (PNG)",
        data=buf.getvalue(),
        file_name="math_graph_advanced.png",
        mime="image/png"
    )
    st.info("💡 다운로드한 이미지는 한글(HWP)이나 Word 시험지에 드래그해서 넣으면 배경이 투명하여 아주 깔끔하게 들어갑니다.")
