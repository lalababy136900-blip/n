import time
import streamlit as st

st.set_page_config(
    page_title="台指期即時報價盯盤系統", page_icon="📈", layout="wide"
)


# --- 1. 全域即時數據暫存區 (讓背景 API 回呼與網頁畫面共用) ---
@st.cache_resource
def get_shared_data():
  return {
      "api": None,
      "connected": False,
      "status": "⚠️ 尚未連線（請於左側輸入資訊啟動）",
      "trades": [],  # 存放即時成交明細
      "asks": [
          (0, 0),
          (0, 0),
          (0, 0),
          (0, 0),
          (0, 0),
      ],  # 賣價五檔 (價格, 張數)
      "bids": [
          (0, 0),
          (0, 0),
          (0, 0),
          (0, 0),
          (0, 0),
      ],  # 買價五檔 (價格, 張數)
      "total_bid": 0,
      "total_ask": 0,
  }


shared = get_shared_data()

# --- 2. 側邊欄：Unitrade API 連線設定 ---
with st.sidebar:
  st.header("🔌 Unitrade API 連線")
  env_choice = st.selectbox("連線環境", ["正式環境", "測試環境"])
  user_id = st.text_input("統一期貨帳號", placeholder="請輸入身分證字號/帳號")
  password = st.text_input("登入密碼", type="password")
  ca_file = st.text_input(
      "憑證檔名 (需放在專案同資料夾)", placeholder="例如: my_cert.pfx"
  )
  ca_pwd = st.text_input("憑證密碼", type="password")
  symbol = st.text_input("訂閱商品代碼", value="TXFK6")

  connect_btn = st.button("🚀 啟動行情連線", use_container_width=True)

  st.markdown("---")
  st.header("⚙️ 參數設定")
  threshold = st.slider("大單門檻 (張)", min_value=1, max_value=100, value=30)
  st.info(f"💡 目前設定：單筆成交量 $\\ge$ {threshold} 張觸發警報")

# --- 3. 處理連線與訂閱 ---
if connect_btn:
  try:
    from unitrade.unitrade import Unitrade, URL_TEST, URL_PROD
    from unitrade.quote.ddata import DTickDataTrade, DTickDataBidOffer

    api = Unitrade()
    target_url = URL_TEST if env_choice == "測試環境" else URL_PROD

    api.login(
        url=target_url,
        user=user_id,
        password=password,
        ca_filename=ca_file,
        ca_password=ca_pwd,
    )

    # 接收即時成交明細
    def on_tick_data_trade(tick: DTickDataTrade):
      t_time = getattr(tick, "time", time.strftime("%H:%M:%S"))
      price = getattr(tick, "price", 0)
      qty = getattr(tick, "qty", 0)
      is_red = getattr(tick, "side", 1) == 1

      shared["trades"].insert(
          0,
          {
              "time": t_time,
              "price": price,
              "qty": qty,
              "is_red": is_red,
          },
      )
      if len(shared["trades"]) > 20:
        shared["trades"].pop()

    # 接收即時五檔報價
    def on_tick_data_bidoffer(bidoffer: DTickDataBidOffer):
      asks = []
      bids = []
      for i in range(5, 0, -1):  # 賣五到賣一
        p = getattr(bidoffer, f"ask_price{i}", 0)
        v = getattr(bidoffer, f"ask_qty{i}", 0)
        asks.append((p, v))
      for i in range(1, 6):  # 買一到買五
        p = getattr(bidoffer, f"bid_price{i}", 0)
        v = getattr(bidoffer, f"bid_qty{i}", 0)
        bids.append((p, v))
      shared["asks"] = asks
      shared["bids"] = bids
      shared["total_ask"] = sum(v for _, v in asks)
      shared["total_bid"] = sum(v for _, v in bids)

    api.dquote.on_tick_data_trade = on_tick_data_trade
    api.dquote.on_tick_data_bidoffer = on_tick_data_bidoffer
    api.dquote.subscribe_trade_bid_offer(symbol)

    shared["api"] = api
    shared["connected"] = True
    shared["status"] = f"🟢 已連線並訂閱 {symbol}"
  except ImportError:
    shared["connected"] = False
    shared["status"] = "❌ 雲端尚未安裝 unitrade，請確認 requirements.txt"
  except Exception as e:
    shared["connected"] = False
    shared["status"] = f"❌ 連線失敗: {e}"

with st.sidebar:
  if shared["connected"]:
    st.success(shared["status"])
  else:
    st.warning(shared["status"])

# --- 4. 主畫面排版 ---
st.title("📊 台指期即時報價與五檔監控")

# 上方：即時成交明細
st.subheader("⚡ 即時成交明細")
detail_container = st.container(height=220)
with detail_container:
  if not shared["trades"]:
    st.caption("等待即時成交數據傳入中...（請確認左側已啟動連線且在交易時段內）")
  else:
    html_lines = []
    for t in shared["trades"]:
      color = "#ff4b4b" if t["is_red"] else "#00cc66"
      side_txt = "外盤" if t["is_red"] else "內盤"
      big_badge = (
          f'<span style="background-color: #ff4b4b22; color: {color}; padding:'
          " 2px 6px; border-radius: 4px; font-size: 11px; margin-left:"
          f' 6px;">🔥 大單 {t["qty"]} 張</span>'
          if t["qty"] >= threshold
          else ""
      )
      html_lines.append(
          f'<span style="color: #999;">{t["time"]}</span> | '
          f'<span style="color: {color}; font-weight: bold;">{t["price"]}</span> | '
          f'<span style="color: {color};">{t["qty"]} 張 ({side_txt})</span>{big_badge}'
      )
    st.markdown(
        '<div style="font-family: monospace; font-size: 14px; line-height:'
        f' 1.8;">{"<br>".join(html_lines)}</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# 中間：委買委賣五檔（左賣右買）
st.subheader("📊 委買委賣五檔")
col_ask_box, col_bid_box = st.columns(2)

with col_ask_box:
  ask_rows = "".join([
      f'<div style="display: flex; justify-content: space-between; padding: 4px 0; color: #ff4b4b;"><span>{p}</span> <span>{v}張</span></div>'
      for p, v in shared["asks"]
  ])
  st.markdown(
      f"""
        <div style="background-color: #1e1e1e; padding: 12px; border-radius: 6px; font-family: monospace;">
            <div style="color: #ff4b4b; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #444; padding-bottom: 4px;">🔴 賣價五檔 (委賣)</div>
            {ask_rows}
        </div>
        """,
      unsafe_allow_html=True,
  )

with col_bid_box:
  bid_rows = "".join([
      f'<div style="display: flex; justify-content: space-between; padding: 4px 0; color: #00cc66;"><span>{p}</span> <span>{v}張</span></div>'
      for p, v in shared["bids"]
  ])
  st.markdown(
      f"""
        <div style="background-color: #1e1e1e; padding: 12px; border-radius: 6px; font-family: monospace;">
            <div style="color: #00cc66; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #444; padding-bottom: 4px;">🟢 買價五檔 (委買)</div>
            {bid_rows}
        </div>
        """,
      unsafe_allow_html=True,
  )

st.markdown("<br>", unsafe_allow_html=True)

# 下方：總掛單統計
st.markdown("##### 📌 總掛單統計")
col_stat1, col_stat2 = st.columns(2)
with col_stat1:
  st.metric(label="總委買張數", value=f"{shared['total_bid']:,}")
with col_stat2:
  st.metric(label="總委賣張數", value=f"{shared['total_ask']:,}")

# --- 5. 已連線時，每秒自動刷新畫面 ---
if shared["connected"]:
  time.sleep(1)
  st.rerun()
