import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import io

# --- 폰트 및 축 설정 ---
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = ['Hancom Batang', 'Batang', 'Malgun Gothic', 'sans-serif']
plt.rcParams['font.size'] = 12
plt.rcParams['axes.unicode_minus'] = False 

st.set_page_config(page_title="수학 모의고사 그래프 생성기", page_icon="📐", layout="wide")
st.title("📐 고등 수학 모의고사 흑백 그래프 생성기")

# 카테고리
categories = [
    "일차함수", "이차함수", "유리함수", "무리함수", 
    "지수함수", "로그함수", 
    "삼각함수: 사인(sin)", "삼각함수: 코사인(cos)", "삼각함수: 탄젠트(tan)",
    "미적분: 구간별 정의 함수 (불연속/극한)", "정적분함수 (넓이 색칠)"
]
category = st.selectbox("과목 및 단원 선택", categories)

st.divider()

# --- 그래프 표시 범위 (짤림 방지 및 주기 설정) ---
st.write("🔍 **그래프 표시 범위 (그래프가 짤리거나 주기를 조절할 때 수정하세요)**")
c_x1, c_x2, c_y1, c_y2 = st.columns(4)
with c_x1: x_min = st.number_input("x 최솟값", value=-6.0, step=1.0)
with c_x2: x_max = st.number_input("x 최댓값", value=6.0, step=1.0)
with c_y1: y_min = st.number_input("y 최솟값", value=-6.0, step=1.0)
with c_y2: y_max = st.number_input("y 최댓값", value=6.0, step=1.0)

st.divider()

col_left, col_right = st.columns([1.2, 1])
x_sym = sp.Symbol('x')

# 입력 수식을 안전하게 Sympy로 변환 (e 지원)
def parse_expr(expr_str):
    return sp.sympify(expr_str, locals={"e": sp.E})

with col_left:
    st.subheader("그래프 세부 설정")
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 설정된 범위에 맞춰 x 데이터 생성
    x_default = np.linspace(x_min, x_max, 2000)
    
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

    elif category == "무리함수":
        st.latex(r"y = a\sqrt{b(x - p)} + q")
        c1, c2 = st.columns(2)
        with c1:
            a = st.number_input("바깥 계수 (a)", value=1.0)
            p = st.number_input("시작점 x (p)", value=0.0)
        with c2:
            b = st.number_input("안쪽 계수 (b)", value=1.0)
            q = st.number_input("시작점 y (q)", value=0.0)
        
        if b > 0: x_root = np.linspace(p, x_max + 5, 2000)
        else: x_root = np.linspace(x_min - 5, p, 2000)
        y_root = a * np.sqrt(b * (x_root - p)) + q
        
        ax.plot(x_root, y_root, 'black', linewidth=1.5)
        ax.plot(p, q, 'ko', markersize=5, zorder=5)

    elif category == "지수함수":
        st.latex(r"y = a^{x - p} + q")
        base_choice = st.radio("밑 (a) 선택", ["e (자연상수)", "2", "10", "직접 입력"], horizontal=True)
        if base_choice == "e (자연상수)": a = np.e
        elif base_choice == "직접 입력": a = st.number_input("밑 직접 입력", value=3.0)
        else: a = float(base_choice)
        
        c1, c2 = st.columns(2)
        with c1: p = st.number_input("x 평행이동 (p)", value=0.0)
        with c2: q = st.number_input("y 평행이동 (q)", value=0.0)
        ax.plot(x_default, a**(x_default - p) + q, 'black', linewidth=1.5)

    elif category == "로그함수":
        st.latex(r"y = \log_a (x - p) + q")
        base_choice = st.radio("밑 (a) 선택", ["e (자연상수/ln)", "2", "10", "직접 입력"], horizontal=True)
        if base_choice == "e (자연상수/ln)": a = np.e
        elif base_choice == "직접 입력": a = st.number_input("밑 직접 입력", value=3.0)
        else: a = float(base_choice)
        
        c1, c2 = st.columns(2)
        with c1: p = st.number_input("x 점근선 (p)", value=0.0)
        with c2: q = st.number_input("y 평행이동 (q)", value=0.0)
        
        x_log = np.linspace(p + 0.0001, x_max + 5, 2000)
        y_log = np.log(x_log - p) / np.log(a) + q
        ax.plot(x_log, y_log, 'black', linewidth=1.5)

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
            y_tan[np.abs(np.cos(b * (x_default - p))) < 0.05] = np.nan 
            ax.plot(x_default, y_tan, 'black', linewidth=1.5)

    elif category == "미적분: 구간별 정의 함수 (불연속/극한)":
        st.info("💡 자연상수는 `e`, 루트는 `sqrt(x)`, 분수는 `1/x` 로 입력하세요.")
        boundary = st.number_input("구간 기준점 (x = c)", value=1.0)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**$x < {boundary}$ 일 때**")
            expr_str_L = st.text_input("왼쪽 함수식 입력", value="e**x - 1")
            include_L = st.checkbox(f"x = {boundary} 포함 (≤)", value=False, key="inc_L")
            try:
                expr_sym_L = parse_expr(expr_str_L)
                st.latex(sp.latex(expr_sym_L)) # 예쁜 수식 즉시 렌더링
                f_L = sp.lambdify(x_sym, expr_sym_L, ['numpy', {'e': np.e}])
            except: st.error("올바른 수식을 입력하세요.")
                
        with c2:
            st.markdown(f"**$x > {boundary}$ 일 때**")
            expr_str_R = st.text_input("오른쪽 함수식 입력", value="-x + 3")
            include_R = st.checkbox(f"x = {boundary} 포함 (≥)", value=True, key="inc_R")
            try:
                expr_sym_R = parse_expr(expr_str_R)
                st.latex(sp.latex(expr_sym_R)) # 예쁜 수식 즉시 렌더링
                f_R = sp.lambdify(x_sym, expr_sym_R, ['numpy', {'e': np.e}])
            except: st.error("올바른 수식을 입력하세요.")

        try:
            x_L = np.linspace(x_min, boundary, 1000)
            x_R = np.linspace(boundary, x_max, 1000)
            y_L, y_R = f_L(x_L), f_R(x_R)
            
            if np.isscalar(y_L): y_L = np.full_like(x_L, y_L)
            if np.isscalar(y_R): y_R = np.full_like(x_R, y_R)

            ax.plot(x_L, y_L, 'black', linewidth=1.5)
            ax.plot(x_R, y_R, 'black', linewidth=1.5)

            val_L, val_R = f_L(boundary), f_R(boundary)
            if include_L: ax.plot(boundary, val_L, 'ko', markersize=6, zorder=10)
            else: ax.plot(boundary, val_L, 'ko', markerfacecolor='white', markersize=6, zorder=10)
            if include_R: ax.plot(boundary, val_R, 'ko', markersize=6, zorder=10)
            else: ax.plot(boundary, val_R, 'ko', markerfacecolor='white', markersize=6, zorder=10)
        except: pass

    elif category == "정적분함수 (넓이 색칠)":
        expr_str = st.text_input("함수식 입력 (예: -x**2 + 4, e**x)", value="-x**2 + 4")
        try:
            expr_sym = parse_expr(expr_str)
            st.latex(sp.latex(expr_sym))
            f = sp.lambdify(x_sym, expr_sym, ['numpy', {'e': np.e}])
            
            y = f(x_default)
            if np.isscalar(y): y = np.full_like(x_default, y)
            ax.plot(x_default, y, 'black', linewidth=1.5)
            
            c1, c2 = st.columns(2)
            with c1: a_val = st.number_input("적분 시작 (a)", value=-1.0)
            with c2: b_val = st.number_input("적분 끝 (b)", value=2.0)
            
            x_fill = np.linspace(a_val, b_val, 500)
            y_fill = f(x_fill)
            if np.isscalar(y_fill): y_fill = np.full_like(x_fill, y_fill)
            
            ax.fill_between(x_fill, y_fill, 0, color='gray', alpha=0.3)
            # a, b 값 축에 표시
            ax.annotate(f"{a_val:g}", xy=(a_val, 0), xytext=(0, -5), textcoords='offset points', ha='center', va='top')
            ax.annotate(f"{b_val:g}", xy=(b_val, 0), xytext=(0, -5), textcoords='offset points', ha='center', va='top')
        except: st.error("올바른 수식을 입력해주세요.")

    # --- 보조선 및 축 좌표 숫자 추가 (모의고사 핵심 양식) ---
    st.markdown("---")
    st.write("📏 **점선 보조선 및 축 좌표 추가 (선택사항)**")
    st.caption("그래프 위 특정 좌표와 축을 연결하는 점선을 그립니다. 2개 이상일 경우 '|' 로 구분하세요.")
    guidelines = st.text_input("좌표 입력 (x, y)", placeholder="예: 1, 2 | -3, 4")
    
    if guidelines:
        pts = guidelines.split('|')
        for pt in pts:
            try:
                px, py = map(float, pt.split(','))
                # x축으로 수선의 발 (점선)
                ax.plot([px, px], [0, py], 'k--', linewidth=1, alpha=0.8)
                # y축으로 수선의 발 (점선)
                ax.plot([0, px], [py, py], 'k--', linewidth=1, alpha=0.8)
                # 좌표 위에 점 찍기
                ax.plot(px, py, 'ko', markersize=4, zorder=6)
                
                # 축에 숫자 쓰기 (선이나 축과 겹치지 않도록 방향 최적화)
                if px != 0:
                    ax.annotate(f"{px:g}", xy=(px, 0), xytext=(0, -5 if py>0 else 5), textcoords='offset points', ha='center', va='top' if py>0 else 'bottom', fontsize=12)
                if py != 0:
                    ax.annotate(f"{py:g}", xy=(0, py), xytext=(-5 if px>0 else 5, 0), textcoords='offset points', ha='right' if px>0 else 'left', va='center', fontsize=12)
            except:
                pass

    # --- 공통 축 디자인 (고정) ---
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, zorder=10)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, zorder=10)

    ax.text(1.03, 0, r'$x$', transform=ax.get_yaxis_transform(), ha='left', va='center', fontsize=14)
    ax.text(0, 1.03, r'$y$', transform=ax.get_xaxis_transform(), ha='center', va='bottom', fontsize=14)
    
    # 원점 O 위치 절대 고정 (축 확대/축소에 영향 안 받음)
    ax.annotate(r'$O$', xy=(0, 0), xytext=(-8, -8), textcoords='offset points', ha='right', va='top', fontsize=13, zorder=15)

    ax.set_xticks([])
    ax.set_yticks([])
    
    # 사용자가 설정한 범위 적용 (그래프 짤림 방지)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

with col_right:
    st.pyplot(fig)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=400, bbox_inches="tight", transparent=True)
    st.download_button(
        label="📥 시험지용 그래프 다운로드 (PNG)",
        data=buf.getvalue(),
        file_name="math_graph_perfect.png",
        mime="image/png"
    )
