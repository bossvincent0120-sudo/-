import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# 1. 頁面佈局設定
st.set_page_config(layout="wide")
st.title("📊 廣義幾何懸吊式比重計系統")

# 2. UI 佈局
col_ui1, col_ui2, col_ui3 = st.columns([1, 1, 1])
with col_ui1:
    shape_label = st.selectbox("幾何形狀", ["圓柱體 (P=2)", "三角薄板 (P=3)", "圓錐體 (P=4)"])
with col_ui2:
    L_total = st.number_input("總長度 L", value=40.0)
    L_out = st.number_input("水外長 L_out", value=20.0)
with col_ui3:
    C1 = st.slider("線性誤差 C1", 0.0, 0.4, 0.1)
    C2 = st.slider("二次誤差 C2", 0.0, 0.4, 0.0)

# 3. 物理運算
shape_idx = ["圓柱體 (P=2)", "三角薄板 (P=3)", "圓錐體 (P=4)"].index(shape_label)
P_VALUES = [2, 3, 4]
P = P_VALUES[shape_idx]
n = P - 2
x_ratio = L_out / L_total if L_total > 0 else 0
d_true = max(0.0, (1 - x_ratio**P) - (C1 * x_ratio + C2 * x_ratio**2))
T_mag = max(0.0, (1.0 + (C1 * x_ratio + C2 * x_ratio**2)) - (1 - x_ratio**P))

# 4. 數據看板
m1, m2, m3 = st.columns(3)
m1.metric("真實比重 (d)", f"{d_true:.4f}")
m2.metric("張力 (T)", f"{T_mag:.4f}")
m3.metric("浮力 (Fb)", f"{1 - x_ratio**P:.4f}")

# 5. 繪圖區 (強制等比例修正)
fig, ax1 = plt.subplots(figsize=(6, 6))
ax1.set_aspect('equal') # 關鍵：鎖定長寬比，圖形才不會變形
ax1.axis('off')

# 幾何座標
theta = np.deg2rad(45)
p_top = np.array([-L_out * np.sin(theta), L_out * np.cos(theta)])
p_bot = p_top + np.array([(L_total) * np.sin(theta), -(L_total) * np.cos(theta)])

# 繪製形狀
w = 2.0
if shape_idx == 0: # 圓柱
    ax1.add_patch(Polygon([p_top-np.array([np.cos(theta), np.sin(theta)])*w, p_top+np.array([np.cos(theta), np.sin(theta)])*w, 
                           p_bot+np.array([np.cos(theta), np.sin(theta)])*w, p_bot-np.array([np.cos(theta), np.sin(theta)])*w], 
                          facecolor='#d5dbdb', edgecolor='black'))
elif shape_idx == 2: # 圓錐
    ax1.add_patch(Polygon([p_top, p_bot+np.array([np.cos(theta), np.sin(theta)])*w*2, p_bot-np.array([np.cos(theta), np.sin(theta)])*w*2], 
                          facecolor='#ebedef', edgecolor='black'))

# 向量 (精準配色)
ax1.arrow(p_top[0], p_top[1], 0, 5, color='blue', lw=3, head_width=1, label='T')
ax1.arrow(p_top[0]+5, p_top[1]-5, 0, -5, color='#DAA520', lw=3, head_width=1, label='W')
ax1.arrow(p_top[0]+10, p_top[1]-10, 0, 5, color='red', lw=3, head_width=1, label='Fb')

st.pyplot(fig)
