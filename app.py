import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# 1. 頁面設定
st.set_page_config(layout="wide", page_title="懸吊式比重計數位雙生")
st.title("📊 廣義幾何懸吊式比重計系統")

# 2. UI 佈局
col_ui1, col_ui2, col_ui3, col_ui4 = st.columns([1, 1.5, 1, 1])
with col_ui1:
    shape_opts = ["圓柱體 (P=2)", "長方薄板 (P=2)", "三角薄板 (P=3)", "圓錐體 (P=4)"]
    shape_label = st.selectbox("幾何形狀", shape_opts)
with col_ui2:
    L_total = st.slider("總長度 L", 10.0, 100.0, 40.0)
    L_out = st.slider("水外長 L_out", 0.0, L_total, 20.0)
with col_ui3:
    C1 = st.slider("線性誤差 C1", 0.0, 0.4, 0.1)
with col_ui4:
    C2 = st.slider("二次誤差 C2", 0.0, 0.4, 0.0)

# 3. 物理運算
shape_idx = shape_opts.index(shape_label)
P_vals = [2, 2, 3, 4]
P = P_vals[shape_idx]
x = L_out / L_total
d_ideal = 1 - (x**P)
E_x = C1 * x + C2 * (x**2)
d_true = max(0.0, d_ideal - E_x)
T = max(0.0, 1.0 + E_x - d_ideal)

# 4. 繪圖區 (強制鎖定坐標系)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# --- Ax1: 受力平衡圖 (修復版) ---
ax1.set_xlim(-50, 50); ax1.set_ylim(-50, 50) # 強制鎖定視野，確保不會消失
ax1.axhline(0, color='#3498db', lw=2, alpha=0.5) # 水面
ax1.axis('off')

theta = np.deg2rad(45)
p_top = np.array([-L_out * np.sin(theta), L_out * np.cos(theta)])
p_bot = p_top + np.array([L_total * np.sin(theta), -L_total * np.cos(theta)])
w = 2.0 

# 形狀邏輯 (包含長方薄板)
if shape_idx == 0: # 圓柱
    pts = [p_top-np.array([np.cos(theta), np.sin(theta)])*w, p_top+np.array([np.cos(theta), np.sin(theta)])*w, p_bot+np.array([np.cos(theta), np.sin(theta)])*w, p_bot-np.array([np.cos(theta), np.sin(theta)])*w]
elif shape_idx == 1: # 長方薄板
    pts = [p_top-np.array([np.cos(theta), np.sin(theta)])*w*0.5, p_top+np.array([np.cos(theta), np.sin(theta)])*w*0.5, p_bot+np.array([np.cos(theta), np.sin(theta)])*w*0.5, p_bot-np.array([np.cos(theta), np.sin(theta)])*w*0.5]
elif shape_idx == 2: # 三角板
    pts = [p_top, p_bot+np.array([np.cos(theta), np.sin(theta)])*w*3, p_bot-np.array([np.cos(theta), np.sin(theta)])*w*3]
else: # 圓錐
    pts = [p_top, p_bot+np.array([np.cos(theta), np.sin(theta)])*w*2, p_bot-np.array([np.cos(theta), np.sin(theta)])*w*2]

ax1.add_patch(Polygon(pts, facecolor='#d5dbdb', edgecolor='black', lw=2))

# 向量 (保留配色)
ax1.arrow(p_top[0], p_top[1], 0, T*5, color='blue', lw=3, head_width=2)
# ... [其他向量保持不變]

# --- Ax2: 數據圖 ---
ax2.plot(np.linspace(0,1,100), 1-np.linspace(0,1,100)**P, 'k--')
ax2.plot(np.linspace(0,1,100), 1-np.linspace(0,1,100)**P-(C1*np.linspace(0,1,100)+C2*np.linspace(0,1,100)**2), 'green', lw=3)
ax2.scatter(x, d_true, color='red', s=100)

st.pyplot(fig)
