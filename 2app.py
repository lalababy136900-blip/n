import streamlit as st
import pandas as pd
import shioaji as sj
import time
from datetime import datetime
from collections import deque

# ================= 1. 填寫你的永豐金 API 金鑰 =================
API_KEY = "6EvJDWTeHPLsYpsLNggmnoKjYcpe7CxYG7nCEJtZczJ3"
SECRET_KEY = "8FQx6Mhzjpq4Es3amhwsrzvKyDxeayp1rmavVJeV2uQ2"
# ==========================================================

st.set_page_config(page_title="微台指 永豐API即時監控", layout="wide")

# 初始化 Shioaji 連線 (快取連線避免每次重整都重新登入)
@st.cache_resource
def init_shioaji():
    api = sj.Shioaji(simulation=True)
    api.login(api_key=API_KEY, secret_key=SECRET_KEY)
    
    # 用於儲存即時收到的 Tick 數據
    tick_buffer = deque(maxlen=50)

    # 註冊期貨即時 Tick 回呼函式
    @api.on_tick_fop_v1
    def quote_callback(exchange, tick):
        side = "外盤(買)" if tick.tick_type == 1 else ("內盤(賣)" if tick.tick_type == 2 else "中性")
        tick_buffer.appendleft({
            "時間": tick.datetime.strftime("%H:%M:%S"),
            "價格": float(tick.close),
            "單量": int(tick.volume),
            "內外盤": side
        })

    # 訂閱微台指近月合約 (TMFR1 為微台指近月連續合約代碼)
    contract = api.Contracts.Futures.TMF.TMFR1
    api.subscribe(contract, quote_type=sj.constant.QuoteType.Tick)
    
    return api, tick_buffer

# 側邊欄設定
st.sidebar.header("⚙️ 警示設定")
big_order_threshold = st.sidebar.number_input("大單警示門檻 (口數)", min_value=1, max_value=500, value=30, step=5)
st.sidebar.info(f"💡 單筆成交達 **{big_order_threshold} 口** 以上將觸發大單標記！")

st.title("🚨 微台指 (TMF) 永豐API即時盤差與大單監控")

# 嘗試連線
try:
    api, tick_buffer = init_shioaji()
    st.sidebar.success("✅ 永豐 Shioaji API 連線成功 (微台指 TMFR1)")
except Exception as e:
    st.error(f"❌ API 連線失敗，請檢查金鑰或合約代碼：{e}")
    st.stop()

# 顯示即時明細區塊
if len(tick_buffer) == 0:
    st.warning("⏳ 已連線，正在等待微台指即時成交 Tick 推播中（非開盤時段無新成交）...")
else:
    df = pd.DataFrame(list(tick_buffer))
    latest = df.iloc[0]

    # 計算目前畫面統計的內外盤差
    buy_vol = df[df["內外盤"] == "外盤(買)"]["單量"].sum()
    sell_vol = df[df["內外盤"] == "內盤(賣)"]["單量"].sum()
    net_diff = buy_vol - sell_vol

    # 頂部指標卡
    col1, col2, col3 = st.columns(3)
    col1.metric("微台指最新成交價", f"{latest['價格']:,.0f}")
    col2.metric("近期累積盤差 (買-賣)", f"{net_diff:+d} 口")
    col3.metric("最新一筆成交", f"{latest['單量']} 口 ({latest['內外盤']})")

    st.subheader(f"⚡ 即時成交明細 (大單門檻: {big_order_threshold}口)")

    def highlight_big_order(row):
        return ['background-color: rgba(255, 75, 75, 0.2)' if row['單量'] >= big_order_threshold else '' for _ in row]

    st.dataframe(
        df.style.apply(highlight_big_order, axis=1),
        width="stretch"
    )

# 自動重新整理畫面（每秒檢查一次是否有新 Tick 進來）
time.sleep(1)
st.rerun()
