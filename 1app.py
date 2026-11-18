import random
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="台指期 專業三竹風看盤介面",
    page_icon="📈",
    layout="centered",
)

# 強制套用深色看盤風格與緊湊排版 CSS
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

    /* 經典三竹風黑底五檔表格 */
    .orderbook-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #141414;
        font-family: monospace;
        font-size: 14px;
        border: 1px solid #2a2a2a;
    }
    .orderbook-table th {
        background-color: #1f1f1f;
        color: #aaa;
        padding: 6px;
        border-bottom: 1px solid #333;
        text-align: center;
    }
    .orderbook-table td {
        padding: 6px 10px;
        border-bottom: 1px solid #222;
        text-align: right;
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

# 初始化狀態
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.accumulated_spread = 0
    st.session_state.minute_volume = 0
    st.session_state.trade_log = []

placeholder = st.empty()

for _ in range(300):
    current_time = time.time()
    elapsed = current_time - st.session_state.start_time

    # 每 60 秒歸零 1 分鐘累積盤差
    if elapsed >= 60:
        st.session_state.start_time = current_time
        st.session_state.accumulated_spread = 0
        st.session_state.minute_volume = 0

    # 模擬即時跳動（之後串接統一期貨 API 時替換此區塊）
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
        # 1. 頂部即時報價列
        st.markdown(
            f"""
            <div class="top-bar">
                <div>
                    <div style="font-size:13px; color:#aaa;">台指期近全 (TX)</div>
                    <div class="price-main">{curr_price}</div>
                </div>
                <div style="text-align:right;">
                    <div class="price-sub">▲ +{price_diff} (+0.60%)</div>
                    <div style="font-size:12px; color:#888; margin-top:4px;">總量 648,695</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. 核心數據三小卡（1分盤差、1分成交量、歸零倒數）
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="stat-box"><div class="stat-label">🔥 1分累積盤差</div><div class="stat-val" style="color:{spread_color};">{acc_spread:+d}</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="stat-box"><div class="stat-label">1分累積量</div><div class="stat-val">{st.session_state.minute_volume:,}</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="stat-box"><div class="stat-label">分K重置倒數</div><div class="stat-val">{seconds_left} 秒</div></div>',
                unsafe_allow_html=True,
            )

        # 3. 逐筆成交明細（黑底緊湊列表＋大單紅綠高亮）
        st.markdown("##### 📋 即時成交明細")
        trades_html = '<div class="trade-container">'
        for t in st.session_state.trade_log:
            c_hex = "#ff4d4d" if t["is_red"] else "#00cc66"
            row_cls = ""
            bolt = ""
            if t["is_big"]:
                row_cls = "big-red-row" if t["is_red"] else "big-green-row"
                bolt = " ⚡"
            trades_html += f"""
            <div class="trade-row {row_cls}">
                <span style="color:#888;">{t["時間"]}</span>
                <span style="color:{c_hex}; font-weight:bold;">{t["價格"]}</span>
                <span style="color:{c_hex}; font-weight:bold;">{t["張數"]}{bolt}</span>
            </div>
            """
        trades_html += "</div>"
        st.markdown(trades_html, unsafe_allow_html=True)

        # 4. 經典三竹風黑底委買委賣五檔（左右對稱緊密合併）
        st.markdown("##### 📊 委買委賣五檔")
        p = curr_price
        rows_html = ""
        for i in range(5):
            # 賣價由高到低 (p+5 到 p+1)，買價由高到低 (p 到 p-4)
            sell_p = p + (5 - i)
            sell_v = random.randint(2, 35)
            buy_p = p - i
            buy_v = random.randint(2, 35)
            rows_html += f"""
            <tr>
                <td class="vol-text">{buy_v}</td>
                <td class="buy-text">{buy_p}</td>
                <td class="sell-text" style="border-left: 1px solid #333;">{sell_p}</td>
                <td class="vol-text">{sell_v}</td>
            </tr>
            """

        orderbook_html = f"""
        <table class="orderbook-table">
            <thead>
                <tr>
                    <th>買量</th>
                    <th>買進</th>
                    <th style="border-left: 1px solid #333;">賣出</th>
                    <th>賣量</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """
        st.markdown(orderbook_html, unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()
