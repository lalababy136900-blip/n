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

# --- 1. 上方：即時成交明細與大單警示區塊 ---
st.subheader("⚡ 即時成交明細")

# 使用容器包覆成交明細，營造即時滾動視窗感
detail_container = st.container(height=240)
with detail_container:
  st.markdown(
      """
        <div style="font-family: monospace; font-size: 14px; line-height: 1.8;">
            <span style="color: #999;">10:32:15</span> | <span style="color: #ff4b4b; font-weight: bold;">23450</span> | <span style="color: #ff4b4b;">2 張 (外盤)</span> <span style="background-color: #ff4b4b22; color: #ff4b4b; padding: 2px 6px; border-radius: 4px; font-size: 11px;">🔥 大單 35 張</span><br>
            <span style="color: #999;">10:32:08</span> | <span style="color: #00cc66;">23448</span> | <span style="color: #00cc66;">1 張 (內盤)</span><br>
            <span style="color: #999;">10:31:55</span> | <span style="color: #00cc66;">23448</span> | <span style="color: #00cc66;">3 張 (內盤)</span><br>
            <span style="color: #999;">10:31:40</span> | <span style="color: #ff4b4b;">23449</span> | <span style="color: #ff4b4b;">1 張 (外盤)</span><br>
            <span style="color: #999;">10:31:12</span> | <span style="color: #ff4b4b;">23449</span> | <span style="color: #ff4b4b;">2 張 (外盤)</span>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("---")

# --- 2. 下方：委買委賣五檔與總量統計區塊 ---
st.subheader("📊 委買委賣五檔")

# 總量統計列
col_stat1, col_stat2 = st.columns(2)
with col_stat1:
  st.metric(label="總委買張數", value="2,772", delta="+120")
with col_stat2:
  st.metric(label="總委賣張數", value="331", delta="-45")

# 左右並排顯示五檔掛單（左側賣價五檔，右側買價五檔）
col_bid, col_ask = st.columns(2)

with col_bid:
  st.markdown("#### 🔴 賣價五檔 (委賣)")
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
