import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
import matplotlib.patheffects as path_effects

# 頁面設定
st.set_page_config(layout="wide", page_title="懸吊式比重計數位雙生")

st.title("📊 廣義幾何懸吊式比重計系統")

# --- 側邊欄 UI 設定 (對標你的介面) ---
st.sidebar.header("參數控制面板")
lang = st.sidebar.radio("🌐 Language", ['中文', 'English'])

# 形狀定義
shapes_zh = ["圓柱體 (P=2)", "長方薄板 (P=2)", "三角薄板 (P=3)", "圓錐體 (P=4)"]
shapes_en = ["Cylinder (P=2)", "Rect Plate (P=2)", "Tri Plate (P=3)", "Cone (P=4)"]
shape_label = st.sidebar.selectbox("幾何形狀", shapes_zh if lang == '中文' else shapes_en)
shape_idx = (shapes_zh if lang == '中文' else shapes_en).index(shape_label)

L_total = st.sidebar.number_input("總長度 L", value=40.0)
L_out = st.sidebar.number_input("水外長 L_out", value=20.0)
C1 = st.sidebar.slider("線性誤差 C1", 0.0, 0.4, 0.1)
C2 = st.sidebar.slider("二次誤差 C2", 0.0, 0.4, 0.0)

# --- 物理運算 ---
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

# --- 儀表板顯示 ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("真實比重 (d)", f"{d_true:.4f}")
col2.metric("張力 (T)", f"{T_mag:.4f}")
col3.metric("浮力 (Fb)", f"{FB_mag:.4f}")
col4.metric("重力 (W)", f"{W_fixed:.4f}")
col5.metric("誤差 (E)", f"{E_x:.4f}")

# --- 繪圖區 ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
pe = [path_effects.withStroke(linewidth=3, foreground="white")]
scale = max(50, L_total * 1.3)

# 實體平衡繪圖 (簡化版)
ax1.set_xlim(-scale*0.8, scale*0.8)
ax1.set_ylim(-scale*1.2, scale*0.8)
ax1.axhline(0, color='blue', alpha=0.3)
ax1.axis('off')
ax1.set_title("物理受力平衡")

# 繪製物體 (簡單示意)
ax1.add_patch(Polygon([[-5, 20], [5, 20], [5, -20], [-5, -20]], facecolor='#d5dbdb'))

# 繪製向量
ax1.arrow(0, 20, 0, T_mag*5, color='blue', head_width=2) # T
ax1.arrow(0, -5, 0, -W_fixed*5, color='goldenrod', head_width=2) # W
ax1.arrow(0, -10, 0, FB_mag*5, color='red', head_width=2) # Fb

# 數據曲線
x_m = np.linspace(0, 1, 100)
ax2.plot(x_m, 1-x_m**P, 'g--', label="Ideal")
ax2.plot(x_m, 1-x_m**P-(C1*x_m+C2*x_m**2), 'green', lw=3, label="Calibrated")
ax2.scatter(x_ratio, d_true, color='red', s=100)
ax2.set_title("比重校正演算")
ax2.legend()

st.pyplot(fig)
