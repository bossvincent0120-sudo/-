import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
import matplotlib.patheffects as path_effects

# 1. 頁面佈局設定
st.set_page_config(layout="wide", page_title="懸吊式比重計數位雙生")
st.title("📊 廣義幾何懸吊式比重計系統 (數位雙生版)")

# 2. UI 佈局
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

# 3. 物理運算
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

# 4. 數據看板
st.markdown("---")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("真實比重 (d)", f"{d_true:.4f}")
m2.metric("張力 (T)", f"{T_mag:.4f}")
m3.metric("浮力 (Fb)", f"{FB_mag:.4f}")
m4.metric("重力 (W)", f"{W_fixed:.4f}")
m5.metric("干擾矩 (E)", f"{E_x:.4f}")

# 5. 繪圖引擎 (整合後的繪圖邏輯)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
pe = [path_effects.withStroke(linewidth=3, foreground="white")]
scale = max(50, L_total * 1.3)

# Ax1: 物理平衡圖
ax1.set_xlim(-scale*0.8, scale*0.8); ax1.set_ylim(-scale*1.3, scale*1.0)
ax1.axhline(0, color='#3498db', lw=3, alpha=0.5)
ax1.fill_between([-scale, scale], -scale*1.5, 0, color='#3498db', alpha=0.1)
ax1.axis('off')

# 計算幾何座標
theta = np.deg2rad(45)
cos_t, sin_t = np.cos(theta), np.sin(theta)
p_top = np.array([-L_out * sin_t, L_out * cos_t])
p_bot = np.array([(L_total - L_out) * sin_t, -(L_total - L_out) * cos_t])
def get_pos(s): return p_top + np.array([s * sin_t, -s * cos_t])

# 繪製物體 (對標您之前的邏輯)
v_perp = np.array([cos_t, sin_t])
w = scale * 0.05
ax1.add_patch(Polygon([get_pos(0)-v_perp*w, get_pos(0)+v_perp*w, get_pos(L_total)+v_perp*w, get_pos(L_total)-v_perp*w], closed=True, facecolor='#d5dbdb', edgecolor='#7f8c8d'))

# 繪製 CG/CB 與 向量箭頭
z_cg = L_total * (P-1)/P
z_cb = L_total * ((P-1)/P) * ((1 - x_ratio**P) / (1 - x_ratio**(P-1))) if x_ratio < 0.99 else L_total
p_cg, p_cb = get_pos(z_cg), get_pos(z_cb)

ax1.plot(p_cg[0], p_cg[1], marker='+', color='goldenrod', markersize=12, zorder=10)
ax1.plot(p_cb[0], p_cb[1], 'ro', markersize=8, zorder=10)
ax1.arrow(p_top[0], p_top[1], 0, T_mag*scale*0.4, color='blue', lw=2, head_width=scale*0.03) # T
ax1.arrow(p_cg[0], p_cg[1], 0, -W_fixed*scale*0.4, color='goldenrod', lw=2, head_width=scale*0.03) # W
ax1.arrow(p_cb[0], p_cb[1], 0, FB_mag*scale*0.4, color='red', lw=2, head_width=scale*0.03) # Fb

# Ax2: 數據曲線
x_m = np.linspace(0, 1, 100)
ax2.plot(x_m, 1-x_m**P, 'g--', alpha=0.3)
ax2.plot(x_m, 1-x_m**P-(C1*x_m+C2*x_m**2), 'green', lw=3)
ax2.scatter(x_ratio, d_true, color='red', s=100)
ax2.grid(True, alpha=0.2)

st.pyplot(fig)
plt.close(fig) # 確保不發生繪圖快取殘留
