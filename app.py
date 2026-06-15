import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse

# 1. 網頁配置
st.set_page_config(layout="wide", page_title="懸吊式比重計數位雙生")
st.title("📊 廣義幾何懸吊式比重計系統")

# 2. UI 佈局
col1, col2 = st.columns([1, 3])
with col1:
    lang = st.radio("Language", ['中文', 'English'])
    shape_opts = ["圓柱體 (P=2)", "長方薄板 (P=2)", "三角薄板 (P=3)", "圓錐體 (P=4)"]
    shape_label = st.selectbox("幾何形狀", shape_opts)
    L_total = st.number_input("總長度 L", value=40.0)
    L_out = st.number_input("水外長 L_out", value=20.0)
    C1 = st.slider("線性誤差 C1", 0.0, 0.4, 0.1)
    C2 = st.slider("二次誤差 C2", 0.0, 0.4, 0.0)

# 3. 物理運算
shape_idx = shape_opts.index(shape_label)
P_VALUES = [2, 2, 3, 4]
P = P_VALUES[shape_idx]
x_ratio = L_out / L_total if L_total > 0 else 0
d_ideal = 1 - (x_ratio**P)
E_x = (C1 * x_ratio) + (C2 * (x_ratio**2))
d_true = max(0.0, d_ideal - E_x)
T_mag = max(0.0, (1.0 + E_x) - d_ideal)

# 4. 數據監控顯示
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("真實比重 (d)", f"{d_true:.4f}")
m2.metric("張力 (T)", f"{T_mag:.4f}", delta_color="normal")
m3.metric("浮力 (Fb)", f"{d_ideal:.4f}")
m4.metric("重力 (W)", "1.0000")

# 5. 繪圖邏輯 (配色對標版)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
scale = max(50, L_total * 1.3)
ax1.set_xlim(-scale*0.8, scale*0.8); ax1.set_ylim(-scale*1.3, scale*1.0)
ax1.axhline(0, color='#3498db', lw=2, alpha=0.3)
ax1.axis('off')

# 幾何座標計算
theta = np.deg2rad(45)
cos_t, sin_t = np.cos(theta), np.sin(theta)
p_top = np.array([-L_out * sin_t, L_out * cos_t])
def get_pos(s): return p_top + np.array([s * sin_t, -s * cos_t])
p_bot = get_pos(L_total)

# 繪製物體
w = scale * 0.06
pts = [get_pos(0)-np.array([cos_t, sin_t])*w, get_pos(0)+np.array([cos_t, sin_t])*w, 
       get_pos(L_total)+np.array([cos_t, sin_t])*w, get_pos(L_total)-np.array([cos_t, sin_t])*w]
ax1.add_patch(Polygon(pts, facecolor='#d5dbdb', edgecolor='#7f8c8d', lw=2))

# 向量繪製 (顏色精準對標)
v_s = scale * 0.5
# T (Blue)
ax1.arrow(p_top[0], p_top[1], 0, T_mag*v_s, color='#0000FF', lw=3, head_width=scale*0.03)
ax1.text(p_top[0]-5, p_top[1]+T_mag*v_s+3, 'T', color='#0000FF', fontsize=16, fontweight='bold')
# W (Goldenrod)
p_cg = get_pos(L_total * (P-1)/P)
ax1.plot(p_cg[0], p_cg[1], marker='+', color='#DAA520', markersize=14, markeredgewidth=4)
ax1.arrow(p_cg[0], p_cg[1], 0, -1.0*v_s, color='#DAA520', lw=3, head_width=scale*0.03)
ax1.text(p_cg[0]+3, p_cg[1]-1.0*v_s-8, 'W', color='#DAA520', fontsize=16, fontweight='bold')
# Fb (Red)
z_cb = L_total * ((P-1)/P) * ((1 - x_ratio**P) / (1 - x_ratio**(P-1))) if x_ratio < 0.99 else L_total
p_cb = get_pos(z_cb)
ax1.plot(p_cb[0], p_cb[1], 'ro', markersize=10, markeredgecolor='white')
ax1.arrow(p_cb[0], p_cb[1], 0, d_ideal*v_s, color='#FF0000', lw=3, head_width=scale*0.03)
ax1.text(p_cb[0]-8, p_cb[1]+d_ideal*v_s+3, 'Fb', color='#FF0000', fontsize=16, fontweight='bold')

# Ax2: 校正曲線
x_m = np.linspace(0, 1, 100)
ax2.plot(x_m, 1-x_m**P, color='#ced4da', linestyle='--', label="Theory")
ax2.plot(x_m, 1-x_m**P-(C1*x_m+C2*x_m**2), color='#28a745', lw=3, label="Calibrated")
ax2.scatter(x_ratio, d_true, color='#FF0000', s=100)
ax2.legend(); ax2.grid(True, alpha=0.2)

st.pyplot(fig)
plt.close(fig)
