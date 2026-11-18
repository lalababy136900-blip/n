import streamlit as st
from unitrade.unitrade import Unitrade  # 假設使用 unitrade 取得行情

# 設定頁面寬度與配置
st.set_page_config(
    page_title="台指期即時報價系統", page_icon="📈", layout="wide"
)

# --- 1. 初始化行情連線 (純報價不需憑證登入) ---


@st.cache_resource
def init_market_data():
  try:
    # 初始化 Unitrade 行情物件 (僅連線行情源)
    api = Unitrade()
    # api.connect_quote() # 視官方 API 語法連接行情
    return api
  except Exception as e:
    st.error(f"行情連線初始化失敗: {e}")
    return None


api = init_market_data()

# --- 2. 側邊欄：參數設定 ---
with st.sidebar:
  st.header("⚙️ 參數設定")
  threshold = st.slider("大單門檻 (張)", min_value=1, max_value=100, value=30)

  if api:
    st.success("🟢 行情連線正常")
  else:
    st.warning("⚠️ 尚未連線行情")

  st.info(f"💡 目前設定：單筆成交量 $\\ge$ {threshold} 張觸發警報")

st.title("📊 台指期即時報價與五檔監控")

# --- 3. 上方：即時成交明細與大單警示區塊 ---
st.subheader("⚡ 即時成交明細")

detail_container = st.container(height=220)
with detail_container:
  # 這裡未來會接收即時成交回呼 (Callback) 更新資料
  st.markdown(
      """
        <div style="font-family: monospace; font-size: 14px; line-height: 1.8;">
            <span style="color: #999;">10:32:15</span> | <span style="color: #ff4b4b; font-weight: bold;">23450</span> | <span style="color: #ff4b4b;">2 張 (外盤)</span> <span style="background-color: #ff4b4b22; color: #ff4b4b; padding: 2px 6px; border-radius: 4px; font-size: 11px;">🔥 大單 35 張</span><br>
            <span style="color: #999;">10:32:08</span> | <span style="color: #00cc66;">23448</span> | <span style="color: #00cc66;">1 張 (內盤)</span><br>
            <span style="color: #999;">10:31:55</span> | <span style="color: #00cc66;">23448</span> | <span style="color: #00cc66;">3 張 (內盤)</span><br>
            <span style="color: #999;">10:31:40</span> | <span style="color: #ff4b4b;">23449</span> | <span style="color: #ff4b4b;">1 張 (外盤)</span>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("---")

# --- 4. 五檔報價與下方總掛單區塊（左邊賣價、右邊買價） ---
st.subheader("📊 委買委賣五檔")

col_ask_box, col_bid_box = st.columns(2)

with col_ask_box:
  st.markdown(
      """
    <div style="background-color: #1e1e1e; padding: 12px; border-radius: 6px; font-family: monospace;">
        <div style="color: #ff4b4b; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #444; padding-bottom: 4px;">🔴 賣價五檔 (委賣)</div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #ff4b4b;"><span>23454</span> <span>27張</span></div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #ff4b4b;"><span>23453</span> <span>42張</span></div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #ff4b4b;"><span>23452</span> <span>27張</span></div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #ff4b4b;"><span>23451</span> <span>17張</span></div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #ff4b4b;"><span>23450</span> <span>18張</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )

with col_bid_box:
  st.markdown(
      """
    <div style="background-color: #1e1e1e; padding: 12px; border-radius: 6px; font-family: monospace;">
        <div style="color: #00cc66; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #444; padding-bottom: 4px;">🟢 買價五檔 (委買)</div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #00cc66;"><span>23448</span> <span>5張</span></div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #00cc66;"><span>23447</span> <span>53張</span></div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #00cc66;"><span>23446</span> <span>26張</span></div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #00cc66;"><span>23445</span> <span>26張</span></div>
        <div style="display: flex; justify-content: space-between; padding: 4px 0; color: #00cc66;"><span>23444</span> <span>7張</span></div>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("<br>", unsafe_allow_html=True)

# 下方總掛單統計
st.markdown("##### 📌 總掛單統計")
col_stat1, col_stat2 = st.columns(2)
with col_stat1:
  st.metric(label="總委買張數", value="2,772", delta="+120")
with col_stat2:
  st.metric(label="總委賣張數", value="331", delta="-45")
