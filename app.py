import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import io
from sympy.parsing.sympy_parser import parse_expr as sympy_parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application

# --- 폰트 및 기본 설정 ---
plt.rcParams['mathtext.fontset'] = 'stix' 
plt.rcParams['font.family'] = 'HYhwpEQ' # 한컴 수식 폰트
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False 

st.set_page_config(page_title="수학 모의고사 그래프 생성기", page_icon="📐", layout="wide")
st.title("📐 고등 수학 모의고사 흑백 그래프 생성기")

categories = [
    "일차함수", "이차함수", "다항함수: 3차/4차함수", "유리함수", "무리함수", 
    "지수함수", "로그함수", 
    "삼각함수: 사인(sin)", "삼각함수: 코사인(cos)", "삼각함수: 탄젠트(tan)",
    "미적분: 구간별 정의 함수 (불연속/극한)", "정적분함수 (넓이 색칠)",
    "기하: 원의 방정식", "기하: 이차곡선 (포물선, 타원, 쌍곡선)"
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
y_sym = sp.Symbol('y')

# 💡 지능형 수식 파서 (3x -> 3*x 자동 변환 지원)
transformations = standard_transformations + (implicit_multiplication_application,)

def parse_func(expr_str):
    expr_str = str(expr_str).replace('^', '**')
    return sympy_parse_expr(expr_str, local_dict={"e": sp.E, "pi": sp.pi, "x": x_sym}, transformations=transformations)

def parse_float_expr(expr_str):
    if not isinstance(expr_str, str): return float(expr_str)
    try:
        s = str(expr_str).replace('^', '**')
        sym_expr = sympy_parse_expr(s, local_dict={"pi": sp.pi, "e": sp.E}, transformations=transformations)
        return float(sym_expr.evalf())
    except: return 0.0

bbox_white = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=1.0)

# --- 세션 상태 초기화 (점, 선, 접선 리스트) ---
if 'pts_list' not in st.session_state: st.session_state.pts_list = []
else:
    for i in range(len(st.session_state.pts_list)):
        if isinstance(st.session_state.pts_list[i], str):
            st.session_state.pts_list[i] = {"raw": st.session_state.pts_list[i], "hide_coord": False, "hide_line": False, "label_pos": "오른쪽 위", "style": "꽉 찬 점"}
        elif "style" not in st.session_state.pts_list[i]:
            st.session_state.pts_list[i]["style"] = "꽉 찬 점"

if 'lines_list' not in st.session_state: st.session_state.lines_list = []
if 'tan_list' not in st.session_state: st.session_state.tan_list = []

def add_pt_callback():
    if st.session_state.new_pt:
        st.session_state.pts_list.append({"raw": st.session_state.new_pt, "hide_coord": False, "hide_line": False, "label_pos": "오른쪽 위", "style": "꽉 찬 점"})
        st.session_state.new_pt = ""
def add_line_callback():
    if st.session_state.new_line:
        st.session_state.lines_list.append(st.session_state.new_line)
        st.session_state.new_line = ""
def add_tan_callback():
    if st.session_state.new_tan:
        st.session_state.tan_list.append(st.session_state.new_tan)
        st.session_state.new_tan = ""

current_f, current_df, current_circle = None, None, None

with col_left:
    st.subheader("그래프 세부 설정")
    fig, ax = plt.subplots(figsize=(6, 6))
    
    plot_x_min = min(0, x_min)
    plot_x_max = max(0, x_max)
    x_default = np.linspace(plot_x_min, plot_x_max, 3000)
    
    if category == "일차함수":
        st.latex(r"\mathbf{[기본형]} \quad y = ax + b")
        c1, c2 = st.columns(2)
        with c1: a = st.number_input("기울기 (a)", value=1.0)
        with c2: b = st.number_input("y절편 (b)", value=0.0)
        expr_sym = a * x_sym + b
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        
        ax.plot(x_default, a * x_default + b, 'black', linewidth=1.5, zorder=5)

    elif category == "이차함수":
        st.latex(r"\mathbf{[기본형]} \quad y = a(x - p)^2 + q")
        c1, c2, c3 = st.columns(3)
        with c1: a = st.number_input("최고차항 계수 (a)", value=1.0)
        with c2: p = st.number_input("꼭짓점 x (p)", value=0.0)
        with c3: q = st.number_input("꼭짓점 y (q)", value=0.0)
        
        expr_sym = a * (x_sym - p)**2 + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        
        current_f = sp.lambdify(x_sym, expr_sym, ['numpy'])
        current_df = sp.lambdify(x_sym, sp.diff(expr_sym, x_sym), ['numpy'])
        ax.plot(x_default, current_f(x_default), 'black', linewidth=1.5, zorder=5)

    elif category == "다항함수: 3차/4차함수":
        st.latex(r"\mathbf{[기본형]} \quad y = f(x)")
        st.info("💡 `3x^2 - 2x + 1` 처럼 치셔도 완벽하게 인식합니다!")
        expr_str = st.text_input("함수식 입력", value="x^3 - 3x")
        try:
            expr_sym = parse_func(expr_str)
            st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
            
            current_f = sp.lambdify(x_sym, expr_sym, ['numpy', {'e': np.e}])
            current_df = sp.lambdify(x_sym, sp.diff(expr_sym, x_sym), ['numpy', {'e': np.e}])
            
            y = current_f(x_default)
            if np.isscalar(y): y = np.full_like(x_default, y)
            ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)
        except: st.error("수식을 이해할 수 없습니다. 다시 확인해주세요.")

    elif category == "유리함수":
        st.latex(r"\mathbf{[기본형]} \quad y = \frac{k}{x - p} + q")
        c1, c2, c3 = st.columns(3)
        with c1: k = st.number_input("분자 (k)", value=1.0)
        with c2: p = st.number_input("x 점근선 (p)", value=1.0)
        with c3: q = st.number_input("y 점근선 (q)", value=1.0)
        show_asym = st.checkbox("점근선 표시 (점선)", value=True)
        
        expr_sym = k / (x_sym - p) + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        
        y = k / (x_default - p) + q
        y[np.abs(x_default - p) < 0.05] = np.nan 
        ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)
        if show_asym:
            ax.axvline(p, color='black', linestyle='--', linewidth=1.0, alpha=0.5, zorder=4)
            ax.axhline(q, color='black', linestyle='--', linewidth=1.0, alpha=0.5, zorder=4)

    elif category == "기하: 원의 방정식":
        st.latex(r"\mathbf{[기본형]} \quad (x - a)^2 + (y - b)^2 = r^2")
        c1, c2, c3 = st.columns(3)
        with c1: a_circ = st.number_input("중심 x (a)", value=0.0)
        with c2: b_circ = st.number_input("중심 y (b)", value=0.0)
        with c3: r_circ = st.number_input("반지름 (r)", value=3.0, min_value=0.1)
        
        lhs = (x_sym - a_circ)**2 + (y_sym - b_circ)**2
        st.latex(rf"\mathbf{{[현재 식]}} \quad {sp.latex(lhs)} = {r_circ**2:g}")
        
        current_circle = (a_circ, b_circ, r_circ)
        theta = np.linspace(0, 2*np.pi, 1000)
        ax.plot(a_circ + r_circ * np.cos(theta), b_circ + r_circ * np.sin(theta), 'black', linewidth=1.5, zorder=5)
        ax.plot(a_circ, b_circ, 'ko', markersize=3, zorder=5)

    # (그 외 다른 함수들 생략 없이 렌더링 유지)
    elif category == "무리함수":
        st.latex(r"\mathbf{[기본형]} \quad y = a\sqrt{b(x - p)} + q")
        c1, c2 = st.columns(2)
        with c1: a = st.number_input("바깥 계수 (a)", value=1.0); p = st.number_input("시작점 x (p)", value=0.0)
        with c2: b = st.number_input("안쪽 계수 (b)", value=1.0); q = st.number_input("시작점 y (q)", value=0.0)
        
        expr_sym = a * sp.sqrt(b * (x_sym - p)) + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        
        x_root = np.linspace(p, plot_x_max + 2, 2000) if b > 0 else np.linspace(plot_x_min - 2, p, 2000)
        y_root = a * np.sqrt(b * (x_root - p)) + q
        ax.plot(x_root, y_root, 'black', linewidth=1.5, zorder=5)
        ax.plot(p, q, 'ko', markersize=5, zorder=10)

    elif category == "지수함수":
        st.latex(r"\mathbf{[기본형]} \quad y = a^{x - p} + q")
        base_choice = st.radio("밑 (a)", ["e (자연상수)", "2", "10", "직접 입력"], horizontal=True)
        a = np.e if base_choice == "e (자연상수)" else (float(base_choice) if base_choice != "직접 입력" else st.number_input("직접 입력", value=3.0))
        c1, c2 = st.columns(2)
        with c1: p = st.number_input("x 평행이동 (p)", value=0.0)
        with c2: q = st.number_input("y 평행이동 (q)", value=0.0)
        
        expr_sym = a**(x_sym - p) + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        ax.plot(x_default, a**(x_default - p) + q, 'black', linewidth=1.5, zorder=5)

    elif category == "로그함수":
        st.latex(r"\mathbf{[기본형]} \quad y = \log_a(x - p) + q")
        base_choice = st.radio("밑 (a)", ["e (자연상수)", "2", "10", "직접 입력"], horizontal=True)
        a = np.e if base_choice == "e (자연상수)" else (float(base_choice) if base_choice != "직접 입력" else st.number_input("직접 입력", value=3.0))
        c1, c2 = st.columns(2)
        with c1: p = st.number_input("x 점근선 (p)", value=0.0)
        with c2: q = st.number_input("y 평행이동 (q)", value=0.0)
        
        expr_sym = sp.log(x_sym - p, a) + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        x_log = np.linspace(p + 0.0001, plot_x_max + 2, 3000)
        ax.plot(x_log, np.log(x_log - p) / np.log(a) + q, 'black', linewidth=1.5, zorder=5)

    elif "삼각함수" in category:
        st.info("💡 `pi`, `2*pi`, `1/3` 처럼 입력할 수 있습니다.")
        if "sin" in category: st.latex(r"\mathbf{[기본형]} \quad y = a \sin(b(x - p)) + q")
        elif "cos" in category: st.latex(r"\mathbf{[기본형]} \quad y = a \cos(b(x - p)) + q")
        elif "tan" in category: st.latex(r"\mathbf{[기본형]} \quad y = a \tan(b(x - p)) + q")
        
        c1, c2 = st.columns(2)
        with c1: a = st.number_input("진폭", value=1.0); p_str = st.text_input("x 평행이동", value="0")
        with c2: b_str = st.text_input("주기", value="1"); q = st.number_input("y 평행이동", value=0.0)
        p, b = parse_float_expr(p_str), parse_float_expr(b_str)
        
        if "sin" in category: y = a * np.sin(b * (x_default - p)) + q
        elif "cos" in category: y = a * np.cos(b * (x_default - p)) + q
        elif "tan" in category:
            y = a * np.tan(b * (x_default - p)) + q
            y[np.abs(np.cos(b * (x_default - p))) < 0.05] = np.nan 
        ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)

    elif category == "기하: 이차곡선 (포물선, 타원, 쌍곡선)":
        conic_type = st.radio("이차곡선 종류", ["포물선 (위/아래)", "포물선 (좌/우)", "타원", "쌍곡선"], horizontal=True)
        if "포물선" in conic_type:
            c1, c2, c3 = st.columns(3)
            with c1: p_val = st.number_input("초점 (p)", value=1.0)
            with c2: h = st.number_input("x (h)", value=0.0)
            with c3: k = st.number_input("y (k)", value=0.0)
            t = np.linspace(-15, 15, 2000)
            if "위/아래" in conic_type: 
                st.latex(rf"\mathbf{{[현재 식]}} \quad 4({p_val:g})(y - {k:g}) = (x - {h:g})^2")
                ax.plot(t + h, (t**2)/(4*p_val) + k, 'black', linewidth=1.5, zorder=5)
            else: 
                st.latex(rf"\mathbf{{[현재 식]}} \quad 4({p_val:g})(x - {h:g}) = (y - {k:g})^2")
                ax.plot((t**2)/(4*p_val) + h, t + k, 'black', linewidth=1.5, zorder=5)
        elif conic_type == "타원":
            c1, c2, c3, c4 = st.columns(4)
            with c1: a_el = st.number_input("가로(a)", value=3.0)
            with c2: b_el = st.number_input("세로(b)", value=2.0)
            with c3: h = st.number_input("x(h)", value=0.0)
            with c4: k = st.number_input("y(k)", value=0.0)
            st.latex(rf"\mathbf{{[현재 식]}} \quad \frac{{(x-{h:g})^2}}{{{a_el**2:g}}} + \frac{{(y-{k:g})^2}}{{{b_el**2:g}}} = 1")
            theta = np.linspace(0, 2*np.pi, 1000)
            ax.plot(h + a_el*np.cos(theta), k + b_el*np.sin(theta), 'black', linewidth=1.5, zorder=5)
        elif "쌍곡선" in conic_type:
            c1, c2, c3, c4 = st.columns(4)
            with c1: a_hyp = st.number_input("가로(a)", value=2.0)
            with c2: b_hyp = st.number_input("세로(b)", value=2.0)
            with c3: h = st.number_input("x(h)", value=0.0)
            with c4: k = st.number_input("y(k)", value=0.0)
            st.latex(rf"\mathbf{{[현재 식]}} \quad \frac{{(x-{h:g})^2}}{{{a_hyp**2:g}}} - \frac{{(y-{k:g})^2}}{{{b_hyp**2:g}}} = 1")
            t = np.linspace(-2.5, 2.5, 1000)
            ax.plot(h + a_hyp * np.cosh(t), k + b_hyp * np.sinh(t), 'black', linewidth=1.5, zorder=5)
            ax.plot(h - a_hyp * np.cosh(t), k + b_hyp * np.sinh(t), 'black', linewidth=1.5, zorder=5)

    # (구간별, 정적분함수 등은 동일하게 작동하므로 생략 없이 유지)
    elif category == "미적분: 구간별 정의 함수 (불연속/극한)":
        boundary = parse_float_expr(st.text_input("구간 기준점 (x = c)", value="1.0"))
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
            expr_sym = parse_func(expr_str)
            st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
            f = sp.lambdify(x_sym, expr_sym, ['numpy', {'e': np.e}])
            y = f(x_default)
            if np.isscalar(y): y = np.full_like(x_default, y)
            ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)
            c1, c2 = st.columns(2)
            with c1: a_val = parse_float_expr(st.text_input("적분 시작 (a)", value="-1"))
            with c2: b_val = parse_float_expr(st.text_input("적분 끝 (b)", value="2"))
            x_fill = np.linspace(a_val, b_val, 500)
            y_fill = f(x_fill)
            if np.isscalar(y_fill): y_fill = np.full_like(x_fill, y_fill)
            ax.fill_between(x_fill, y_fill, 0, color='gray', alpha=0.3, zorder=4)
        except: pass


    # --- 📍 점 추가 및 다중 컨트롤 UI ---
    st.markdown("---")
    st.write("📍 **점 추가 및 세부 제어 (엔터키)**")
    st.caption("💡 `1/3, sqrt(2), A` 처럼 분수와 무리수를 자유롭게 섞어 쓰셔도 됩니다.")
    st.text_input("좌표 입력칸", key="new_pt", placeholder="예: 1, 2 또는 1, 2, A", on_change=add_pt_callback)
    
    for i, pt_dict in enumerate(st.session_state.pts_list):
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1.2, 1.2, 1.5, 1.5, 1.0])
        col1.write(f"`{pt_dict['raw']}`")
        pt_dict['hide_coord'] = col2.checkbox("숫자숨김", value=pt_dict.get('hide_coord', False), key=f"hide_c_{i}")
        pt_dict['hide_line'] = col3.checkbox("점선숨김", value=pt_dict.get('hide_line', False), key=f"hide_l_{i}")
        pt_dict['style'] = col4.selectbox("모양", ["꽉 찬 점", "빈 점"], index=0 if pt_dict.get('style', '꽉 찬 점') == "꽉 찬 점" else 1, key=f"style_{i}", label_visibility="collapsed")
        pt_dict['label_pos'] = col5.selectbox("위치", ["오른쪽 위", "왼쪽 위", "오른쪽 아래", "왼쪽 아래"], index=["오른쪽 위", "왼쪽 위", "오른쪽 아래", "왼쪽 아래"].index(pt_dict.get('label_pos', '오른쪽 위')), key=f"pos_{i}", label_visibility="collapsed")
        if col6.button("삭제", key=f"del_pt_{i}"):
            st.session_state.pts_list.pop(i); st.rerun()

    pos_map = {"오른쪽 위": (6, 6, 'left', 'bottom'), "왼쪽 위": (-6, 6, 'right', 'bottom'), "오른쪽 아래": (6, -6, 'left', 'top'), "왼쪽 아래": (-6, -6, 'right', 'top')}

    for pt_dict in st.session_state.pts_list:
        try:
            parts = [p.strip() for p in pt_dict['raw'].split(',')]
            px, py = parse_float_expr(parts[0]), parse_float_expr(parts[1])
            label = parts[2] if len(parts) > 2 else ""

            if not pt_dict.get('hide_line', False):
                ax.plot([px, px], [0, py], 'k--', linewidth=1, alpha=0.8, zorder=3)
                ax.plot([0, px], [py, py], 'k--', linewidth=1, alpha=0.8, zorder=3)
            
            # 빈 점 / 꽉 찬 점 그리기
            if pt_dict.get('style', '꽉 찬 점') == "꽉 찬 점": ax.plot(px, py, 'ko', markersize=5, zorder=10)
            else: ax.plot(px, py, 'ko', markerfacecolor='white', markersize=5, markeredgewidth=1.2, zorder=10)
            
            if label:
                l_off_x, l_off_y, l_ha, l_va = pos_map[pt_dict.get('label_pos', '오른쪽 위')]
                ax.annotate(rf'$\mathrm{{{label}}}$', xy=(px, py), xytext=(l_off_x, l_off_y), textcoords='offset points', ha=l_ha, va=l_va, fontsize=13, fontfamily='stix', bbox=bbox_white, zorder=25)

            if not pt_dict.get('hide_coord', False):
                va_x, y_off_x = ('top', -7) if py >= 0 else ('bottom', 7)
                ha_y, x_off_y = ('right', -7) if px >= 0 else ('left', 7)
                if px != 0: ax.annotate(f"{px:g}", xy=(px, 0), xytext=(0, y_off_x), textcoords='offset points', ha='center', va=va_x, fontsize=11, fontfamily='HYhwpEQ', bbox=bbox_white, zorder=20)
                if py != 0: ax.annotate(f"{py:g}", xy=(0, py), xytext=(x_off_y, 0), textcoords='offset points', ha=ha_y, va='center', fontsize=11, fontfamily='HYhwpEQ', bbox=bbox_white, zorder=20)
        except: pass

    # --- 🔗 점선 연결 및 📈 접선 그리기 ---
    st.markdown("---")
    c_lines, c_tans = st.columns(2)
    
    with c_lines:
        st.write("🔗 **두 점 점선 연결**")
        st.text_input("예: 1, 2, sqrt(3), 4", key="new_line", on_change=add_line_callback)
        for i, line in enumerate(st.session_state.lines_list):
            col1, col2 = st.columns([3, 1])
            col1.write(f"`{line}`")
            if col2.button("삭제", key=f"del_line_{i}"): st.session_state.lines_list.pop(i); st.rerun()
        for line in st.session_state.lines_list:
            try:
                parts = line.split(',')
                x1, y1, x2, y2 = map(parse_float_expr, parts)
                ax.plot([x1, x2], [y1, y2], 'k--', linewidth=1.5, zorder=4)
            except: pass

    with c_tans:
        st.write("📈 **자동 접선 긋기 (이차/삼사차/원)**")
        st.caption("함수: `x좌표`, 원: `x좌표, 상` 또는 `x좌표, 하`")
        st.text_input("예: 1/3 또는 3, 상", key="new_tan", on_change=add_tan_callback)
        for i, tan_val in enumerate(st.session_state.tan_list):
            col1, col2 = st.columns([3, 1])
            col1.write(f"`접점 = {tan_val}`")
            if col2.button("삭제", key=f"del_tan_{i}"): st.session_state.tan_list.pop(i); st.rerun()
                
        for tan_val in st.session_state.tan_list:
            try:
                parts = [p.strip() for p in tan_val.split(',')]
                tx = parse_float_expr(parts[0])
                
                # 원의 접선
                if current_circle:
                    a_c, b_c, r_c = current_circle
                    if abs(tx - a_c) <= r_c + 1e-6:
                        dy_offset = np.sqrt(max(0, r_c**2 - (tx - a_c)**2))
                        ty = b_c - dy_offset if (len(parts) > 1 and "하" in parts[1]) else b_c + dy_offset
                        ax.plot(tx, ty, 'ko', markersize=5, zorder=15)
                        
                        dx, dy = tx - a_c, ty - b_c
                        # 💡 수직 접선(x = a) 버그 완벽 해결 (큰 값으로 그려 auto_y에서 제외)
                        if abs(dy) < 1e-6: 
                            ax.plot([tx, tx], [-1000, 1000], 'black', linewidth=1.0, zorder=4)
                        else:
                            tan_line_y = b_c + (r_c**2 - dx*(x_default - a_c)) / dy
                            ax.plot(x_default, tan_line_y, 'black', linewidth=1.0, zorder=4)
                
                # 다항/이차함수 접선
                elif current_f and current_df:
                    slope = float(current_df(tx))
                    y_val = float(current_f(tx))
                    tan_y = slope * (x_default - tx) + y_val
                    ax.plot(x_default, tan_y, 'black', linewidth=1.0, zorder=4)
                    ax.plot(tx, y_val, 'ko', markersize=5, zorder=15)
            except: pass

    # --- 마무리 렌더링 설정 ---
    st.markdown("---")
    o_pos = st.radio("원점(O) 기호 위치 선택", ["기본 (왼쪽 아래)", "오른쪽 아래", "왼쪽 위", "오른쪽 위", "숨기기"], horizontal=True)

    # 💡 지능형 Y축 자동 맞춤 (세로 접선이나 축 점선이 범위 계산을 망치지 못하게 철벽 방어)
    if auto_y:
        min_y, max_y = 0, 0
        for line in ax.get_lines():
            ydata = line.get_ydata()
            # 10개 이상의 점으로 이루어진 선(진짜 그래프 곡선)만 범위 계산에 포함
            if len(ydata) > 10:
                valid_y = ydata[np.isfinite(ydata)]
                if len(valid_y) > 0:
                    min_y = min(min_y, np.min(valid_y))
                    max_y = max(max_y, np.max(valid_y))
        
        y_pad = (max_y - min_y) * 0.1 if (max_y - min_y) != 0 else 1
        final_y_min = min(0, min_y - y_pad)
        final_y_max = max(0, max_y + y_pad)
        
        if final_y_max - final_y_min > 200:
            final_y_min = max(-50, final_y_min)
            final_y_max = min(50, final_y_max)
    else:
        final_y_min, final_y_max = min(0, y_min), max(0, y_max)

    ax.set_xlim(plot_x_min, plot_x_max)
    ax.set_ylim(final_y_min, final_y_max)
    if "기하" in category: ax.set_aspect('equal')
    
    ax.spines['left'].set_color('none'); ax.spines['bottom'].set_color('none')
    ax.spines['right'].set_color('none'); ax.spines['top'].set_color('none')
    ax.axhline(0, color='black', linewidth=1.2, zorder=2)
    ax.axvline(0, color='black', linewidth=1.2, zorder=2)
    ax.plot(plot_x_max, 0, ">k", clip_on=False, zorder=10)
    ax.plot(0, final_y_max, "^k", clip_on=False, zorder=10)
    
    ax.text(plot_x_max + (plot_x_max - plot_x_min)*0.03, 0, r'$x$', ha='left', va='center', fontsize=14, fontfamily='stix', zorder=20)
    ax.text(0, final_y_max + (final_y_max - final_y_min)*0.03, r'$y$', ha='center', va='bottom', fontsize=14, fontfamily='stix', zorder=20)
    
    if o_pos != "숨기기":
        o_x, o_y, o_ha, o_va = {"기본 (왼쪽 아래)": (-8, -8, 'right', 'top'), "오른쪽 아래": (8, -8, 'left', 'top'), "왼쪽 위": (-8, 8, 'right', 'bottom'), "오른쪽 위": (8, 8, 'left', 'bottom')}[o_pos]
        ax.annotate(r'$\mathrm{O}$', xy=(0, 0), xytext=(o_x, o_y), textcoords='offset points', ha=o_ha, va=o_va, fontsize=13, fontfamily='stix', bbox=bbox_white, zorder=20)

    ax.set_xticks([]); ax.set_yticks([])

with col_right:
    st.pyplot(fig)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=400, bbox_inches="tight", transparent=True)
    st.download_button("📥 시험지용 그래프 다운로드 (PNG)", data=buf.getvalue(), file_name="math_graph.png", mime="image/png")
