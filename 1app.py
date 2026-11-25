import random
import time
import pandas as pd
import streamlit as st

# 設定網頁寬版排版，更貼近手機App或電腦看盤畫面
st.set_page_config(
    page_title="台指期 專業三竹風看盤介面",
    page_icon="📈",
    layout="centered"
)

# 極簡黑底、紅漲綠跌、專業看盤介面 CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    .top-header {
        background-color: #1a1a1a;
        padding: 10px;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 10px;
    }
    .up-price {
        color: #ff4d4d;
        font-size: 28px;
        font-weight: bold;
    }
    .down-price {
        color: #00cc66;
        font-size: 28px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 8px;
        border-radius: 6px;
        text-align: center;
    }
    /* 大單高亮 */
    .big-red {
        background-color: rgba(255, 77, 77, 0.2);
        border-left: 4px solid #ff4d4d;
        padding: 4px;
        margin: 2px 0;
    }
    .big-green {
        background-color: rgba(0, 204, 102, 0.2);
        border-left: 4px solid #00cc66;
        padding: 4px;
        margin: 2px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 側邊欄：設定大單門檻
st.sidebar.header("⚙️ 盯盤設定")
threshold = st.sidebar.slider(
    "大單門檻 (張數)", min_value=10, max_value=100, value=30, step=5
)
st.sidebar.info(f"💡 單筆張數大於等於 **{threshold} 張** 時觸發提示與高亮")

# 初始化 Session State
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.accumulated_spread = 0
    st.session_state.minute_volume = 0
    st.session_state.trade_log = []

placeholder = st.empty()

# 模擬即時跳動迴圈
for _ in range(300):
    current_time = time.time()
    elapsed = current_time - st.session_state.start_time

    # 每 60 秒自動歸零 1 分鐘累積盤差
    if elapsed >= 60:
        st.session_state.start_time = current_time
        st.session_state.accumulated_spread = 0
        st.session_state.minute_volume = 0

    # 模擬成交數據
    is_red = random.choice([True, False])  # True=外盤買進(紅), False=內盤賣出(綠)
    tick_vol = random.randint(1, 45)
    base_price = 21910
    curr_price = base_price + random.randint(-4, 4)
    price_diff = curr_price - 21780

    # 累積盤差與總量
    spread_delta = tick_vol if is_red else -tick_vol
    st.session_state.accumulated_spread += spread_delta
    st.session_state.minute_volume += tick_vol

    is_big = tick_vol >= threshold
    time_str = time.strftime("%H:%M:%S", time.localtime(current_time))

    if is_big:
        side_name = "紅燈(買)" if is_red else "綠燈(賣)"
        st.toast(f"🚨【大單警示】成交 {tick_vol} 張 ({side_name})！", icon="⚡")

    # 記錄成交明細（已修復：補齊完整字典與 insert 呼叫）
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

    if len(st.session_state.trade_log) > 10:
        st.session_state.trade_log.pop()

    acc_spread = st.session_state.accumulated_spread
    min_vol = st.session_state.minute_volume
    spread_color = "#ff4d4d" if acc_spread >= 0 else "#00cc66"
    seconds_left = max(0, int(60 - elapsed))

    with placeholder.container():
        # 1. 頂部主行情區
        st.markdown(
            f"""
            <div class="top-header">
                <span style="font-size:14px; color:#aaa;">台指期近全</span>
                <div class="up-price">{curr_price} <span style="font-size:14px; color:#ff4d4d;">+{price_diff} (+0.60%)</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 上方三小卡：總量、盤差、倒數
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(
                '<div class="metric-card">總量<br><b>648,695</b></div>',
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f'<div class="metric-card">1分盤差<br><span style="color:{spread_color}; font-weight:bold;">{acc_spread:+d}</span></div>',
                unsafe_allow_html=True,
            )
        with col_c:
            st.markdown(
                f'<div class="metric-card">分K重置<br><b>{seconds_left} 秒</b></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # 2. 中間上半部：即時成交明細
        st.markdown("### 📋 即時成交明細")
        for trade in st.session_state.trade_log:
            t_time = trade["時間"]
            t_price = trade["價格"]
            t_vol = trade["張數"]
            t_red = trade["is_red"]
            t_big = trade["is_big"]
            c_hex = "#ff4d4d" if t_red else "#00cc66"

            if t_big:
                box_css = "big-red" if t_red else "big-green"
                st.markdown(
                    f"""
                    <div class="{box_css}">
                        <span style="color:#aaa; font-size:11px;">{t_time}</span> | 成交價: <span style="color:{c_hex}; font-weight:bold;">{t_price}</span> | 單量: <span style="color:{c_hex}; font-weight:bold; font-size:15px;">{t_vol} ⚡</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="padding: 2px 0; border-bottom: 1px solid #222; font-size: 13px;">
                        <span style="color:#aaa; font-size:11px;">{t_time}</span> | 成交價: <span style="color:{c_hex};">{t_price}</span> | 單量: <span style="color:{c_hex}; font-weight:bold;">{t_vol}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        # 3. 中間下半部：五檔與即時盤差
        st.markdown("### 📊 委買委賣五檔")
        p = curr_price
        col_sell_side, col_buy_side = st.columns(2)

        with col_sell_side:
            sell_df = pd.DataFrame(
                {
                    "賣價": [p + 4, p + 3, p + 2, p + 1, p],
                    "張數": [
                        random.randint(1, 15),
                        random.randint(2, 20),
                        random.randint(3, 25),
                        random.randint(1, 10),
                        random.randint(2, 12),
                    ],
                }
            )
            st.dataframe(sell_df, hide_index=True, use_container_width=True)

        with col_buy_side:
            buy_df = pd.DataFrame(
                {
                    "買價": [p - 1, p - 2, p - 3, p - 4, p - 5],
                    "張數": [
                        random.randint(2, 12),
                        random.randint(1, 10),
                        random.randint(3, 25),
                        random.randint(2, 20),
                        random.randint(1, 15),
                    ],
                }
            )
            st.dataframe(buy_df, hide_index=True, use_container_width=True)

        # 4. 底部數據提示
        st.caption("⏱️ 完美對齊三竹風排版：即時價位、1分鐘累積盤差、大單紅綠數字高亮！")

    time.sleep(1)
    st.rerun()
