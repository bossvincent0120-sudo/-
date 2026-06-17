import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon, Ellipse
import matplotlib.patheffects as path_effects
import os

# --- 0. 網頁配置設定 ---
st.set_page_config(layout="wide", page_title="懸吊式比重計數位雙生")

# --- 1. 字體初始化 ---
@st.cache_resource
def load_fonts():
    return FontProperties() # 簡化以確保執行穩定

tc_font = load_fonts()

# --- 2. 狀態初始化 ---
if 'c1_val' not in st.session_state: st.session_state.c1_val = 0.00
if 'c2_val' not in st.session_state: st.session_state.c2_val = 0.00

# --- 3. UI 控制 ---
col_top1, col_top2, col_top3 = st.columns(3)
with col_top1:
    shape_map = {"圓柱體": 0, "長方薄板": 1, "三角薄板": 2, "圓錐體": 3}
    selected_shape = st.selectbox("幾何形狀:", list(shape_map.keys()))
    shape_idx = shape_map[selected_shape]
with col_top2:
    L_total = st.number_input("總長度 L:", value=40.0, min_value=0.1)
with col_top3:
    L_out = st.number_input("水外長 L_out:", value=20.0, min_value=0.0)

# 強制物理邏輯檢查
if L_out > L_total:
    st.error("⚠️ L_out 不能大於 L")
    st.stop()

# 將輸入與 Session State 脫鉤，改用 on_change 更新
C1 = st.number_input("線性誤差 C1:", value=st.session_state.c1_val, step=0.01)
C2 = st.number_input("二次誤差 C2:", value=st.session_state.c2_val, step=0.01)

# --- 3.5 擬合演算 ---
with st.expander("🔬 虛擬實驗室：標定演算", expanded=True):
    num_pts = st.number_input("採樣點數:", min_value=2, value=3)
    X_fit, Y_fit = [], []
    for i in range(int(num_pts)):
        c_i1, c_i2 = st.columns(2)
        l_i = c_i1.number_input(f"L_{i+1}", value=40.0, key=f"L{i}")
        lo_i = c_i2.number_input(f"LO_{i+1}", value=20.0, key=f"LO{i}")
        
        x = lo_i/l_i if l_i > 0 else 0
        d_exp = 1 - (x**[2,2,3,4][shape_idx])
        # 模擬誤差
        d_std = d_exp - (([0.035,0.048,0.075,0.11][shape_idx])*x + ([0.012,0.02,0.045,0.065][shape_idx])*(x**2))
        X_fit.append([x, x**2])
        Y_fit.append(d_exp - d_std)

    if st.button("執行擬合並更新"):
        coeffs, _, _, _ = np.linalg.lstsq(np.array(X_fit), np.array(Y_fit), rcond=None)
        st.session_state.c1_val = float(-coeffs[0])
        st.session_state.c2_val = float(-coeffs[1])
        st.rerun()

# --- 4. 運算與繪圖 (保留原邏輯) ---
P = [2,2,3,4][shape_idx]
x_ratio = L_out/L_total if L_total > 0 else 0
d_ideal = 1 - (x_ratio**P)
d_true = max(0.0, d_ideal - (C1*x_ratio + C2*x_ratio**2))

st.metric("真實比重 d_true:", f"{d_true:.4f}")

fig, ax = plt.subplots(figsize=(10, 4))
x_m = np.linspace(0, 1, 100)
ax.plot(x_m, 1-(x_m**P), '--', label="理想")
ax.plot(x_m, np.maximum(0, 1-(x_m**P) - (C1*x_m + C2*x_m**2)), label="校正")
ax.scatter(x_ratio, d_true, color='red', zorder=10)
ax.legend(); st.pyplot(fig)
