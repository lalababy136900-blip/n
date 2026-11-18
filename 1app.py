import streamlit as st

# 設定頁面寬度
st.set_page_config(
    page_title="台指期 盤差與大單紅綠監控", page_icon="📈", layout="wide"
)

# --- 側邊欄：警示設定 ---
with st.sidebar:
  st.header("⚙️ 警示設定")
  threshold = st.slider("大單門檻 (張數)", min_value=1, max_value=100, value=30)
  st.info(f"💡 單筆大單門檻：{threshold} 張")

st.title("📊 台指期即時監控面板")

# --- 主畫面上下排版 ---
# 將畫面分為上下兩大區塊：上方放成交明細，下方/中間放委買委賣五檔

# 【上方】成交明細與大單警示區塊
st.subheader("⚡ 即時成交明細 (大單警示)")
# 這裡放置你的成交明細表格或容器
# 範例容器：
detail_container = st.container(height=300)
with detail_container:
  st.markdown(
      '<div style="color: #ff4b4b;">🔴 [大單警示] 成交 50 張 (紅燈(買))！價格：23449</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div style="color: #00cc66;">🟢 02:23:41 | 價格: 23450 | 張數: 32</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div style="color: #ff4b4b;">🔴 02:23:40 | 價格: 23452 | 張數: 40</div>',
      unsafe_allow_html=True,
  )

st.markdown("---")

# 【中間】委買委賣五檔區塊
st.subheader("📊 委買委賣五檔")
col1, col2 = st.columns(2)

with col1:
  st.markdown("#### 賣價五檔")
  # 這裡放入你的賣價與張數表格
  st.dataframe(
      {
          "賣價": [23454, 23453, 23452, 23451, 23450],
          "張數": [27, 42, 27, 17, 18],
      },
      use_container_width=True,
  )

with col2:
  st.markdown("#### 買價五檔")
  # 這裡放入你的買價與張數表格
  st.dataframe(
      {
          "買價": [23448, 23447, 23446, 23445, 23444],
          "張數": [5, 53, 26, 26, 7],
      },
      use_container_width=True,
  )
