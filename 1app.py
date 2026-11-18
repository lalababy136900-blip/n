import streamlit as st

# 設定頁面寬度與配置
st.set_page_config(
    page_title="台指期即時盯盤系統", page_icon="📈", layout="wide"
)

# --- 側邊欄：設定區 ---
with st.sidebar:
  st.header("⚙️ 參數設定")
  threshold = st.slider("大單門檻 (張)", min_value=1, max_value=100, value=30)
  st.info(f"💡 目前設定：單筆成交量 $\\ge$ {threshold} 張觸發警報")

st.title("📊 台指期即時監控面板")

# --- 1. 上方：即時成交明細區塊 ---
st.subheader("⚡ 即時成交明細 (大單警示)")

# 使用固定高度的容器來模擬成交明細滾動視窗
detail_container = st.container(height=220)
with detail_container:
  # 模擬成交明細資料：時間、價格、張數、內外盤屬性
  # 註：台指期紅漲綠跌 / 紅色外盤(買)、綠色內盤(賣)
  st.markdown(
      """
        <div style="font-family: monospace; font-size: 14px; line-height: 1.6;">
            <span style="color: #999;">10:29:40</span> | <span style="color: #ff4b4b; font-weight: bold;">23449</span> | <span style="color: #ff4b4b;">1 張 (外盤)</span> <span style="background-color: #ff4b4b22; color: #ff4b4b; padding: 2px 6px; border-radius: 4px; font-size: 11px;">🔥 大單 35 張</span><br>
            <span style="color: #999;">10:29:34</span> | <span style="color: #00cc66;">23448</span> | <span style="color: #00cc66;">1 張 (內盤)</span><br>
            <span style="color: #999;">10:29:26</span> | <span style="color: #00cc66;">23448</span> | <span style="color: #00cc66;">1 張 (內盤)</span><br>
            <span style="color: #999;">10:29:18</span> | <span style="color: #ff4b4b;">23449</span> | <span style="color: #ff4b4b;">2 張 (外盤)</span><br>
            <span style="color: #999;">10:28:39</span> | <span style="color: #ff4b4b;">23449</span> | <span style="color: #ff4b4b;">1 張 (外盤)</span>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("---")

# --- 2. 中間：委買委賣五檔區塊 ---
st.subheader("📊 委買委賣五檔")

# 上方顯示總委買 / 總委賣量統計列
col_stat1, col_stat2 = st.columns(2)
with col_stat1:
  st.metric(label="總委買張數", value="2,772", delta="+120")
with col_stat2:
  st.metric(label="總委賣張數", value="331", delta="-45")

# 左右並排顯示五檔掛單（左側賣價五檔，右側買價五檔，或對應三竹風看盤習慣）
col_bid, col_ask = st.columns(2)

with col_bid:
  st.markdown("#### 🔴 賣價五檔 (委賣)")
  # 賣價通常由上到下價格遞減或遞增，依看盤習慣調整
  st.dataframe(
      {
          "賣價": [23454, 23453, 23452, 23451, 23450],
          "張數": [27, 42, 27, 17, 18],
      },
      use_container_width=True,
      hide_index=True,
  )

with col_ask:
  st.markdown("#### 🟢 買價五檔 (委買)")
  st.dataframe(
      {
          "買價": [23448, 23447, 23446, 23445, 23444],
          "張數": [5, 53, 26, 26, 7],
      },
      use_container_width=True,
      hide_index=True,
  )
