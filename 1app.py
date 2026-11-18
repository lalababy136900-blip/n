import streamlit as st

# 網頁版面設定
st.set_page_config(
    page_title="台指期即時報價盯盤系統", page_icon="📈", layout="wide"
)

# --- 1. 嘗試載入 Unitrade 行情模組 ---
@st.cache_resource
def init_quote_client():
  try:
    import unitrade
    from unitrade.unitrade import Unitrade
    
    # 僅初始化行情連線，完全不呼叫 api.login() 進行憑證登入
    api = Unitrade()
    return api, "🟢 Unitrade 模組載入成功"
  except ImportError:
    return None, "⚠️ 找不到 unitrade 套件，請確認是否有安裝。"
  except Exception as e:
    return None, f"⚠️ 初始化異常: {e}"

api, status_msg = init_quote_client()

# --- 2. 側邊欄：參數與狀態 ---
with st.sidebar:
  st.header("⚙️ 參數設定")
  threshold = st.slider("大單門檻 (張)", min_value=1, max_value=100, value=30)
  
  if api:
    st.success(status_msg)
  else:
    st.error(status_msg)

  st.info(f"💡 目前設定：單筆成交量 $\\ge$ {threshold} 張觸發警報")

st.title("📊 台指期即時報價與五檔監控")

# --- 3. 上方：即時成交明細 ---
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

# --- 4. 五檔報價（左賣右買） ---
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
