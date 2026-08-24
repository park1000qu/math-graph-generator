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

def parse_expr(expr_str):
    try: return float(sp.sympify(expr_str, locals={"pi": sp.pi, "e": sp.E}).evalf())
    except: return 0.0

def parse_func(expr_str):
    return sp.sympify(expr_str, locals={"e": sp.E})

bbox_white = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=1.0)

# --- 세션 상태 초기화 ---
if 'pts_list' not in st.session_state: 
    st.session_state.pts_list = []
else:
    for i in range(len(st.session_state.pts_list)):
        if isinstance(st.session_state.pts_list[i], str):
            st.session_state.pts_list[i] = {"raw": st.session_state.pts_list[i], "hide_coord": False, "hide_line": False, "label_pos": "오른쪽 위"}
        else:
            if "hide_line" not in st.session_state.pts_list[i]:
                st.session_state.pts_list[i]["hide_line"] = False

if 'lines_list' not in st.session_state: 
    st.session_state.lines_list = []

def add_pt_callback():
    if st.session_state.new_pt:
        st.session_state.pts_list.append({
            "raw": st.session_state.new_pt,
            "hide_coord": False,
            "hide_line": False,
            "label_pos": "오른쪽 위"
        })
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

    elif category == "다항함수: 3차/4차함수":
        expr_str = st.text_input("함수식 입력 (예: x**3 - 3*x)", value="x**3 - 3*x")
        draw_tan = st.checkbox("접선 그리기")
        if draw_tan:
            tan_x_val = st.number_input("접점의 x좌표", value=1.0)
            
        try:
            expr_sym = parse_func(expr_str)
            st.latex(sp.latex(expr_sym))
            f = sp.lambdify(x_sym, expr_sym, ['numpy', {'e': np.e}])
            y = f(x_default)
            if np.isscalar(y): y = np.full_like(x_default, y)
            ax.plot(x_default, y, 'black', linewidth=1.5, zorder=5)
            
            # 💡 다항함수 자동 미분 및 접선 그리기
            if draw_tan:
                df_sym = sp.diff(expr_sym, x_sym)
                df = sp.lambdify(x_sym, df_sym, ['numpy', {'e': np.e}])
                slope = float(df(tan_x_val))
                y_val = float(f(tan_x_val))
                
                tan_y = slope * (x_default - tan_x_val) + y_val
                ax.plot(x_default, tan_y, 'black', linewidth=1.0, zorder=4)
                ax.plot(tan_x_val, y_val, 'ko', markersize=5, zorder=15) # 접점 쾅
        except: pass

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

    elif category == "기하: 원의 방정식":
        st.latex(r"(x - a)^2 + (y - b)^2 = r^2")
        c1, c2, c3 = st.columns(3)
        with c1: a_circ = st.number_input("중심 x (a)", value=0.0)
        with c2: b_circ = st.number_input("중심 y (b)", value=0.0)
        with c3: r_circ = st.number_input("반지름 (r)", value=3.0, min_value=0.1)
        
        draw_tan_circ = st.checkbox("이 원에 접선 그리기")
        if draw_tan_circ:
            tan_c1, tan_c2 = st.columns(2)
            with tan_c1: tan_cx = st.number_input("접점 x좌표", value=a_circ + r_circ/np.sqrt(2))
            with tan_c2: half_choice = st.radio("접점 위치", ["상단 점 (y > b)", "하단 점 (y < b)"])
        
        # 원 그리기 (매개변수)
        theta = np.linspace(0, 2*np.pi, 1000)
        circ_x = a_circ + r_circ * np.cos(theta)
        circ_y = b_circ + r_circ * np.sin(theta)
        ax.plot(circ_x, circ_y, 'black', linewidth=1.5, zorder=5)
        
        # 중심점 표시
        ax.plot(a_circ, b_circ, 'ko', markersize=3, zorder=5)

        # 💡 원의 접선 그리기
        if draw_tan_circ:
            if abs(tan_cx - a_circ) <= r_circ + 1e-6: # 원의 정의구역 내일 때
                y_offset = np.sqrt(max(0, r_circ**2 - (tan_cx - a_circ)**2))
                tan_cy = b_circ + y_offset if "상단" in half_choice else b_circ - y_offset
                ax.plot(tan_cx, tan_cy, 'ko', markersize=5, zorder=15)
                
                # 접선 방정식: (x_1 - a)(x - a) + (y_1 - b)(y - b) = r^2
                dx, dy = tan_cx - a_circ, tan_cy - b_circ
                if abs(dy) < 1e-6: # 수직 접선
                    ax.axvline(tan_cx, color='black', linewidth=1.0, zorder=4)
                else:
                    tan_line_y = b_circ + (r_circ**2 - dx*(x_default - a_circ)) / dy
                    ax.plot(x_default, tan_line_y, 'black', linewidth=1.0, zorder=4)

    elif category == "기하: 이차곡선 (포물선, 타원, 쌍곡선)":
        conic_type = st.radio("이차곡선 종류", ["포물선 (위/아래)", "포물선 (왼쪽/오른쪽)", "타원", "쌍곡선 (좌/우)", "쌍곡선 (상/하)"], horizontal=True)
        
        if "포물선" in conic_type:
            c1, c2, c3 = st.columns(3)
            with c1: p_val = st.number_input("초점 상수 (p)", value=1.0)
            with c2: h = st.number_input("꼭짓점 x (h)", value=0.0)
            with c3: k = st.number_input("꼭짓점 y (k)", value=0.0)
            
            t = np.linspace(-15, 15, 2000)
            if "위/아래" in conic_type:
                st.latex(r"4p(y-k) = (x-h)^2")
                ax.plot(t + h, (t**2)/(4*p_val) + k, 'black', linewidth=1.5, zorder=5)
            else:
                st.latex(r"4p(x-h) = (y-k)^2")
                ax.plot((t**2)/(4*p_val) + h, t + k, 'black', linewidth=1.5, zorder=5)
                
        elif conic_type == "타원":
            st.latex(r"\frac{(x-h)^2}{a^2} + \frac{(y-k)^2}{b^2} = 1")
            c1, c2, c3, c4 = st.columns(4)
            with c1: a_el = st.number_input("가로축 반경 (a)", value=3.0, min_value=0.1)
            with c2: b_el = st.number_input("세로축 반경 (b)", value=2.0, min_value=0.1)
            with c3: h = st.number_input("중심 x (h)", value=0.0)
            with c4: k = st.number_input("중심 y (k)", value=0.0)
            
            theta = np.linspace(0, 2*np.pi, 1000)
            ax.plot(h + a_el*np.cos(theta), k + b_el*np.sin(theta), 'black', linewidth=1.5, zorder=5)
            
        elif "쌍곡선" in conic_type:
            if "좌/우" in conic_type: st.latex(r"\frac{(x-h)^2}{a^2} - \frac{(y-k)^2}{b^2} = 1")
            else: st.latex(r"\frac{(x-h)^2}{a^2} - \frac{(y-k)^2}{b^2} = -1")
            
            c1, c2, c3, c4 = st.columns(4)
            with c1: a_hyp = st.number_input("가로 관련 (a)", value=2.0, min_value=0.1)
            with c2: b_hyp = st.number_input("세로 관련 (b)", value=2.0, min_value=0.1)
            with c3: h = st.number_input("중심 x (h)", value=0.0)
            with c4: k = st.number_input("중심 y (k)", value=0.0)
            
            t = np.linspace(-2.5, 2.5, 1000)
            if "좌/우" in conic_type:
                # sec(t), tan(t) 매개변수 사용 방식을 피하기 위해 cosh, sinh 사용
                x_right = h + a_hyp * np.cosh(t)
                x_left = h - a_hyp * np.cosh(t)
                y_hyp = k + b_hyp * np.sinh(t)
                ax.plot(x_right, y_hyp, 'black', linewidth=1.5, zorder=5)
                ax.plot(x_left, y_hyp, 'black', linewidth=1.5, zorder=5)
            else:
                x_hyp = h + a_hyp * np.sinh(t)
                y_up = k + b_hyp * np.cosh(t)
                y_down = k - b_hyp * np.cosh(t)
                ax.plot(x_hyp, y_up, 'black', linewidth=1.5, zorder=5)
                ax.plot(x_hyp, y_down, 'black', linewidth=1.5, zorder=5)
            
            # 점근선 (선택)
            if st.checkbox("점근선 표시 (선택)", value=False):
                ax.plot(x_default, (b_hyp/a_hyp)*(x_default - h) + k, 'k--', linewidth=1.0, alpha=0.5)
                ax.plot(x_default, -(b_hyp/a_hyp)*(x_default - h) + k, 'k--', linewidth=1.0, alpha=0.5)

    # --- 기존 리스트형 점 및 위치/숨김 제어 UI 유지 ---
    st.markdown("---")
    c_pts, c_lines = st.columns([1.5, 1])
    
    with c_pts:
        st.write("📍 **점 추가 및 세부 제어 (엔터키)**")
        st.text_input("예: 1, 2 또는 1, 2, A", key="new_pt", on_change=add_pt_callback)
        
        for i, pt_dict in enumerate(st.session_state.pts_list):
            col1, col2, col3, col4, col5 = st.columns([2.5, 1.8, 1.8, 2.5, 1.2])
            col1.write(f"`{pt_dict['raw']}`")
            pt_dict['hide_coord'] = col2.checkbox("숫자숨김", value=pt_dict.get('hide_coord', False), key=f"hide_c_{i}")
            pt_dict['hide_line'] = col3.checkbox("점선숨김", value=pt_dict.get('hide_line', False), key=f"hide_l_{i}")
            pt_dict['label_pos'] = col4.selectbox("위치", ["오른쪽 위", "왼쪽 위", "오른쪽 아래", "왼쪽 아래"], 
                                                index=["오른쪽 위", "왼쪽 위", "오른쪽 아래", "왼쪽 아래"].index(pt_dict.get('label_pos', '오른쪽 위')), 
                                                key=f"pos_{i}", label_visibility="collapsed")
            if col5.button("삭제", key=f"del_pt_{i}"):
                st.session_state.pts_list.pop(i)
                st.rerun()

        pos_map = {
            "오른쪽 위": (6, 6, 'left', 'bottom'),
            "왼쪽 위": (-6, 6, 'right', 'bottom'),
            "오른쪽 아래": (6, -6, 'left', 'top'),
            "왼쪽 아래": (-6, -6, 'right', 'top')
        }

        for pt_dict in st.session_state.pts_list:
            try:
                parts = [p.strip() for p in pt_dict['raw'].split(',')]
                px = float(parts[0])
                py = float(parts[1])
                label = parts[2] if len(parts) > 2 else ""

                if not pt_dict.get('hide_line', False):
                    ax.plot([px, px], [0, py], 'k--', linewidth=1, alpha=0.8, zorder=3)
                    ax.plot([0, px], [py, py], 'k--', linewidth=1, alpha=0.8, zorder=3)
                
                ax.plot(px, py, 'ko', markersize=5, zorder=10)
                
                if label:
                    l_off_x, l_off_y, l_ha, l_va = pos_map[pt_dict.get('label_pos', '오른쪽 위')]
                    ax.annotate(rf'$\mathrm{{{label}}}$', xy=(px, py), xytext=(l_off_x, l_off_y), textcoords='offset points', 
                                ha=l_ha, va=l_va, fontsize=13, fontfamily='stix', bbox=bbox_white, zorder=25)

                if not pt_dict.get('hide_coord', False):
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
        st.write("🔗 **두 점 점선 연결**")
        st.text_input("예: 1, 2, 3, 4", key="new_line", on_change=add_line_callback)
        
        for i, line in enumerate(st.session_state.lines_list):
            col1, col2 = st.columns([3, 1])
            col1.write(f"`{line}`")
            if col2.button("삭제", key=f"del_line_{i}"):
                st.session_state.lines_list.pop(i)
                st.rerun()

        for line in st.session_state.lines_list:
            try:
                x1, y1, x2, y2 = map(float, line.split(','))
                ax.plot([x1, x2], [y1, y2], 'k--', linewidth=1.5, zorder=4)
            except: pass

    st.markdown("---")
    o_pos = st.radio("원점(O) 기호 위치 선택", ["기본 (왼쪽 아래)", "오른쪽 아래", "왼쪽 위", "오른쪽 위", "숨기기"], horizontal=True)

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
    
    if o_pos != "숨기기":
        if o_pos == "기본 (왼쪽 아래)": o_x, o_y, o_ha, o_va = -8, -8, 'right', 'top'
        elif o_pos == "오른쪽 아래": o_x, o_y, o_ha, o_va = 8, -8, 'left', 'top'
        elif o_pos == "왼쪽 위": o_x, o_y, o_ha, o_va = -8, 8, 'right', 'bottom'
        elif o_pos == "오른쪽 위": o_x, o_y, o_ha, o_va = 8, 8, 'left', 'bottom'
        
        ax.annotate(r'$\mathrm{O}$', xy=(0, 0), xytext=(o_x, o_y), textcoords='offset points', 
                    ha=o_ha, va=o_va, fontsize=13, fontfamily='stix', bbox=bbox_white, zorder=20)

    ax.set_xticks([])
    ax.set_yticks([])

with col_right:
    st.pyplot(fig)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=400, bbox_inches="tight", transparent=True)
    st.download_button("📥 시험지용 그래프 다운로드 (PNG)", data=buf.getvalue(), file_name="math_graph.png", mime="image/png")
