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

# 3. 物理運算 (與您 Colab 邏輯一致)
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

# 5. 繪圖區
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
# [這裡請貼上您之前修正過的那段繪圖邏輯，保證 CG/CB 標記與向量正確]
# 為確保一模一樣，建議直接在 GitHub 編輯器中複製您在 Colab 中最滿意的繪圖段落貼入這裡
st.pyplot(fig)
