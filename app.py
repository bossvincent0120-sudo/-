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

# --- 3. Streamlit UI 控制項 ---
lang = st.radio("🌐 Language:", ['中文', 'English'], horizontal=True)
t = UI_TEXT[lang]

col_top1, col_top2, col_top3 = st.columns(3)
with col_top1:
    shape_options = [s[0] for s in t['shapes']]
    selected_shape = st.selectbox(t['labels'][0], shape_options)
    shape_idx = shape_options.index(selected_shape)
with col_top2:
    L_total = st.number_input(t['labels'][1], value=40.0, step=1.0)
with col_top3:
    L_out = st.number_input(t['labels'][2], value=20.0, step=1.0)

col_bot1, col_bot2, col_bot3 = st.columns(3)
with col_bot1:
    C1 = st.number_input(t['labels'][3], value=0.00, step=0.01)
with col_bot2:
    C2 = st.number_input(t['labels'][4], value=0.00, step=0.01)
with col_bot3:
    P_temp = [2, 2, 3, 4][shape_idx]
    x_ratio_temp = L_out / L_total if L_total > 0 else 0
    d_ideal_input = 1 - (x_ratio_temp**P_temp)
    st.metric("理想理論值 d_ideal:", f"{d_ideal_input:.4f}")

# --- 3.5 虛擬實驗室：標定數據模擬與擬合計算工具 ---
with st.expander("🔬 虛擬實驗室：物理誤差模擬與標定演算"):
    st.markdown("本區模擬現實中探頭進入**純水 (d=1.000)** 時的狀況。系統內建「動態材質擾動引擎」，會根據您的輸入自動模擬不同材質（如壓克力、金屬）所造成的表面張力與重心變異。")
    
    num_pts = st.number_input("欲模擬的採樣點數量 (N):", min_value=2, max_value=10, value=3, step=1)
    
    # 【核心修改】材質動態擾動引擎
    # 將上方主介面的 L_total 與 L_out 作為「材質切換」的種子
    # 只要稍微調整主介面的長度，系統就會模擬您換了一支「親水性或疏水性不同」的探頭
    np.random.seed(int(L_total * 100 + L_out * 10 + shape_idx))
    material_multiplier = np.random.uniform(0.3, 2.0) 
    
    base_c1 = [0.035, 0.045, 0.082, 0.125][shape_idx] * material_multiplier
    base_c2 = [0.012, 0.018, 0.045, 0.075][shape_idx] * material_multiplier
    
    X_fit = []
    Y_fit = []
    
    for i in range(int(num_pts)):
        st.markdown(f"**第 {i+1} 組模擬數據**")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            l_i = st.number_input(f"總長度 L_{i+1}", value=40.0, step=1.0, key=f"L_{i}")
        with col_f2:
            default_lout = max(0.0, 20.0 - i * 5.0)
            lout_i = st.number_input(f"水外長 L_out_{i+1}", value=default_lout, step=1.0, key=f"Lout_{i}")
        
        x_i = lout_i / l_i if l_i > 0 else 0
        P_fit = [2, 2, 3, 4][shape_idx]
        d_ideal_sim = 1 - (x_i**P_fit)
        
        # 加入極微小的環境雜訊，模擬真實水波擾動
        noise = np.random.uniform(-0.003, 0.003)
        d_exp_sim = d_ideal_sim - (base_c1 * x_i) - (base_c2 * (x_i**2)) + noise
        
        d_std_fixed = 1.000
        
        st.caption(f"💡 露出比例 x = {x_i:.3f} | 虛擬感測器讀值 d_exp = {d_exp_sim:.4f}")
        
        X_fit.append([x_i, x_i**2])
        Y_fit.append(d_exp_sim - d_std_fixed)
    
    if st.button("執行最小平方法擬合"):
        try:
            if all(x == 0 for x, _ in X_fit):
                st.warning("⚠️ 數據點無法建立曲線，請確保 L_out 不全為 0。")
            else:
                c, _, _, _ = np.linalg.lstsq(np.array(X_fit), np.array(Y_fit), rcond=None)
                st.success(f"✅ 擬合成功！演算法成功捕捉該材質與幾何之特徵。\n請將主介面滑桿設定為： **線性誤差 C1 = {-c[0]:.4f}** , **二次誤差 C2 = {-c[1]:.4f}**")
        except Exception as e:
            st.error("計算失敗。")

# --- 4. 物理運算 (一字未動) ---
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

# --- 5. 藍色數據儀表板 (一字未動) ---
st.markdown(f"""
<div style="background-color: #f1f8ff; padding: 15px; border-radius: 8px; border-left: 10px solid #007bff; margin-bottom: 20px; font-family: sans-serif;">
    <h3 style="margin: 0 0 12px 0; color: #0056b3; font-size: 18px;">{t['report_title']}</h3>
    <div style="display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr; gap: 10px; align-items: center; font-size: 14px;">
        <span><b>待測物:</b> {t['shapes'][shape_idx][0]}</span>
        <span style="color: #0056b3;">🔵 <b>{t['vec_T']}</b> = {T_mag:.4f}</span>
        <span style="color: #d9534f;">🔴 <b>{t['vec_Fb']}</b> = {FB_mag:.4f}</span>
        <span style="color: #f0ad4e;">🟡 <b>{t['vec_W']}</b> = {W_fixed:.4f}</span>
        <span style="color: #28a745;">🟢 <b>{t['vec_d']}</b> = {d_true:.4f}</span>
        <span style="color: #6f42c1;">🟣 <b>理想值(d_ideal)</b> = {d_ideal:.4f}</span>
    </div>
    <div style="margin-top: 10px; font-size: 12px; color: #555; border-top: 1px solid #ddd; padding-top: 5px;">
        微積分幾何中心檢驗：質心 (CG) = {z_cg_val:.2f} | 浮心 (CB) = {z_cb_val:.2f}
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. 繪圖區 (一字未動) ---
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
st.pyplot(fig)
