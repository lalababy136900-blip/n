import random
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="台指期 專業三竹風看盤介面",
    page_icon="📈",
    layout="centered",
)

# 強制套用深色看盤風格與緊湊排版 CSS（修復五檔對齊與寬度）
st.markdown(
    """
    <style>
    /* 整體黑底設定 */
    .stApp { background-color: #0d0d0d; color: #e0e0e0; }
    header[data-testid="stHeader"] { background-color: #0d0d0d; }
    
    /* 頂部報價看板 */
    .top-bar {
        background-color: #181818;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #2a2a2a;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .price-main { color: #ff4d4d; font-size: 32px; font-weight: bold; line-height: 1.1; }
    .price-sub { color: #ff4d4d; font-size: 14px; font-weight: bold; }
    
    /* 三小格數據卡 */
    .stat-box {
        background-color: #181818;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
    }
    .stat-label { font-size: 12px; color: #888; }
    .stat-val { font-size: 18px; font-weight: bold; margin-top: 2px; }

    /* 即時明細滾動區塊 */
    .trade-container {
        background-color: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 12px;
    }
    .trade-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 8px;
        border-bottom: 1px solid #222;
        font-size: 14px;
        font-family: monospace;
    }
    .big-red-row {
        background-color: rgba(255, 77, 77, 0.22);
        border-left: 4px solid #ff4d4d;
        font-weight: bold;
    }
    .big-green-row {
        background-color: rgba(0, 204, 102, 0.22);
        border-left: 4px solid #00cc66;
        font-weight: bold;
    }

    /* 經典三竹風黑底五檔表格（強制對稱、固定欄寬） */
    .orderbook-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #141414;
        font-family: monospace;
        font-size: 14px;
        border: 1px solid #2a2a2a;
        table-layout: fixed;
    }
    .orderbook-table th {
        background-color: #1f1f1f;
        color: #aaa;
        padding: 6px;
        border-bottom: 1px solid #333;
        text-align: center;
        width: 25%;
    }
    .orderbook-table td {
        padding: 6px 8px;
        border-bottom: 1px solid #222;
        text-align: center;
    }
    .sell-text { color: #00cc66; font-weight: bold; }
    .buy-text { color: #ff4d4d; font-weight: bold; }
    .vol-text { color: #e0e0e0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 側邊欄設定
st.sidebar.header("⚙️ 盯盤設定")
threshold = st.sidebar.slider("大單門檻 (張數)", min_value=10, max_value=100, value=30, step=5)
st.sidebar.info(f"💡 單筆張數 ≥ **{threshold} 張** 自動高亮並跳出提示")

# 初始化 1 分鐘重置狀態
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.accumulated_spread = 0
    st.session_state.minute_volume = 0
    st.session_state.trade_log = []

placeholder = st.empty()

for _ in range(300):
    current_time = time.time()
    elapsed = current_time - st.session_state.start_time

    # 每 60 秒歸零 1 分鐘累積盤差與成交量
    if elapsed >= 60:
        st.session_state.start_time = current_time
        st.session_state.accumulated_spread = 0
        st.session_state.minute_volume = 0

    # 模擬即時跳動
    is_red = random.choice([True, False])  # True=外盤買(紅), False=內盤賣(綠)
    tick_vol = random.randint(1, 45)
    base_price = 21910
    curr_price = base_price + random.randint(-4, 4)
    price_diff = curr_price - 21780

    spread_delta = tick_vol if is_red else -tick_vol
    st.session_state.accumulated_spread += spread_delta
    st.session_state.minute_volume += tick_vol

    is_big = tick_vol >= threshold
    time_str = time.strftime("%H:%M:%S", time.localtime(current_time))

    if is_big:
        side_label = "外盤買進" if is_red else "內盤賣出"
        st.toast(f"⚡ 大單 {tick_vol} 張 ({side_label}) @ {curr_price}", icon="🚨")

    st.session_state.trade_log.insert(
        0,
        {
            "時間": time_str,
            "價格": curr_price,
            "張數": tick_vol,
            "is_red": is_red,
            "is_big": is_big,
        },
    )
    if len(st.session_state.trade_log) > 8:
        st.session_state.trade_log.pop()

    acc_spread = st.session_state.accumulated_spread
    spread_color = "#ff4d4d" if acc_spread >= 0 else "#00cc66"
    seconds_left = max(0, int(60 - elapsed))

    with placeholder.container():
        # 1.
