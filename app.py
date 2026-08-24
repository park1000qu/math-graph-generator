import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io

# 페이지 기본 설정
st.set_page_config(page_title="고등 수학 시험용 그래프 생성기", page_icon="📐", layout="centered")

st.title("📐 고등 수학 모의고사 스타일 그래프 생성기")
st.write("시험지나 학습지에 바로 사용할 수 있는 흑백 수능/내신 양식의 그래프를 생성합니다.")

# 1. 카테고리 선택
category = st.selectbox(
    "과목 및 단원 선택",
    ["공통수학2: 유리함수", "공통수학2: 무리함수", "공통수학1: 이차함수", "수학I: 지수함수/로그함수", "수학II: 다항함수의 극값"]
)

# 2. 파라미터 입력 및 설정
st.subheader("그래프 세부 설정")

fig, ax = plt.subplots(figsize=(6, 6))

if category == "공통수학2: 유리함수":
    st.markdown("**기본형: $y = \\frac{k}{x-p} + q$**")
    col1, col2, col3 = st.columns(3)
    with col1:
        k = st.number_input("분자 (k)", value=2.0, step=0.5)
    with col2:
        p = st.number_input("x 점근선 (p)", value=1.0, step=0.5)
    with col3:
        q = st.number_input("y 점근선 (q)", value=1.0, step=0.5)
    
    show_asymptote = st.checkbox("점근선 표시 (점선)", value=True)

    # 그래프 그리기
    x1 = np.linspace(p - 6, p - 0.05, 300)
    x2 = np.linspace(p + 0.05, p + 6, 300)
    ax.plot(x1, k / (x1 - p) + q, 'black', linewidth=1.5)
    ax.plot(x2, k / (x2 - p) + q, 'black', linewidth=1.5)

    if show_asymptote:
        ax.axvline(x=p, color='black', linestyle='--', linewidth=1)
        ax.axhline(y=q, color='black', linestyle='--', linewidth=1)
        # 점근선 수치 표시
        if p != 0:
            ax.text(p, -0.6, f"{p:g}", ha='center', va='top', fontsize=11, fontfamily='serif')
        if q != 0:
            ax.text(-0.6, q, f"{q:g}", ha='right', va='center', fontsize=11, fontfamily='serif')

elif category == "공통수학2: 무리함수":
    st.markdown("**기본형: $y = a\\sqrt{b(x-p)} + q$**")
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("계수 a", value=1.0, step=0.5)
        p = st.number_input("시작점 x (p)", value=1.0, step=0.5)
    with col2:
        b = st.number_input("부호 b", value=1.0, step=1.0)
        q = st.number_input("시작점 y (q)", value=-1.0, step=0.5)

    if b > 0:
        x = np.linspace(p, p + 7, 300)
    else:
        x = np.linspace(p - 7, p, 300)
    
    y = a * np.sqrt(np.maximum(0, b * (x - p))) + q
    ax.plot(x, y, 'black', linewidth=1.5)
    ax.plot(p, q, 'ko', markersize=4) # 시작점 표시

else:
    # 다른 함수 기본 예시 (이차함수 등)
    x = np.linspace(-4, 4, 300)
    ax.plot(x, x**2 - 2, 'black', linewidth=1.5)

# --- 한국 시험지 스타일 축 디자인 공통 적용 ---
ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')

# 축 화살표 설정
ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

# 축 라벨 ($x$, $y$, 원점 $O$)
ax.text(ax.get_xlim()[1]*1.03, 0, r'$x$', ha='left', va='center', fontsize=13, fontfamily='serif')
ax.text(0, ax.get_ylim()[1]*1.03, r'$y$', ha='center', va='bottom', fontsize=13, fontfamily='serif')
ax.text(-0.5, -0.6, r'$O$', ha='right', va='top', fontsize=13, fontfamily='serif')

# 기본 눈금 제거 (시험지 스타일)
ax.set_xticks([])
ax.set_yticks([])

st.pyplot(fig)

# 이미지 다운로드 버튼
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
st.download_button(
    label="📥 시험지용 고화질 그래프 다운로드 (PNG)",
    data=buf.getvalue(),
    file_name="math_graph.png",
    mime="image/png"
)
