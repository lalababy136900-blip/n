import time
import streamlit as st

# 設定頁面寬度與配置
st.set_page_config(
    page_title="台指期即時報價盯盤系統", page_icon="📈", layout="wide"
)

# --- 1. 側邊欄：Unitrade API 連線設定與參數 ---
with st.sidebar:
  st.header("🔌 Unitrade API 連線")

  # 選擇環境 (測試環境 URL_TEST 或 正式環境 URL_PROD)
  env_choice = st.selectbox("連線環境", ["測試環境", "正式環境"])
  user_id = st.text_input("統一期貨帳號", placeholder="請輸入身分證字號/帳號")
  password = st.text_input("登入密碼", type="password")
  ca_file = st.text_input(
      "憑證檔名 (需放在同資料夾)", placeholder="例如: my_cert.pfx"
  )
  ca_pwd = st.text_input("憑證密碼", type="password")
  symbol = st.text_input("訂閱商品代碼", value="TXFL6")

  connect_btn = st.button("🚀 啟動行情連線", use_container_width=True)

  st.markdown("---")
  st.header("⚙️ 參數設定")
  threshold = st.slider("大單門檻 (張)", min_value=1, max_value=100, value=30)
  st.info(f"💡 目前設定：單筆成交量 $\\ge$ {threshold} 張觸發警報")

# --- 2. 處理 Unitrade 連線與行情訂閱 ---
if "api_status" not in st.session_state:
  st.session_state.api_status = "⚠️ 尚未連線（請於左側輸入資訊啟動）"
  st.session_state.api_connected = False

if connect_btn:
  try:
    import unitrade
    from unitrade.unitrade import Unitrade, URL_TEST, URL_PROD
    from unitrade.quote.ddata import DTickDataTrade

    api = Unitrade()
    target_url = URL_TEST if env_choice == "測試環境" else URL_PROD

    # 執行登入連線
    api.login(
        url=target_url,
        user=user_id,
        password=password,
        ca_filename=ca_file,
        ca_password=ca_pwd,
    )

    # 定義即時成交回呼
    def on_tick_data_trade(tick: DTickDataTrade):
      # 收到即時成交資料時可更新至此
      print(tick)

    api.dquote.on_tick_data_trade = on_tick_data_trade
    api.dquote.subscribe_trade_bid_offer(symbol)

    st.session_state.api_status = f"🟢 已連線並訂閱 {symbol}"
    st.session_state.api_connected = True
  except ImportError:
    st.session_state.api_status = (
        "❌ 雲端尚未安裝 unitrade，請確認 requirements.txt"
    )
  except Exception as e:
    st.session_state.api_status = f"❌ 連線失敗: {e}"

# 顯示目前 API 狀態
with st.sidebar:
  if st.session_state.api_connected:
    st.success(st.session_state.api_status)
  else:
    st.warning(st.session_state.api_status)

# --- 3. 主畫面排版（上方明細、中間五檔左賣右買、下方總掛單） ---
st.title("📊 台指期即時報價與五檔監控")

# 上方：即時成交明細
st.subheader("⚡ 即時成交明細")
detail_container = st.container(height=220)
with detail_container:
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

# 中間：委買委賣五檔（左賣右買）
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

# 下方：總掛單統計
st.markdown("##### 📌 總掛單統計")
col_stat1, col_stat2 = st.columns(2)
with col_stat1:
  st.metric(label="總委買張數", value="2,772", delta="+120")
with col_stat2:
  st.metric(label="總委賣張數", value="331", delta="-45")
