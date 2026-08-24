import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import io
import re
from sympy.parsing.sympy_parser import parse_expr as sympy_parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application

# --- 폰트 및 기본 설정 ---
plt.rcParams['mathtext.fontset'] = 'stix' 
plt.rcParams['font.family'] = 'HYhwpEQ' # 한컴 수식 폰트
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False 

# 💡 타이틀 변경
st.set_page_config(page_title="평가자료용 수학 그래프 생성기", page_icon="📐", layout="wide")
st.title("📐 평가자료용 수학 그래프 생성기")
st.info("💡 **모든 숫자 입력칸**에 `1/3`, `sqrt2`, `2sqrt3`, `pi/2` 등 수식을 그대로 입력하실 수 있습니다!")

categories = [
    "일차함수", "이차함수", "다항함수: 3차/4차함수", "유리함수", "무리함수", 
    "지수함수", "로그함수", 
    "삼각함수: 사인(sin)", "삼각함수: 코사인(cos)", "삼각함수: 탄젠트(tan)",
    "미적분: 구간별 정의 함수 (불연속/극한)", "정적분함수 (넓이 색칠)",
    "기하: 원의 방정식", "기하: 이차곡선 (포물선, 타원, 쌍곡선)"
]
category = st.selectbox("메인 그래프 형태 선택", categories)

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

# 💡 지능형 수식 파서
transformations = standard_transformations + (implicit_multiplication_application,)

def robust_parse(val_str):
    if not isinstance(val_str, str): return float(val_str)
    s = str(val_str).strip()
    if not s: return 0.0
    s = s.replace('^', '**')
    s = re.sub(r'sqrt\s*(\d+(?:\.\d+)?)', r'sqrt(\1)', s)
    
    env = {"pi": sp.pi, "e": sp.E, "sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "log": sp.log, "ln": sp.log}
    try:
        expr = sympy_parse_expr(s, local_dict=env, transformations=transformations)
        return float(expr.evalf())
    except:
        return 0.0

def parse_func(expr_str):
    expr_str = str(expr_str).replace('^', '**')
    expr_str = re.sub(r'sqrt\s*(\d+(?:\.\d+)?)', r'sqrt(\1)', expr_str)
    env = {"e": sp.E, "pi": sp.pi, "x": x_sym, "sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan}
    return sympy_parse_expr(expr_str, local_dict=env, transformations=transformations)

def math_input(label, default_val, key=None):
    return robust_parse(st.text_input(label, value=str(default_val), key=key))

bbox_white = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=1.0)

# --- 세션 상태 초기화 ---
if 'pts_list' not in st.session_state: st.session_state.pts_list = []
if 'lines_list' not in st.session_state: st.session_state.lines_list = []
if 'tan_list' not in st.session_state: st.session_state.tan_list = []
if 'extra_graphs' not in st.session_state: st.session_state.extra_graphs = [] # 다중 그래프용 세션 추가

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
    
    # 1. 메인 그래프 렌더링
    if category == "일차함수":
        st.latex(r"\mathbf{[기본형]} \quad y = ax + b")
        c1, c2 = st.columns(2)
        with c1: a = math_input("기울기 (a)", "1")
        with c2: b = math_input("y절편 (b)", "0")
        expr_sym = a * x_sym + b
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        ax.plot(x_default, a * x_default + b, 'black', linewidth=1.5, zorder=5)

    elif category == "이차함수":
        st.latex(r"\mathbf{[기본형]} \quad y = a(x - p)^2 + q")
        c1, c2, c3 = st.columns(3)
        with c1: a = math_input("최고차항 계수 (a)", "1")
        with c2: p = math_input("꼭짓점 x (p)", "0")
        with c3: q = math_input("꼭짓점 y (q)", "0")
        
        expr_sym = a * (x_sym - p)**2 + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        current_f = sp.lambdify(x_sym, expr_sym, ['numpy'])
        current_df = sp.lambdify(x_sym, sp.diff(expr_sym, x_sym), ['numpy'])
        ax.plot(x_default, current_f(x_default), 'black', linewidth=1.5, zorder=5)

    elif category == "다항함수: 3차/4차함수":
        st.latex(r"\mathbf{[기본형]} \quad y = f(x)")
        expr_str = st.text_input("함수식 입력", value="x^3 - 3x")
        try:
            expr_sym = parse_func(expr_str)
            st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
            current_f = sp.lambdify(x_sym, expr_sym, ['numpy', {'e': np.e}])
            current_df = sp.lambdify(x_sym, sp.diff(expr_sym, x_sym), ['numpy', {'e': np.e}])
            y = current_f(x_default)
            if np.isscalar(y): y = np.full_like(x_default, y)
            ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)
        except: st.error("수식을 이해할 수 없습니다. 수식을 확인해주세요.")

    elif category == "유리함수":
        st.latex(r"\mathbf{[기본형]} \quad y = \frac{k}{x - p} + q")
        c1, c2, c3 = st.columns(3)
        with c1: k = math_input("분자 (k)", "1")
        with c2: p = math_input("x 점근선 (p)", "1")
        with c3: q = math_input("y 점근선 (q)", "1")
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
        with c1: a_circ = math_input("중심 x (a)", "0")
        with c2: b_circ = math_input("중심 y (b)", "0")
        with c3: r_circ = math_input("반지름 (r)", "3")
        
        lhs = (x_sym - a_circ)**2 + (y_sym - b_circ)**2
        st.latex(rf"\mathbf{{[현재 식]}} \quad {sp.latex(lhs)} = {r_circ**2:g}")
        current_circle = (a_circ, b_circ, r_circ)
        theta = np.linspace(0, 2*np.pi, 1000)
        ax.plot(a_circ + r_circ * np.cos(theta), b_circ + r_circ * np.sin(theta), 'black', linewidth=1.5, zorder=5)
        ax.plot(a_circ, b_circ, 'ko', markersize=3, zorder=5)

    elif category == "무리함수":
        st.latex(r"\mathbf{[기본형]} \quad y = a\sqrt{b(x - p)} + q")
        c1, c2 = st.columns(2)
        with c1: a = math_input("바깥 계수 (a)", "1"); p = math_input("시작점 x (p)", "0")
        with c2: b = math_input("안쪽 계수 (b)", "1"); q = math_input("시작점 y (q)", "0")
        expr_sym = a * sp.sqrt(b * (x_sym - p)) + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        x_root = np.linspace(p, plot_x_max + 2, 2000) if b > 0 else np.linspace(plot_x_min - 2, p, 2000)
        y_root = a * np.sqrt(b * (x_root - p)) + q
        ax.plot(x_root, y_root, 'black', linewidth=1.5, zorder=5)
        ax.plot(p, q, 'ko', markersize=5, zorder=10)

    elif category == "지수함수":
        st.latex(r"\mathbf{[기본형]} \quad y = a^{x - p} + q")
        base_choice = st.radio("밑 (a)", ["e (자연상수)", "2", "10", "직접 입력"], horizontal=True)
        a = np.e if base_choice == "e (자연상수)" else (float(base_choice) if base_choice != "직접 입력" else math_input("직접 입력", "3"))
        c1, c2 = st.columns(2)
        with c1: p = math_input("x 평행이동 (p)", "0")
        with c2: q = math_input("y 평행이동 (q)", "0")
        expr_sym = a**(x_sym - p) + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        ax.plot(x_default, a**(x_default - p) + q, 'black', linewidth=1.5, zorder=5)

    elif category == "로그함수":
        st.latex(r"\mathbf{[기본형]} \quad y = \log_a(x - p) + q")
        base_choice = st.radio("밑 (a)", ["e (자연상수)", "2", "10", "직접 입력"], horizontal=True)
        a = np.e if base_choice == "e (자연상수)" else (float(base_choice) if base_choice != "직접 입력" else math_input("직접 입력", "3"))
        c1, c2 = st.columns(2)
        with c1: p = math_input("x 점근선 (p)", "0")
        with c2: q = math_input("y 평행이동 (q)", "0")
        expr_sym = sp.log(x_sym - p, a) + q
        st.latex(r"\mathbf{[현재 식]} \quad y = " + sp.latex(expr_sym))
        x_log = np.linspace(p + 0.0001, plot_x_max + 2, 3000)
        ax.plot(x_log, np.log(x_log - p) / np.log(a) + q, 'black', linewidth=1.5, zorder=5)

    elif "삼각함수" in category:
        if "sin" in category: st.latex(r"\mathbf{[기본형]} \quad y = a \sin(b(x - p)) + q")
        elif "cos" in category: st.latex(r"\mathbf{[기본형]} \quad y = a \cos(b(x - p)) + q")
        elif "tan" in category: st.latex(r"\mathbf{[기본형]} \quad y = a \tan(b(x - p)) + q")
        c1, c2 = st.columns(2)
        with c1: a = math_input("진폭", "1"); p = math_input("x 평행이동", "0")
        with c2: b = math_input("주기", "1"); q = math_input("y 평행이동", "0")
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
            with c1: p_val = math_input("초점 (p)", "1")
            with c2: h = math_input("x (h)", "0")
            with c3: k = math_input("y (k)", "0")
            t = np.linspace(-15, 15, 2000)
            if "위/아래" in conic_type: 
                st.latex(rf"\mathbf{{[현재 식]}} \quad 4({p_val:g})(y - {k:g}) = (x - {h:g})^2")
                ax.plot(t + h, (t**2)/(4*p_val) + k, 'black', linewidth=1.5, zorder=5)
            else: 
                st.latex(rf"\mathbf{{[현재 식]}} \quad 4({p_val:g})(x - {h:g}) = (y - {k:g})^2")
                ax.plot((t**2)/(4*p_val) + h, t + k, 'black', linewidth=1.5, zorder=5)
        elif conic_type == "타원":
            c1, c2, c3, c4 = st.columns(4)
            with c1: a_el = math_input("가로(a)", "3")
            with c2: b_el = math_input("세로(b)", "2")
            with c3: h = math_input("x(h)", "0")
            with c4: k = math_input("y(k)", "0")
            st.latex(rf"\mathbf{{[현재 식]}} \quad \frac{{(x-{h:g})^2}}{{{a_el**2:g}}} + \frac{{(y-{k:g})^2}}{{{b_el**2:g}}} = 1")
            theta = np.linspace(0, 2*np.pi, 1000)
            ax.plot(h + a_el*np.cos(theta), k + b_el*np.sin(theta), 'black', linewidth=1.5, zorder=5)
        elif "쌍곡선" in conic_type:
            c1, c2, c3, c4 = st.columns(4)
            with c1: a_hyp = math_input("가로(a)", "2")
            with c2: b_hyp = math_input("세로(b)", "2")
            with c3: h = math_input("x(h)", "0")
            with c4: k = math_input("y(k)", "0")
            st.latex(rf"\mathbf{{[현재 식]}} \quad \frac{{(x-{h:g})^2}}{{{a_hyp**2:g}}} - \frac{{(y-{k:g})^2}}{{{b_hyp**2:g}}} = 1")
            t = np.linspace(-2.5, 2.5, 1000)
            ax.plot(h + a_hyp * np.cosh(t), k + b_hyp * np.sinh(t), 'black', linewidth=1.5, zorder=5)
            ax.plot(h - a_hyp * np.cosh(t), k + b_hyp * np.sinh(t), 'black', linewidth=1.5, zorder=5)

    elif category == "미적분: 구간별 정의 함수 (불연속/극한)":
        boundary = math_input("구간 기준점 (x = c)", "1")
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
            with c1: a_val = math_input("적분 시작 (a)", "-1")
            with c2: b_val = math_input("적분 끝 (b)", "2")
            x_fill = np.linspace(a_val, b_val, 500)
            y_fill = f(x_fill)
            if np.isscalar(y_fill): y_fill = np.full_like(x_fill, y_fill)
            ax.fill_between(x_fill, y_fill, 0, color='gray', alpha=0.3, zorder=4)
        except: pass

    # 💡 2. 다중 그래프 추가 렌더링 (메인 그래프 위에 덧그리기)
    for g in st.session_state.extra_graphs:
        try:
            ex = parse_func(g['expr'])
            f_ext = sp.lambdify(x_sym, ex, ['numpy', {'e': np.e}])
            
            # 지정된 범위가 없으면 화면 전체를 그림
            g_min = robust_parse(g['xmin']) if g['xmin'].strip() else plot_x_min
            g_max = robust_parse(g['xmax']) if g['xmax'].strip() else plot_x_max
            if g_min > g_max: g_min, g_max = g_max, g_min
            
            x_ext = np.linspace(g_min, g_max, 1500)
            y_ext = f_ext(x_ext)
            if np.isscalar(y_ext): y_ext = np.full_like(x_ext, y_ext)
            
            ax.plot(x_ext, y_ext, 'black', linewidth=1.5, zorder=5)
        except: pass

    # --- 📍 점 추가 및 다중 컨트롤 UI ---
    st.markdown("---")
    st.write("📍 **점 추가 및 세부 제어 (엔터키)**")
    st.text_input("좌표 입력칸", key="new_pt", placeholder="예: 1/3, sqrt2, A", on_change=add_pt_callback)
    
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
            px, py = robust_parse(parts[0]), robust_parse(parts[1])
            label = parts[2] if len(parts) > 2 else ""

            if not pt_dict.get('hide_line', False):
                ax.plot([px, px], [0, py], 'k--', linewidth=1, alpha=0.8, zorder=3)
                ax.plot([0, px], [py, py], 'k--', linewidth=1, alpha=0.8, zorder=3)
            
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

    # --- 🔗 선, 접선, 추가 그래프 레이아웃 ---
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
                x1, y1, x2, y2 = map(robust_parse, parts)
                ax.plot([x1, x2], [y1, y2], 'k--', linewidth=1.5, zorder=4)
            except: pass

    with c_tans:
        st.write("📈 **자동 접선 긋기 (이차/삼사차/원)**")
        st.caption("함수: `x좌표`, 원: `x좌표, 상` 또는 `하`")
        st.text_input("예: 1/3 또는 sqrt2, 상", key="new_tan", on_change=add_tan_callback)
        for i, tan_val in enumerate(st.session_state.tan_list):
            col1, col2 = st.columns([3, 1])
            col1.write(f"`접점 = {tan_val}`")
            if col2.button("삭제", key=f"del_tan_{i}"): st.session_state.tan_list.pop(i); st.rerun()
                
        for tan_val in st.session_state.tan_list:
            try:
                parts = [p.strip() for p in tan_val.split(',')]
                tx = robust_parse(parts[0])
                
                if current_circle:
                    a_c, b_c, r_c = current_circle
                    if abs(tx - a_c) <= r_c + 1e-6:
                        dy_offset = np.sqrt(max(0, r_c**2 - (tx - a_c)**2))
                        ty = b_c - dy_offset if (len(parts) > 1 and "하" in parts[1]) else b_c + dy_offset
                        ax.plot(tx, ty, 'ko', markersize=5, zorder=15)
                        
                        dx, dy = tx - a_c, ty - b_c
                        if abs(dy) < 1e-6: 
                            ax.plot([tx, tx], [-1000, 1000], 'black', linewidth=1.0, zorder=4)
                        else:
                            tan_line_y = b_c + (r_c**2 - dx*(x_default - a_c)) / dy
                            ax.plot(x_default, tan_line_y, 'black', linewidth=1.0, zorder=4)
                
                elif current_f and current_df:
                    slope = float(current_df(tx))
                    y_val = float(current_f(tx))
                    tan_y = slope * (x_default - tx) + y_val
                    ax.plot(x_default, tan_y, 'black', linewidth=1.0, zorder=4)
                    ax.plot(tx, y_val, 'ko', markersize=5, zorder=15)
            except: pass

    # 💡 3. 다중 그래프 추가 UI 
    st.markdown("---")
    c_extra, c_options = st.columns([1.5, 1])
    
    with c_extra:
        st.write("➕ **다중 그래프 추가 (범위 제한)**")
        with st.form("extra_graph_form", clear_on_submit=True):
            e_expr = st.text_input("수식 (예: 2x+1, -x^2+4)")
            c_min, c_max = st.columns(2)
            e_min = c_min.text_input("x 최소 (빈칸=전체)")
            e_max = c_max.text_input("x 최대 (빈칸=전체)")
            submit_extra = st.form_submit_button("그래프 겹쳐 그리기")
            if submit_extra and e_expr:
                st.session_state.extra_graphs.append({"expr": e_expr, "xmin": e_min, "xmax": e_max})
                st.rerun()

        for i, g in enumerate(st.session_state.extra_graphs):
            col1, col2 = st.columns([5, 1])
            range_str = f"[{g['xmin']} ~ {g['xmax']}]" if (g['xmin'] or g['xmax']) else "[전체]"
            col1.write(f"`{g['expr']}`  {range_str}")
            if col2.button("삭제", key=f"del_g_{i}"):
                st.session_state.extra_graphs.pop(i)
                st.rerun()

    with c_options:
        st.write("⚙️ **기타 설정**")
        o_pos = st.radio("원점(O) 위치", ["기본 (왼쪽 아래)", "오른쪽 아래", "왼쪽 위", "오른쪽 위", "숨기기"])

    # --- 마무리 렌더링 설정 ---
    if auto_y:
        min_y, max_y = 0, 0
        for line in ax.get_lines():
            ydata = line.get_ydata()
            if len(ydata) > 10: # 점선이나 접선이 아닌 진짜 그래프 곡선만 인식
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
    
    arrow_style = dict(arrowstyle="-|>", color='black', lw=1.2, mutation_scale=18)
    ax.annotate('', xy=(plot_x_max, 0), xytext=(-1, 0), textcoords='offset points', arrowprops=arrow_style, annotation_clip=False, zorder=10)
    ax.annotate('', xy=(0, final_y_max), xytext=(0, -1), textcoords='offset points', arrowprops=arrow_style, annotation_clip=False, zorder=10)
    
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
