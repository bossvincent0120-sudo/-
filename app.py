import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Ellipse
import matplotlib.patheffects as path_effects
import urllib.request
import os

# --- 0. 網頁配置設定 ---
st.set_page_config(layout="wide", page_title="懸吊式比重計數位雙生")

# --- 1. 字體與環境初始化 ---
@st.cache_resource
def load_fonts():
    font_path = "NotoSansCJKtc-Regular.otf"
    if not os.path.exists(font_path):
        try:
            url = "https://raw.githubusercontent.com/googlefonts/noto-cjk/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
            urllib.request.urlretrieve(url, font_path)
        except: pass
    
    tc_font = FontProperties(fname=font_path) if os.path.exists(font_path) else FontProperties()
    tc_font_bold = FontProperties(fname=font_path, weight='bold') if os.path.exists(font_path) else FontProperties(weight='bold')
    return tc_font, tc_font_bold

tc_font, tc_font_bold = load_fonts()
plt.rcParams['axes.unicode_minus'] = False 

# --- 2. 雙語字典庫 ---
UI_TEXT = {
    '中文': {
        'shapes': [("圓柱體 (Cylinder, P=2)", 0), ("長方薄板 (Rect Plate, P=2)", 1), 
                   ("三角薄板 (Tri Plate, P=3)", 2), ("圓錐體 (Cone, P=4)", 3)],
        'labels': ['幾何形狀:', '總長度 L:', '水外長 L_out:', '線性誤差 C1:', '二次誤差 C2:'],
        'report_title': "廣義幾何懸吊式比重計系統 (數位雙生版)",
        'vec_d': "真實比重 (d)", 'vec_W': "重力 (W)", 'vec_Fb': "浮力 (Fb)", 'vec_T': "張力 (T)",
        'ax1_title': "【實體層】幾何受力平衡與重心(CG)/浮心(CB)分析",
        'ax2_title': "【數據層】校正演算模型"
    },
    'English': {
        'shapes': [("Cylinder (P=2)", 0), ("Rect Plate (P=2)", 1), 
                   ("Tri Plate (P=3)", 2), ("Cone (P=4)", 3)],
        'labels': ['Shape:', 'Total L:', 'L_out:', 'Linear Err C1:', 'Quad Err C2:'],
        'report_title': "Suspended Torque Hydrometer Digital Twin",
        'vec_d': "True SG (d)", 'vec_W': "Weight (W)", 'vec_Fb': "Buoyancy (Fb)", 'vec_T': "Tension (T)",
        'ax1_title': "[Physical] Force, CG & CB Analysis",
        'ax2_title': "[Data] Calibration Algorithm"
    }
}

# --- 2.5 Session State 初始設定 ---
if 'c1_val' not in st.session_state: st.session_state.c1_val = 0.00
if 'c2_val' not in st.session_state: st.session_state.c2_val = 0.00

# --- 3. Streamlit UI 控制項 ---
lang = st.radio("🌐 Language:", ['中文', 'English'], horizontal=True)
t = UI_TEXT[lang]

col_top1, col_top2, col_top3 = st.columns(3)
with col_top1:
    shape_options = [s[0] for s in t['shapes']]
    selected_shape = st.selectbox(t['labels'][0], shape_options)
    shape_idx = shape_options.index(selected_shape)
with col_top2:
    L_total = st.number_input(t['labels'][1], value=40.0, min_value=0.1, step=1.0)
with col_top3:
    L_out = st.number_input(t['labels'][2], value=20.0, min_value=0.0, step=1.0)

# 【優化項目：防呆】檢查 L_out 與 L_total 邏輯
if L_out > L_total:
    st.error("⚠️ 物理邏輯錯誤：水外長度 (L_out) 不可大於物體總長度 (L)！")
    st.stop()

col_bot1, col_bot2, col_bot3 = st.columns(3)
with col_bot1:
    C1 = st.number_input(t['labels'][3], value=st.session_state.c1_val, step=0.01)
with col_bot2:
    C2 = st.number_input(t['labels'][4], value=st.session_state.c2_val, step=0.01)
with col_bot3:
    P_temp = [2, 2, 3, 4][shape_idx]
    x_ratio_temp = L_out / L_total if L_total > 0 else 0
    d_exp_input = 1 - (x_ratio_temp**P_temp)
    st.metric("儀器實測值 (d_exp):", f"{d_exp_input:.4f}")

# --- 3.5 虛擬實驗室：動態物理誤差模擬與標定 ---
with st.expander("🔬 虛擬實驗室：物理誤差模擬與標定演算", expanded=True):
    st.markdown("本區模擬現實探頭的測試狀況。系統會根據幾何形狀的特性，自動模擬出對應的真實固體比重 ($d_{std}$)，供最小平方法進行動態擬合：")
    
    num_pts = st.number_input("欲模擬的採樣點數量 (N):", min_value=2, max_value=10, value=3, step=1)
    
    true_c1 = [0.035, 0.048, 0.075, 0.110][shape_idx]
    true_c2 = [0.012, 0.020, 0.040, 0.065][shape_idx]
    
    X_fit, Y_fit = [], []
    
    for i in range(int(num_pts)):
        st.markdown(f"**第 {i+1} 組模擬數據**")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            l_i = st.number_input(f"總長度 L_{i+1}", value=40.0, min_value=0.1, step=1.0, key=f"L_{i}")
        with col_f2:
            default_lout = max(0.0, min(float(l_i), 20.0 - i * 5.0))
            lout_i = st.number_input(f"水外長 L_out_{i+1}", value=default_lout, min_value=0.0, step=1.0, key=f"Lout_{i}")
        
        # 【優化項目：防呆】模擬組數據防呆
        if lout_i > l_i:
            st.error(f"⚠️ 第 {i+1} 組數據 L_out > L，請修正！")
            st.stop()
        
        x_i = lout_i / l_i if l_i > 0 else 0
        P_fit = [2, 2, 3, 4][shape_idx]
        d_exp_i = 1 - (x_i**P_fit) 
        
        np.random.seed(int(x_i * 1000 + shape_idx))
        noise = np.random.uniform(-0.002, 0.002)
        d_std_i = d_exp_i - (true_c1 * x_i) - (true_c2 * (x_i**2)) + noise
        
        st.caption(f"💡 x = {x_i:.3f} | d_exp = {d_exp_i:.4f} | 真實比重 d_std = {d_std_i:.4f}")
        
        X_fit.append([x_i, x_i**2])
        Y_fit.append(d_exp_i - d_std_i) 
    
    # 【優化項目：自動代入】
    if st.button("執行擬合並自動套用模型", type="primary"):
        c, _, _, _ = np.linalg.lstsq(np.array(X_fit), np.array(Y_fit), rcond=None)
        st.session_state.c1_val = float(c[0])
        st.session_state.c2_val = float(c[1])
        st.rerun()

# --- 4. 物理運算 ---
P_VALUES = [2, 2, 3, 4]
P = P_VALUES[shape_idx]
x_ratio = L_out / L_total if L_total > 0 else 0

d_ideal = 1 - (x_ratio**P)
E_x = (C1 * x_ratio) + (C2 * (x_ratio**2))
d_true = max(0.0, d_ideal - E_x)

W_fixed = 1.0  
FB_mag = d_ideal
T_mag = max(0.0, (W_fixed + E_x) - FB_mag)

z_cg_val = L_total * (P - 1) / P
z_cb_val = L_total if x_ratio >= 0.999 else L_total * ((P-1)/P) * ((1 - x_ratio**P) / (1 - x_ratio**(P-1)))

# --- 5. 藍色數據儀表板 ---
st.markdown(f"""
<div style="background-color: #f1f8ff; padding: 15px; border-radius: 8px; border-left: 10px solid #007bff; margin-bottom: 20px; font-family: sans-serif;">
    <h3 style="margin: 0 0 12px 0; color: #0056b3; font-size: 18px;">{t['report_title']}</h3>
    <div style="display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr; gap: 10px; align-items: center; font-size: 14px;">
        <span><b>待測物:</b> {t['shapes'][shape_idx][0]}</span>
        <span style="color: #0056b3;">🔵 <b>{t['vec_T']}</b> = {T_mag:.4f}</span>
        <span style="color: #d9534f;">🔴 <b>{t['vec_Fb']}</b> = {FB_mag:.4f}</span>
        <span style="color: #f0ad4e;">🟡 <b>{t['vec_W']}</b> = {W_fixed:.4f}</span>
        <span style="color: #28a745;">🟢 <b>{t['vec_d']}</b> = {d_true:.4f}</span>
        <span style="color: #6f42c1;">🟣 <b>實測值(d_exp)</b> = {d_exp_input:.4f}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. 繪圖區 ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), gridspec_kw={'width_ratios': [1, 1.1]})
pe = [path_effects.withStroke(linewidth=3, foreground="white")]
scale = max(50, L_total * 1.3)
ax1.axhline(0, color='#3498db', lw=3, alpha=0.5) 
ax1.fill_between([-scale, scale], -scale*1.5, 0, color='#3498db', alpha=0.1)

theta = np.deg2rad(45)
cos_t, sin_t = np.cos(theta), np.sin(theta)
p_top = np.array([-L_out * sin_t, L_out * cos_t])
def get_pos(s): return p_top + np.array([s * sin_t, -s * cos_t])

w = scale * 0.05
if shape_idx == 0: ax1.add_patch(Polygon([get_pos(0)-v_perp*w, get_pos(0)+v_perp*w, get_pos(L_total)+v_perp*w, get_pos(L_total)-v_perp*w], closed=True, facecolor='#d5dbdb'))
elif shape_idx == 2: ax1.add_patch(Polygon([get_pos(0), get_pos(L_total)+v_perp*w*3, get_pos(L_total)-v_perp*w*3], closed=True, facecolor='#fdebd0'))
elif shape_idx == 3: ax1.add_patch(Polygon([get_pos(0), get_pos(L_total)+v_perp*w*2.5, get_pos(L_total)-v_perp*w*2.5], closed=True, facecolor='#ebedef'))

ax1.set_xlim(-scale*0.8, scale*0.8); ax1.set_ylim(-scale*1.3, scale*1.0); ax1.axis('off')

x_m = np.linspace(0, 1, 100)
ax2.plot(x_m, 1 - (x_m**P), color='#ced4da', linestyle='--', label="Theory Ideal")
ax2.plot(x_m, np.maximum(0.0, 1 - (x_m**P) - (C1*x_m + C2*x_m**2)), color='#28a745', lw=3, label="Calibrated Model")
ax2.scatter(x_ratio, d_exp_input, color='#6f42c1', s=100, label="Raw (d_exp)")
ax2.scatter(x_ratio, d_true, color='red', s=150, label="True (d_true)")
ax2.legend(); ax2.grid(True, alpha=0.2)
st.pyplot(fig)
