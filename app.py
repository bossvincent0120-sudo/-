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

# --- 1. 字體與環境初始化 (完全保留您的設定) ---
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

# --- 2. 雙語字典庫 (完全保留) ---
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

# --- 3. Streamlit UI 控制項 (取代 ipywidgets) ---
lang = st.radio("🌐 Language:", ['中文', 'English'], horizontal=True)
t = UI_TEXT[lang]

# 佈局排版對齊您原本的 HBox
col_top1, col_top2, col_top3 = st.columns(3)
with col_top1:
    shape_options = [s[0] for s in t['shapes']]
    selected_shape = st.selectbox(t['labels'][0], shape_options)
    shape_idx = shape_options.index(selected_shape)
with col_top2:
    L_total = st.number_input(t['labels'][1], value=40.0, step=1.0)
with col_top3:
    L_out = st.number_input(t['labels'][2], value=20.0, step=1.0)

# 【修改處】將此列擴充為 3 欄，d_exp 改為自動計算與顯示 (C1, C2 改為 number_input)
col_bot1, col_bot2, col_bot3 = st.columns(3)
with col_bot1:
    C1 = st.number_input(t['labels'][3], value=0.10, step=0.01)
with col_bot2:
    C2 = st.number_input(t['labels'][4], value=0.00, step=0.01)
with col_bot3:
    P_temp = [2, 2, 3, 4][shape_idx]
    x_ratio_temp = L_out / L_total if L_total > 0 else 0
    d_exp_input = 1 - (x_ratio_temp**P_temp)
    st.metric("儀器實測值 d_exp (自動計算):", f"{d_exp_input:.4f}")

# --- 3.5 實驗數據標定與 C1, C2 擬合計算工具 (新增功能) ---
with st.expander("🔬 實驗數據標定與 C1, C2 擬合計算工具"):
    st.markdown("請設定欲輸入的數據組數，並輸入各組的總長度 $L$、水外長 $L_{out}$ 與標準液比重，系統將自動計算 $d_{exp}$ 並擬合：")
    
    num_pts = st.number_input("欲輸入的實驗數據組數 (N):", min_value=2, max_value=10, value=3, step=1)
    
    X_fit = []
    Y_fit = []
    
    for i in range(int(num_pts)):
        st.markdown(f"**第 {i+1} 組數據**")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            l_i = st.number_input(f"總長度 L_{i+1}", value=40.0, step=1.0, key=f"L_{i}")
        with col_f2:
            lout_i = st.number_input(f"水外長 L_out_{i+1}", value=20.0, step=1.0, key=f"Lout_{i}")
        with col_f3:
            # 需輸入標準液的真實比重才能計算殘差誤差
            d_std_i = st.number_input(f"該標準液體真實比重 d_std_{i+1}", value=1.000, step=0.001, format="%.3f", key=f"dstd_{i}")
        
        x_i = lout_i / l_i if l_i > 0 else 0
        P_fit = [2, 2, 3, 4][shape_idx]
        d_exp_i = 1 - (x_i**P_fit)
        st.caption(f"💡 自動計算結果：露出比例 x = {x_i:.3f} | 儀器實測值 d_exp_{i+1} = {d_exp_i:.4f}")
        
        X_fit.append([x_i, x_i**2])
        Y_fit.append(d_exp_i - d_std_i)
    
    if st.button("執行多項式擬合計算"):
        try:
            c, _, _, _ = np.linalg.lstsq(np.array(X_fit), np.array(Y_fit), rcond=None)
            st.success(f"✅ 擬合成功！建議請將上方滑桿設定為： **線性誤差 C1 = {c[0]:.4f}** , **二次誤差 C2 = {c[1]:.4f}**")
        except Exception as e:
            st.error("計算失敗，請檢查輸入的數據。")

# --- 4. 物理運算 (完全保留您的原始邏輯) ---
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

if x_ratio >= 0.999: 
    z_cb_val = L_total
else:
    z_cb_val = L_total * ((P-1)/P) * ((1 - x_ratio**P) / (1 - x_ratio**(P-1)))

# --- 5. 藍色數據儀表板 (保留您的 HTML 設計，透過 st.markdown 渲染) ---
# 【修改處】將 CSS Grid 欄位擴增，加入紫色的實測值 (d_exp) 顯示
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
    <div style="margin-top: 10px; font-size: 12px; color: #555; border-top: 1px solid #ddd; padding-top: 5px;">
        微積分幾何中心檢驗：質心 (CG) = {z_cg_val:.2f} | 浮心 (CB) = {z_cb_val:.2f}
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. 繪圖區 (一字不漏複製您的 Matplotlib 程式碼) ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), gridspec_kw={'width_ratios': [1, 1.1]})
pe = [path_effects.withStroke(linewidth=3, foreground="white")]

scale = max(50, L_total * 1.3)
ax1.axhline(0, color='#3498db', lw=3, alpha=0.5) 
ax1.fill_between([-scale, scale], -scale*1.5, 0, color='#3498db', alpha=0.1)

theta = np.deg2rad(45)
cos_t, sin_t = np.cos(theta), np.sin(theta)
p_top = np.array([-L_out * sin_t, L_out * cos_t])

def get_pos(s): return p_top + np.array([s * sin_t, -s * cos_t])
p_bot = get_pos(L_total)

v_perp = np.array([cos_t, sin_t])
w = scale * 0.05
if shape_idx == 0: 
    ax1.add_patch(Polygon([get_pos(0)-v_perp*w, get_pos(0)+v_perp*w, get_pos(L_total)+v_perp*w, get_pos(L_total)-v_perp*w], closed=True, facecolor='#d5dbdb', edgecolor='#7f8c8d', lw=2))
elif shape_idx == 1: 
    ax1.add_patch(Polygon([get_pos(0)-v_perp*w*2, get_pos(0)+v_perp*w*2, get_pos(L_total)+v_perp*w*2, get_pos(L_total)-v_perp*w*2], closed=True, facecolor='#f3f0df', edgecolor='#7f8c8d', alpha=0.8))
elif shape_idx == 2: 
    ax1.add_patch(Polygon([get_pos(0), get_pos(L_total)+v_perp*w*3, get_pos(L_total)-v_perp*w*3], closed=True, facecolor='#fdebd0', edgecolor='#d35400'))
elif shape_idx == 3:
    ax1.add_patch(Polygon([get_pos(0), get_pos(L_total)+v_perp*w*2.5, get_pos(L_total)-v_perp*w*2.5], closed=True, facecolor='#ebedef', edgecolor='#2c3e50'))
    ax1.add_patch(Ellipse(get_pos(L_total), w*5, w*1.5, angle=np.rad2deg(-theta), color='#2c3e50', alpha=0.2))

ax1.plot([p_top[0], p_top[0]], [p_top[1], p_top[1]+scale*0.2], 'k--', lw=1.5, alpha=0.6) 

v_arrow_s = scale * 0.45

ax1.arrow(p_top[0], p_top[1], 0, T_mag*v_arrow_s, head_width=scale*0.03, fc='blue', ec='blue', lw=2.5, zorder=30)
ax1.text(p_top[0], p_top[1]+T_mag*v_arrow_s+3, 'T', color='blue', fontsize=14, fontweight='bold', path_effects=pe)

p_cg = get_pos(z_cg_val)
ax1.plot(p_cg[0], p_cg[1], marker='+', color='goldenrod', markersize=14, markeredgewidth=4, zorder=40)
ax1.arrow(p_cg[0], p_cg[1], 0, -W_fixed*v_arrow_s, head_width=scale*0.03, fc='goldenrod', ec='goldenrod', lw=3, zorder=30)
ax1.text(p_cg[0]+3, p_cg[1]-W_fixed*v_arrow_s-6, 'W (CG)', color='goldenrod', fontsize=14, fontweight='bold', path_effects=pe)

p_cb = get_pos(z_cb_val)
ax1.plot(p_cb[0], p_cb[1], 'ro', markersize=10, zorder=40, markeredgecolor='white')
ax1.arrow(p_cb[0], p_cb[1], 0, FB_mag*v_arrow_s, head_width=scale*0.03, fc='red', ec='red', lw=3, zorder=30)
ax1.text(p_cb[0]-10, p_cb[1]+FB_mag*v_arrow_s+3, 'Fb (CB)', color='red', fontsize=14, fontweight='bold', path_effects=pe)

ax1.set_xlim(-scale*0.8, scale*0.8); ax1.set_ylim(-scale*1.3, scale*1.0); ax1.axis('off')
ax1.set_title(t['ax1_title'], fontproperties=tc_font_bold, fontsize=16)

x_m = np.linspace(0, 1, 100)
y_i, y_c = 1-(x_m**P), 1-(x_m**P)-(C1*x_m + C2*x_m**2)
ax2.plot(x_m, y_i, color='#ced4da', linestyle='--', label="Theory Ideal")
ax2.plot(x_m, y_c, color='#28a745', lw=3, label="Calibrated Model")
ax2.scatter(x_ratio, d_true, color='red', s=150, zorder=10)
ax2.set_xlabel("露出比例 x", fontproperties=tc_font); ax2.set_ylabel("比重 d", fontproperties=tc_font)
ax2.set_title(t['ax2_title'], fontproperties=tc_font_bold, fontsize=16)
ax2.legend(); ax2.grid(True, alpha=0.2)

plt.tight_layout()
st.pyplot(fig) # 唯一修改：將 plt.show() 改為 st.pyplot(fig)
