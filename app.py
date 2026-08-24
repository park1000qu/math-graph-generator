import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import io

# --- 기본 폰트 및 설정 ---
plt.rcParams['mathtext.fontset'] = 'stix'
# 한컴바탕이 없을 경우를 대비해 윈도우/맥 기본 폰트 순차 적용
plt.rcParams['font.family'] = ['Hancom Batang', 'Batang', 'Malgun Gothic', 'AppleGothic', 'sans-serif']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

st.set_page_config(page_title="수학 모의고사 그래프 생성기", page_icon="📐", layout="wide")
st.title("📐 고등 수학 모의고사 흑백 그래프 생성기")

categories = [
    "일차함수", "이차함수", "유리함수", "무리함수", 
    "지수함수", "로그함수", 
    "삼각함수: 사인(sin)", "삼각함수: 코사인(cos)", "삼각함수: 탄젠트(tan)",
    "미적분: 구간별 정의 함수 (불연속/극한)", "정적분함수 (넓이 색칠)"
]
category = st.selectbox("과목 및 단원 선택", categories)

st.divider()
col_left, col_right = st.columns([1.2, 1])
x_sym = sp.Symbol('x') # Sympy 수식 계산용 심볼

with col_left:
    st.subheader("그래프 세부 설정")
    fig, ax = plt.subplots(figsize=(5, 5))
    x_default = np.linspace(-6, 6, 1000)
    
    if category == "일차함수":
        st.latex(r"y = ax + b")
        c1, c2 = st.columns(2)
        with c1: a = st.number_input("기울기 (a)", value=1.0)
        with c2: b = st.number_input("y절편 (b)", value=0.0)
        ax.plot(x_default, a * x_default + b, 'black', linewidth=1.5)

    elif category == "이차함수":
        st.latex(r"y = a(x - p)^2 + q")
        c1, c2, c3 = st.columns(3)
        with c1: a = st.number_input("최고차항 계수 (a)", value=1.0)
        with c2: p = st.number_input("꼭짓점 x (p)", value=0.0)
        with c3: q = st.number_input("꼭짓점 y (q)", value=0.0)
        ax.plot(x_default, a * (x_default - p)**2 + q, 'black', linewidth=1.5)

    elif category == "유리함수":
        st.latex(r"y = \frac{k}{x - p} + q")
        c1, c2, c3 = st.columns(3)
        with c1: k = st.number_input("분자 (k)", value=1.0)
        with c2: p = st.number_input("x 점근선 (p)", value=1.0)
        with c3: q = st.number_input("y 점근선 (q)", value=1.0)
        
        y = k / (x_default - p) + q
        y[np.abs(x_default - p) < 0.05] = np.nan # 점근선 잇는 선 끊기
        ax.plot(x_default, y, 'black', linewidth=1.5)
        
        if st.checkbox("점근선 표시", value=True):
            ax.axvline(x=p, color='black', linestyle='--', linewidth=1)
            ax.axhline(y=q, color='black', linestyle='--', linewidth=1)

    elif category == "무리함수":
        st.latex(r"y = a\sqrt{b(x - p)} + q")
        c1, c2 = st.columns(2)
        with c1:
            a = st.number_input("바깥 계수 (a)", value=1.0)
            p = st.number_input("시작점 x (p)", value=0.0)
        with c2:
            b = st.number_input("안쪽 계수 (b)", value=1.0)
            q = st.number_input("시작점 y (q)", value=0.0)
        
        # 시작점에서 그래프가 끊어지지 않도록 p부터 정확히 배열 생성
        if b > 0:
            x_root = np.linspace(p, p + 10, 1000)
        else:
            x_root = np.linspace(p - 10, p, 1000)
        y_root = a * np.sqrt(b * (x_root - p)) + q
        
        ax.plot(x_root, y_root, 'black', linewidth=1.5)
        ax.plot(p, q, 'ko', markersize=5, zorder=5) # 꽉 찬 점 그리기 (zorder로 겹침 방지)

    elif category == "지수함수":
        st.latex(r"y = a^{x - p} + q")
        c1, c2, c3 = st.columns(3)
        with c1: a = st.number_input("밑 (a > 0)", value=2.0)
        with c2: p = st.number_input("x 평행이동 (p)", value=0.0)
        with c3: q = st.number_input("y 평행이동 (q)", value=0.0)
        ax.plot(x_default, a**(x_default - p) + q, 'black', linewidth=1.5)
        ax.axhline(y=q, color='black', linestyle='--', linewidth=1, alpha=0.5)

    elif category == "로그함수":
        st.latex(r"y = \log_a (x - p) + q")
        c1, c2, c3 = st.columns(3)
        with c1: a = st.number_input("밑 (a > 0, a≠1)", value=2.0)
        with c2: p = st.number_input("x 점근선 (p)", value=0.0)
        with c3: q = st.number_input("y 평행이동 (q)", value=0.0)
        
        x_log = np.linspace(p + 0.001, p + 10, 1000)
        y_log = np.log(x_log - p) / np.log(a) + q
        ax.plot(x_log, y_log, 'black', linewidth=1.5)
        ax.axvline(x=p, color='black', linestyle='--', linewidth=1, alpha=0.5)

    elif "삼각함수" in category:
        func_name = category.split()[-1]
        if "sin" in category: st.latex(r"y = a \sin(b(x - p)) + q")
        elif "cos" in category: st.latex(r"y = a \cos(b(x - p)) + q")
        elif "tan" in category: st.latex(r"y = a \tan(b(x - p)) + q")
        
        c1, c2 = st.columns(2)
        with c1:
            a = st.number_input("진폭 (a)", value=1.0)
            p = st.number_input("x 평행이동 (p)", value=0.0)
        with c2:
            b = st.number_input("주기 계수 (b)", value=1.0)
            q = st.number_input("y 평행이동 (q)", value=0.0)
            
        if "sin" in category:
            ax.plot(x_default, a * np.sin(b * (x_default - p)) + q, 'black', linewidth=1.5)
        elif "cos" in category:
            ax.plot(x_default, a * np.cos(b * (x_default - p)) + q, 'black', linewidth=1.5)
        elif "tan" in category:
            y_tan = a * np.tan(b * (x_default - p)) + q
            y_tan[np.abs(np.cos(b * (x_default - p))) < 0.05] = np.nan # 탄젠트 점근선 선 끊기
            ax.plot(x_default, y_tan, 'black', linewidth=1.5)

    elif category == "미적분: 구간별 정의 함수 (불연속/극한)":
        st.write("💡 `sqrt(x)`나 `1/x`, `x**2` 처럼 입력하시면 실시간으로 수식이 예쁘게 변환됩니다.")
        boundary = st.number_input("구간 기준점 (x = c)", value=1.0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**$x < {boundary}$ 일 때**")
            expr_str_L = st.text_input("왼쪽 함수식", value="x**2")
            include_L = st.checkbox(f"x = {boundary} 포함 (≤)", value=False, key="inc_L")
            try:
                expr_sym_L = sp.sympify(expr_str_L)
                st.latex(sp.latex(expr_sym_L))
                f_L = sp.lambdify(x_sym, expr_sym_L, 'numpy')
            except:
                st.error("올바른 수식을 입력하세요.")
                
        with col_left: # 오른쪽 영역을 위한 컨테이너 조정
            pass
        with c2:
            st.markdown(f"**$x > {boundary}$ 일 때**")
            expr_str_R = st.text_input("오른쪽 함수식", value="-x + 3")
            include_R = st.checkbox(f"x = {boundary} 포함 (≥)", value=True, key="inc_R")
            try:
                expr_sym_R = sp.sympify(expr_str_R)
                st.latex(sp.latex(expr_sym_R))
                f_R = sp.lambdify(x_sym, expr_sym_R, 'numpy')
            except:
                st.error("올바른 수식을 입력하세요.")

        try:
            # 왼쪽, 오른쪽 완전히 분리해서 계산 (선이 이어지는 것 방지)
            x_L = np.linspace(-10, boundary, 500)
            x_R = np.linspace(boundary, 10, 500)
            
            y_L = f_L(x_L)
            y_R = f_R(x_R)
            
            # 상수함수일 경우 배열로 변환
            if np.isscalar(y_L): y_L = np.full_like(x_L, y_L)
            if np.isscalar(y_R): y_R = np.full_like(x_R, y_R)

            ax.plot(x_L, y_L, 'black', linewidth=1.5)
            ax.plot(x_R, y_R, 'black', linewidth=1.5)

            # 불연속점 동그라미 (포함: 꽉 찬 점, 불포함: 흰색 속 빈 점)
            val_L, val_R = f_L(boundary), f_R(boundary)
            
            if include_L: ax.plot(boundary, val_L, 'ko', markersize=6, zorder=5)
            else: ax.plot(boundary, val_L, 'ko', markerfacecolor='white', markersize=6, zorder=5)
            
            if include_R: ax.plot(boundary, val_R, 'ko', markersize=6, zorder=5)
            else: ax.plot(boundary, val_R, 'ko', markerfacecolor='white', markersize=6, zorder=5)
        except:
            pass

    elif category == "정적분함수 (넓이 색칠)":
        expr_str = st.text_input("함수식 입력 (예: -x**2 + 4, sqrt(x))", value="-x**2 + 4")
        try:
            expr_sym = sp.sympify(expr_str)
            st.latex(sp.latex(expr_sym)) # 예쁜 수식으로 출력
            f = sp.lambdify(x_sym, expr_sym, 'numpy')
            
            y = f(x_default)
            if np.isscalar(y): y = np.full_like(x_default, y)
            ax.plot(x_default, y, 'black', linewidth=1.5)
            
            st.write("💡 **적분 구간 설정**")
            c1, c2 = st.columns(2)
            with c1: a_val = st.number_input("아래끝 (a)", value=-1.0)
            with c2: b_val = st.number_input("위끝 (b)", value=2.0)
            
            # 색칠하기
            x_fill = np.linspace(a_val, b_val, 300)
            y_fill = f(x_fill)
            if np.isscalar(y_fill): y_fill = np.full_like(x_fill, y_fill)
            
            ax.fill_between(x_fill, y_fill, 0, color='gray', alpha=0.3)
            ax.text(a_val, -0.5, f"{a_val:g}", ha='center', va='top', fontsize=12)
            ax.text(b_val, -0.5, f"{b_val:g}", ha='center', va='top', fontsize=12)
        except:
            st.error("올바른 수식을 입력해주세요.")

    # --- 공통 축 디자인 (모의고사 스타일) ---
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, zorder=10)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, zorder=10)

    ax.text(1.03, 0, r'$x$', transform=ax.get_yaxis_transform(), ha='left', va='center', fontsize=14)
    ax.text(0, 1.03, r'$y$', transform=ax.get_xaxis_transform(), ha='center', va='bottom', fontsize=14)
    ax.text(-0.05, -0.05, r'$O$', transform=ax.transAxes, ha='right', va='top', fontsize=13)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)

with col_right:
    st.pyplot(fig)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=400, bbox_inches="tight", transparent=True)
    st.download_button(
        label="📥 시험지용 고화질 그래프 다운로드 (PNG)",
        data=buf.getvalue(),
        file_name="math_graph_expert.png",
        mime="image/png"
    )
