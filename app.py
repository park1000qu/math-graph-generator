import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import io

# --- 폰트 및 기본 설정 ---
plt.rcParams['mathtext.fontset'] = 'stix' 
plt.rcParams['font.family'] = 'Hancom Batang'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False 

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

st.write("🔍 **그래프 x축 표시 범위 (y축은 그래프가 잘리지 않게 알아서 맞춰줍니다!)**")
c_x1, c_x2, c_yauto = st.columns([1, 1, 2])
with c_x1: x_min = st.number_input("x 최솟값", value=-6.0, step=1.0)
with c_x2: x_max = st.number_input("x 최댓값", value=6.0, step=1.0)
with c_yauto: auto_y = st.checkbox("y축 자동 맞춤 (그래프 짤림 완벽 방지)", value=True)

if not auto_y:
    c_y1, c_y2 = st.columns(2)
    with c_y1: y_min = st.number_input("y 최솟값 (수동)", value=-6.0, step=1.0)
    with c_y2: y_max = st.number_input("y 최댓값 (수동)", value=6.0, step=1.0)

st.divider()

col_left, col_right = st.columns([1.2, 1])
x_sym = sp.Symbol('x')

def parse_expr(expr_str):
    try: return float(sp.sympify(expr_str, locals={"pi": sp.pi, "e": sp.E}).evalf())
    except: return 0.0

def parse_func(expr_str):
    return sp.sympify(expr_str, locals={"e": sp.E})

bbox_white = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=1.0)

# --- 세션 상태 초기화 (엔터키 리스트용) ---
if 'pts_list' not in st.session_state: st.session_state.pts_list = []
if 'lines_list' not in st.session_state: st.session_state.lines_list = []

def add_pt_callback():
    if st.session_state.new_pt:
        st.session_state.pts_list.append(st.session_state.new_pt)
        st.session_state.new_pt = ""

def add_line_callback():
    if st.session_state.new_line:
        st.session_state.lines_list.append(st.session_state.new_line)
        st.session_state.new_line = ""

with col_left:
    st.subheader("그래프 세부 설정")
    fig, ax = plt.subplots(figsize=(6, 6))
    
    plot_x_min = min(0, x_min)
    plot_x_max = max(0, x_max)
    x_default = np.linspace(plot_x_min, plot_x_max, 3000)
    
    if category == "일차함수":
        c1, c2 = st.columns(2)
        with c1: a = st.number_input("기울기 (a)", value=1.0)
        with c2: b = st.number_input("y절편 (b)", value=0.0)
        ax.plot(x_default, a * x_default + b, 'black', linewidth=1.5, zorder=5)

    elif category == "이차함수":
        c1, c2, c3 = st.columns(3)
        with c1: a = st.number_input("최고차항 계수 (a)", value=1.0)
        with c2: p = st.number_input("꼭짓점 x (p)", value=0.0)
        with c3: q = st.number_input("꼭짓점 y (q)", value=0.0)
        ax.plot(x_default, a * (x_default - p)**2 + q, 'black', linewidth=1.5, zorder=5)

    elif category == "유리함수":
        c1, c2, c3 = st.columns(3)
        with c1: k = st.number_input("분자 (k)", value=1.0)
        with c2: p = st.number_input("x 점근선 (p)", value=1.0)
        with c3: q = st.number_input("y 점근선 (q)", value=1.0)
        y = k / (x_default - p) + q
        y[np.abs(x_default - p) < 0.05] = np.nan 
        ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)

    elif category == "무리함수":
        c1, c2 = st.columns(2)
        with c1:
            a = st.number_input("바깥 계수 (a)", value=1.0)
            p = st.number_input("시작점 x (p)", value=0.0)
        with c2:
            b = st.number_input("안쪽 계수 (b)", value=1.0)
            q = st.number_input("시작점 y (q)", value=0.0)
        if b > 0: x_root = np.linspace(p, plot_x_max + 2, 2000)
        else: x_root = np.linspace(plot_x_min - 2, p, 2000)
        y_root = a * np.sqrt(b * (x_root - p)) + q
        ax.plot(x_root, y_root, 'black', linewidth=1.5, zorder=5)
        ax.plot(p, q, 'ko', markersize=5, zorder=10)

    elif category == "지수함수":
        base_choice = st.radio("밑 (a)", ["e (자연상수)", "2", "10", "직접 입력"], horizontal=True)
        if base_choice == "e (자연상수)": a = np.e
        elif base_choice == "직접 입력": a = st.number_input("직접 입력", value=3.0)
        else: a = float(base_choice)
        c1, c2 = st.columns(2)
        with c1: p = st.number_input("x 평행이동 (p)", value=0.0)
        with c2: q = st.number_input("y 평행이동 (q)", value=0.0)
        ax.plot(x_default, a**(x_default - p) + q, 'black', linewidth=1.5, zorder=5)

    elif category == "로그함수":
        base_choice = st.radio("밑 (a)", ["e (자연상수)", "2", "10", "직접 입력"], horizontal=True)
        if base_choice == "e (자연상수)": a = np.e
        elif base_choice == "직접 입력": a = st.number_input("직접 입력", value=3.0)
        else: a = float(base_choice)
        c1, c2 = st.columns(2)
        with c1: p = st.number_input("x 점근선 (p)", value=0.0)
        with c2: q = st.number_input("y 평행이동 (q)", value=0.0)
        x_log = np.linspace(p + 0.0001, plot_x_max + 2, 3000)
        y_log = np.log(x_log - p) / np.log(a) + q
        ax.plot(x_log, y_log, 'black', linewidth=1.5, zorder=5)

    elif "삼각함수" in category:
        st.info("💡 주기와 평행이동에는 `pi`, `2*pi`, `pi/2` 처럼 입력할 수 있습니다.")
        c1, c2 = st.columns(2)
        with c1:
            a = st.number_input("진폭 (a)", value=1.0)
            p_str = st.text_input("x 평행이동 (p)", value="0")
        with c2:
            b_str = st.text_input("주기 계수 (b)", value="1")
            q = st.number_input("y 평행이동 (q)", value=0.0)
        p, b = parse_expr(p_str), parse_expr(b_str)
        if "sin" in category: y = a * np.sin(b * (x_default - p)) + q
        elif "cos" in category: y = a * np.cos(b * (x_default - p)) + q
        elif "tan" in category:
            y = a * np.tan(b * (x_default - p)) + q
            y[np.abs(np.cos(b * (x_default - p))) < 0.05] = np.nan 
        ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)

    elif category == "미적분: 구간별 정의 함수 (불연속/극한)":
        boundary = st.number_input("구간 기준점 (x = c)", value=1.0)
        c1, c2 = st.columns(2)
        with c1:
            expr_str_L = st.text_input("왼쪽 함수식", value="x**2")
            inc_L = st.checkbox(f"포함 (≤)", value=False)
            try: f_L = sp.lambdify(x_sym, parse_func(expr_str_L), ['numpy', {'e': np.e}])
            except: pass
        with c2:
            expr_str_R = st.text_input("오른쪽 함수식", value="-x + 3")
            inc_R = st.checkbox(f"포함 (≥)", value=True)
            try: f_R = sp.lambdify(x_sym, parse_func(expr_str_R), ['numpy', {'e': np.e}])
            except: pass

        try:
            x_L = np.linspace(plot_x_min, boundary, 1500)
            x_R = np.linspace(boundary, plot_x_max, 1500)
            y_L, y_R = f_L(x_L), f_R(x_R)
            if np.isscalar(y_L): y_L = np.full_like(x_L, y_L)
            if np.isscalar(y_R): y_R = np.full_like(x_R, y_R)

            ax.plot(x_L, y_L, 'black', linewidth=1.5, zorder=5)
            ax.plot(x_R, y_R, 'black', linewidth=1.5, zorder=5)
            val_L, val_R = f_L(boundary), f_R(boundary)
            
            if inc_L: ax.plot(boundary, val_L, 'ko', markersize=5, zorder=10)
            else: ax.plot(boundary, val_L, 'ko', markerfacecolor='white', markersize=5, markeredgewidth=1.2, zorder=10)
            if inc_R: ax.plot(boundary, val_R, 'ko', markersize=5, zorder=10)
            else: ax.plot(boundary, val_R, 'ko', markerfacecolor='white', markersize=5, markeredgewidth=1.2, zorder=10)
        except: pass

    elif category == "정적분함수 (넓이 색칠)":
        expr_str = st.text_input("함수식 입력", value="-x**2 + 4")
        try:
            f = sp.lambdify(x_sym, parse_func(expr_str), ['numpy', {'e': np.e}])
            y = f(x_default)
            if np.isscalar(y): y = np.full_like(x_default, y)
            ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)
            c1, c2 = st.columns(2)
            with c1: a_val = st.number_input("적분 시작 (a)", value=-1.0)
            with c2: b_val = st.number_input("적분 끝 (b)", value=2.0)
            x_fill = np.linspace(a_val, b_val, 500)
            y_fill = f(x_fill)
            if np.isscalar(y_fill): y_fill = np.full_like(x_fill, y_fill)
            ax.fill_between(x_fill, y_fill, 0, color='gray', alpha=0.3, zorder=4)
        except: pass

    # --- 리스트형 점 및 점선 연결 추가 (UI 통일) ---
    st.markdown("---")
    c_pts, c_lines = st.columns(2)
    
    with c_pts:
        st.write("📍 **점 및 축 보조선 (엔터키)**")
        st.text_input("점 좌표 (예: 1, 2)", key="new_pt", on_change=add_pt_callback)
        
        for i, pt in enumerate(st.session_state.pts_list):
            col1, col2 = st.columns([5, 1])
            col1.write(f"`{pt}`")
            if col2.button("삭제", key=f"del_pt_{i}"):
                st.session_state.pts_list.pop(i)
                st.rerun()

        for pt in st.session_state.pts_list:
            try:
                px, py = map(float, pt.split(','))
                ax.plot([px, px], [0, py], 'k--', linewidth=1, alpha=0.8, zorder=3)
                ax.plot([0, px], [py, py], 'k--', linewidth=1, alpha=0.8, zorder=3)
                ax.plot(px, py, 'ko', markersize=5, zorder=10)
                
                va_x = 'top' if py >= 0 else 'bottom'
                y_off_x = -7 if py >= 0 else 7
                ha_y = 'right' if px >= 0 else 'left'
                x_off_y = -7 if px >= 0 else 7

                if px != 0:
                    ax.annotate(f"{px:g}", xy=(px, 0), xytext=(0, y_off_x), textcoords='offset points', 
                                ha='center', va=va_x, fontsize=11, fontfamily='Hancom Batang', bbox=bbox_white, zorder=20)
                if py != 0:
                    ax.annotate(f"{py:g}", xy=(0, py), xytext=(x_off_y, 0), textcoords='offset points', 
                                ha=ha_y, va='center', fontsize=11, fontfamily='Hancom Batang', bbox=bbox_white, zorder=20)
            except: pass

    with c_lines:
        st.write("🔗 **두 점 사이 점선 연결 (엔터키)**")
        st.text_input("선 좌표 (예: 1, 2, 3, 4)", key="new_line", on_change=add_line_callback)
        
        for i, line in enumerate(st.session_state.lines_list):
            col1, col2 = st.columns([5, 1])
            col1.write(f"`{line}`")
            if col2.button("삭제", key=f"del_line_{i}"):
                st.session_state.lines_list.pop(i)
                st.rerun()

        for line in st.session_state.lines_list:
            try:
                x1, y1, x2, y2 = map(float, line.split(','))
                ax.plot([x1, x2], [y1, y2], 'k--', linewidth=1.5, zorder=4)
            except: pass

    # --- 원점 O 위치 수동 제어 ---
    st.markdown("---")
    o_pos = st.radio("원점(O) 기호 위치 선택", ["기본 (왼쪽 아래)", "오른쪽 아래", "왼쪽 위", "오른쪽 위", "숨기기"], horizontal=True)

    # --- 자동 스케일링 로직 ---
    if auto_y:
        min_y, max_y = 0, 0
        for line in ax.get_lines():
            ydata = line.get_ydata()
            if len(ydata) > 0:
                valid_y = ydata[np.isfinite(ydata)]
                if len(valid_y) > 0:
                    min_y = min(min_y, np.min(valid_y))
                    max_y = max(max_y, np.max(valid_y))
        
        y_pad = (max_y - min_y) * 0.1 if (max_y - min_y) != 0 else 1
        final_y_min = min(0, min_y - y_pad)
        final_y_max = max(0, max_y + y_pad)
        
        if final_y_max - final_y_min > 100:
            final_y_min = max(-30, final_y_min)
            final_y_max = min(30, final_y_max)
    else:
        final_y_min = min(0, y_min)
        final_y_max = max(0, y_max)

    ax.set_xlim(plot_x_min, plot_x_max)
    ax.set_ylim(final_y_min, final_y_max)
    
    ax.spines['left'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    ax.axhline(0, color='black', linewidth=1.2, zorder=2)
    ax.axvline(0, color='black', linewidth=1.2, zorder=2)

    ax.plot(plot_x_max, 0, ">k", clip_on=False, zorder=10)
    ax.plot(0, final_y_max, "^k", clip_on=False, zorder=10)
    ax.text(plot_x_max + (plot_x_max - plot_x_min)*0.03, 0, r'$x$', ha='left', va='center', fontsize=14, fontfamily='stix', zorder=20)
    ax.text(0, final_y_max + (final_y_max - final_y_min)*0.03, r'$y$', ha='center', va='bottom', fontsize=14, fontfamily='stix', zorder=20)
    
    # 설정한 원점 위치 반영
    if o_pos != "숨기기":
        if o_pos == "기본 (왼쪽 아래)": o_x, o_y, o_ha, o_va = -8, -8, 'right', 'top'
        elif o_pos == "오른쪽 아래": o_x, o_y, o_ha, o_va = 8, -8, 'left', 'top'
        elif o_pos == "왼쪽 위": o_x, o_y, o_ha, o_va = -8, 8, 'right', 'bottom'
        elif o_pos == "오른쪽 위": o_x, o_y, o_ha, o_va = 8, 8, 'left', 'bottom'
        
        ax.annotate(r'$O$', xy=(0, 0), xytext=(o_x, o_y), textcoords='offset points', 
                    ha=o_ha, va=o_va, fontsize=11, fontfamily='Hancom Batang', bbox=bbox_white, zorder=20)

    ax.set_xticks([])
    ax.set_yticks([])

with col_right:
    st.pyplot(fig)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=400, bbox_inches="tight", transparent=True)
    st.download_button("📥 시험지용 그래프 다운로드 (PNG)", data=buf.getvalue(), file_name="math_graph.png", mime="image/png")
