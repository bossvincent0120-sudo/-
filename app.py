import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse

# 1. 頁面設定
st.set_page_config(layout="wide", page_title="懸吊式比重計數位雙生")
st.title("📊 廣義幾何懸吊式比重計系統")

# 2. UI 控制面板
col_ui1, col_ui2, col_ui3, col_ui4 = st.columns([1, 1.5, 1, 1])
with col_ui1:
    shape_opts = ["圓柱體 (P=2)", "三角薄板 (P=3)", "圓錐體 (P=4)"]
    shape_label = st.selectbox("幾何形狀", shape_opts)
with col_ui2:
    L_total = st.slider("總長度 L", 10.0, 100.0, 40.0)
    L_out = st.slider("水外長 L_out", 0.0, L_total, 20.0)
with col_ui3:
    C1 = st.slider("線性誤差 C1", 0.0, 0.4, 0.1)
with col_ui4:
    C2 = st.slider("二次誤差 C2", 0.0, 0.4, 0.0)

# 3. 物理運算邏輯
shape_idx = shape_opts.index(shape_label)
P_vals = [2, 3, 4]
P = P_vals[shape_idx]
x = L_out / L_total
d_ideal = 1 - (x**P)
E_x = C1 * x + C2 * (x**2)
d_true = max(0.0, d_ideal - E_x)
T = max(0.0, 1.0 + E_x - d_ideal)

# 4. 數值儀表板
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("真實比重 (d)", f"{d_true:.4f}")
m2.metric("張力 (T)", f"{T:.4f}")
m3.metric("浮力 (Fb)", f"{d_ideal:.4f}")
m4.metric("重力 (W)", "1.0000")

# 5. 繪圖區 (強制等比例與精準配色)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
ax1.set_aspect('equal')
ax1.axis('off')

# 幾何中心計算
theta = np.deg2rad(45)
p_top = np.array([-L_out * np.sin(theta), L_out * np.cos(theta)])
p_bot = p_top + np.array([L_total * np.sin(theta), -L_total * np.cos(theta)])
# CG 和 CB 位子 (相對於頂端的距離)
z_cg = L_total * (P-1)/P
z_cb = L_total * ((P-1)/P) * ((1 - x**P) / (1 - x**(P-1))) if x < 0.99 else L_total

# 繪製形狀
w = 2.0
if shape_idx == 0: # 圓柱
    ax1.add_patch(Polygon([p_top-np.array([np.cos(theta), np.sin(theta)])*w, p_top+np.array([np.cos(theta), np.sin(theta)])*w, 
                           p_bot+np.array([np.cos(theta), np.sin(theta)])*w, p_bot-np.array([np.cos(theta), np.sin(theta)])*w], 
                          facecolor='#d5dbdb', edgecolor='black'))
elif shape_idx == 1: # 三角
    ax1.add_patch(Polygon([p_top, p_bot+np.array([np.cos(theta), np.sin(theta)])*w*2, p_bot-np.array([np.cos(theta), np.sin(theta)])*w*2], 
                          facecolor='#fdebd0', edgecolor='#d35400'))
else: # 圓錐
    ax1.add_patch(Polygon([p_top, p_bot+np.array([np.cos(theta), np.sin(theta)])*w*2, p_bot-np.array([np.cos(theta), np.sin(theta)])*w*2], 
                          facecolor='#ebedef', edgecolor='black'))

# 繪製向量與 CG/CB 標記
# T
ax1.arrow(p_top[0], p_top[1], 0, T*5, color='blue', lw=3, head_width=1)
ax1.text(p_top[0]-2, p_top[1]+T*5+2, 'T', color='blue', fontsize=14, fontweight='bold')
# W (CG)
cg_pos = p_top + np.array([z_cg*np.sin(theta), -z_cg*np.cos(theta)])
ax1.plot(cg_pos[0], cg_pos[1], '+', color='#DAA520', markersize=15, markeredgewidth=4)
ax1.arrow(cg_pos[0], cg_pos[1], 0, -5, color='#DAA520', lw=3, head_width=1)
ax1.text(cg_pos[0]+2, cg_pos[1]-8, 'W (CG)', color='#DAA520', fontsize=14, fontweight='bold')
# Fb (CB)
cb_pos = p_top + np.array([z_cb*np.sin(theta), -z_cb*np.cos(theta)])
ax1.plot(cb_pos[0], cb_pos[1], 'ro', markersize=8)
ax1.arrow(cb_pos[0], cb_pos[1], 0, d_ideal*5, color='red', lw=3, head_width=1)
ax1.text(cb_pos[0]-8, cb_pos[1]+d_ideal*5+2, 'Fb (CB)', color='red', fontsize=14, fontweight='bold')

# 校正模型圖
x_vals = np.linspace(0, 1, 100)
ax2.plot(x_vals, 1-x_vals**P, 'k--', alpha=0.3, label="Theory")
ax2.plot(x_vals, 1-x_vals**P-(C1*x_vals+C2*x_vals**2), 'green', lw=3, label="Calibrated")
ax2.scatter(x, d_true, color='red', s=100)
ax2.legend()

st.pyplot(fig)
