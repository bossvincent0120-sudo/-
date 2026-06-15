import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
import matplotlib.patheffects as path_effects

# 1. 頁面佈局設定
st.set_page_config(layout="wide", page_title="懸吊式比重計數位雙生")
st.title("📊 廣義幾何懸吊式比重計系統 (數位雙生版)")

# 2. UI 佈局 (完全對標您的截圖)
col_ui1, col_ui2, col_ui3 = st.columns([1, 2, 2])
with col_ui1:
    lang = st.radio("🌐 Language", ['中文', 'English'])
with col_ui2:
    shape_opts = ["圓柱體 (P=2)", "長方薄板 (P=2)", "三角薄板 (P=3)", "圓錐體 (P=4)"]
    shape_label = st.selectbox("幾何形狀", shape_opts)
with col_ui3:
    col_l1, col_l2 = st.columns(2)
    L_total = col_l1.number_input("總長度 L", value=40.0)
    L_out = col_l2.number_input("水外長 L_out", value=20.0)

col_s1, col_s2 = st.columns(2)
C1 = col_s1.slider("線性誤差 C1", 0.0, 0.4, 0.1)
C2 = col_s2.slider("二次誤差 C2", 0.0, 0.4, 0.0)

# 3. 物理運算邏輯
shape_idx = shape_opts.index(shape_label)
P_VALUES = [2, 2, 3, 4]
P = P_VALUES[shape_idx]
n = P - 2
x_ratio = L_out / L_total if L_total > 0 else 0
d_ideal = 1 - (x_ratio**P)
E_x = (C1 * x_ratio) + (C2 * (x_ratio**2))
d_true = max(0.0, d_ideal - E_x)
W_fixed = 1.0
FB_mag = d_ideal
T_mag = max(0.0, (W_fixed + E_x) - FB_mag)

# 4. 數據看板 (與截圖顯示效果一致)
st.markdown("---")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("真實比重 (d)", f"{d_true:.4f}")
m2.metric("張力 (T)", f"{T_mag:.4f}")
m3.metric("浮力 (Fb)", f"{FB_mag:.4f}")
m4.metric("重力 (W)", f"{W_fixed:.4f}")
m5.metric("干擾矩 (E)", f"{E_x:.4f}")

# 5. 繪圖引擎 (精準配色對標版)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
scale = max(50, L_total * 1.3)

# Ax1: 物理受力平衡模型
ax1.set_xlim(-scale*0.8, scale*0.8); ax1.set_ylim(-scale*1.3, scale*1.0)
ax1.axhline(0, color='#3498db', lw=2, alpha=0.3)
ax1.axis('off')

# 繪製幾何實體
theta = np.deg2rad(45)
cos_t, sin_t = np.cos(theta), np.sin(theta)
p_top = np.array([-L_out * sin_t, L_out * cos_t])
def get_pos(s): return p_top + np.array([s * sin_t, -s * cos_t])
w = scale * 0.05
ax1.add_patch(Polygon([get_pos(0)-np.array([cos_t, sin_t])*w, get_pos(0)+np.array([cos_t, sin_t])*w, 
                       get_pos(L_total)+np.array([cos_t, sin_t])*w, get_pos(L_total)-np.array([cos_t, sin_t])*w], 
                      closed=True, facecolor='#d5dbdb', edgecolor='#7f8c8d', lw=2))

# 向量與質心/浮心精準繪製
v_arrow_s = scale * 0.45
# T (🔵)
ax1.arrow(p_top[0], p_top[1], 0, T_mag*v_arrow_s, color='#0000FF', lw=3, head_width=scale*0.03)
ax1.text(p_top[0]-5, p_top[1]+T_mag*v_arrow_s+3, 'T', color='#0000FF', fontsize=16, fontweight='bold')

# W (🟡)
p_cg = get_pos(L_total * (P-1)/P)
ax1.plot(p_cg[0], p_cg[1], marker='+', color='#DAA520', markersize=14, markeredgewidth=4)
ax1.arrow(p_cg[0], p_cg[1], 0, -W_fixed*v_arrow_s, color='#DAA520', lw=3, head_width=scale*0.03)
ax1.text(p_cg[0]+3, p_cg[1]-W_fixed*v_arrow_s-8, 'W (CG)', color='#DAA520', fontsize=16, fontweight='bold')

# Fb (🔴)
z_cb = L_total * ((P-1)/P) * ((1 - x_ratio**P) / (1 - x_ratio**(P-1))) if x_ratio < 0.99 else L_total
p_cb = get_pos(z_cb)
ax1.plot(p_cb[0], p_cb[1], 'ro', markersize=10, markeredgecolor='white')
ax1.arrow(p_cb[0], p_cb[1], 0, FB_mag*v_arrow_s, color='#FF0000', lw=3, head_width=scale*0.03)
ax1.text(p_cb[0]-8, p_cb[1]+FB_mag*v_arrow_s+3, 'Fb (CB)', color='#FF0000', fontsize=16, fontweight='bold')

# Ax2: 數據曲線
x_m = np.linspace(0, 1, 100)
ax2.plot(x_m, 1-x_m**P, color='#ced4da', linestyle='--', label="Theory Ideal")
ax2.plot(x_m, 1-x_m**P-(C1*x_m+C2*x_m**2), color='#28a745', lw=3, label="Calibrated Model")
ax2.scatter(x_ratio, d_true, color='#FF0000', s=150, zorder=10)
ax2.grid(True, alpha=0.2); ax2.legend()

st.pyplot(fig)
plt.close(fig)
