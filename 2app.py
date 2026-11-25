import random
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="台指期 盤差與大單即時彈出警示", page_icon="🚨", layout="centered"
)

# 套用黑底紅綠 CSS 與大單高亮樣式
st.markdown(
    """
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    .metric-card { background-color: #1e1e1e; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 10px; }
    .up-price { color: #ff4d4d; font-size: 24px; font-weight: bold; }
    .down-price { color: #00cc66; font-size: 24px; font-weight: bold; }
    .big-order-up { background-color: rgba(255, 77, 77, 0.25); border-left: 4px solid #ff4d4d; padding: 6px; margin: 3px 0; }
    .big-order-down { background-color: rgba(0, 204, 102, 0.25); border-left: 4px solid #00cc66; padding: 6px; margin: 3px 0; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🚨 台指期 1分盤差與大單彈出警示監控")
st.markdown("---")

# 側邊欄設定大單門檻
st.sidebar.header("⚙️ 警示設定")
threshold = st.sidebar.slider(
    "大單警示門檻 (張數)", min_value=10, max_value=100, value=30, step=5
)
st.sidebar.info(f"💡 當前設定：單筆成交量達 **{30} 張** 以上即彈出警示！")

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

  # 每 60 秒歸零 1 分鐘累積數據
  if elapsed >= 60:
    st.session_state.start_time = current_time
    st.session_state.accumulated_spread = 0
    st.session_state.minute_volume = 0

  # 模擬每一秒的最新成交
  is_buy_side = random.choice([True, False])  # True=外盤買進, False=內盤賣出
  tick_vol = random.randint(1, 50)  # 隨機產生 1~50 口
  base_price = 23450
  curr_price = base_price + random.randint(-3, 3)

  # 累積盤差與總量
  spread_delta = tick_vol if is_buy_side else -tick_vol
  st.session_state.accumulated_spread += spread_delta
  st.session_state.minute_volume += tick_vol

  is_big = tick_vol >= threshold
  trade_type = "外盤(買)" if is_buy_side else "內盤(賣)"
  time_str = time.strftime("%H:%M:%S", time.localtime(current_time))

  # 🚨 **關鍵：如果達到大單門檻，立刻觸發彈出式通知 (Toast)**
  if is_big:
    side_desc = "🔥【外盤大舉敲進】" if is_buy_side else "💧【內盤大單砸盤】"
    st.toast(
        f"{side_desc} 剛剛成交 {tick_vol} 口！價格：{curr_price} ({trade_type})",
        icon="🚨",
    )

  # 記錄到成交明細
  st.session_state.trade_log.insert(
      0,
      {
          "時間": time_str,
          "價格": curr_price,
          "口數": tick_vol,
          "性質": trade_type,
          "is_big": is_big,
      },
  )

  if len(st.session_state.trade_log) > 15:
    st.session_state.trade_log.pop()

  acc_spread = st.session_state.accumulated_spread
  min_vol = st.session_state.minute_volume
  spread_color = "#ff4d4d" if acc_spread >= 0 else "#00cc66"
  seconds_left = max(0, int(60 - elapsed))

  with placeholder.container():
    # 上方核心數據
    col1, col2, col3 = st.columns(3)

    with col1:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div>台指期最新價</div>
                    <div class="up-price">{curr_price}</div>
                    <div style="font-size:14px; color:#ff4d4d;">+120 (+0.51%)</div>
                </div>
                """,
          unsafe_allow_html=True,
      )

    with col2:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div>🔥 1分累積盤差</div>
                    <div style="color: {spread_color}; font-size: 24px; font-weight: bold;">{acc_spread:+d} 張</div>
                    <div style="font-size:12px; color:#888;">倒數 {seconds_left} 秒重置</div>
                </div>
                """,
          unsafe_allow_html=True,
      )

    with col3:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div>1分成交量</div>
                    <div style="font-size:24px; font-weight:bold;">{min_vol:,}</div>
                    <div style="font-size:12px; color:#888;">本分K累計口數</div>
                </div>
                """,
          unsafe_allow_html=True,
      )

    # 左右並排：五檔與即時明細
    col_depth, col_trades = st.columns([1, 1])

    with col_depth:
      st.markdown("### 📊 委買委賣五檔")
      p = curr_price
      sell_df = pd.DataFrame(
          {
              "賣價": [p + 5, p + 4, p + 3, p + 2, p + 1],
              "張數": [
                  random.randint(5, 30),
                  random.randint(10, 50),
                  random.randint(20, 80),
                  random.randint(5, 30),
                  random.randint(1, 20),
              ],
          }
      )
      st.dataframe(sell_df, hide_index=True, use_container_width=True)

      buy_df = pd.DataFrame(
          {
              "買價": [p - 1, p - 2, p - 3, p - 4, p - 5],
              "張數": [
                  random.randint(5, 30),
                  random.randint(20, 80),
                  random.randint(10, 50),
                  random.randint(5, 30),
                  random.randint(1, 20),
              ],
          }
      )
      st.dataframe(buy_df, hide_index=True, use_container_width=True)

    with col_trades:
      st.markdown(f"### ⚡ 即時成交明細 (大單門檻: {threshold}張)")

      for trade in st.session_state.trade_log:
        t_time = trade["時間"]
        t_price = trade["價格"]
        t_vol = trade["口數"]
        t_type = trade["性質"]
        is_big = trade["is_big"]

        color_style = (
            "color: #ff4d4d; font-weight: bold;"
            if "外盤" in t_type
            else "color: #00cc66; font-weight: bold;"
        )
        big_tag = f" 🚨 **[大單 {t_vol}口]**" if is_big else f" ({t_vol}口)"

        if is_big:
          box_class = (
              "big-order-up" if "外盤" in t_type else "big-order-down"
          )
          st.markdown(
              f"""
                    <div class="{box_class}">
                        <span style="color:#aaa; font-size:12px;">{t_time}</span> | 
                        價格: <span style="font-weight:bold;">{t_price}</span> | 
                        <span style="{color_style}">{t_type}{big_tag}</span>
                    </div>
                    """,
              unsafe_allow_html=True,
          )
        else:
          st.markdown(
              f"""
                    <div style="padding: 2px 0; border-bottom: 1px solid #222; font-size: 14px;">
                        <span style="color:#aaa; font-size:12px;">{t_time}</span> | 
                        價格: {t_price} | 
                        <span style="{color_style}">{t_type}{big_tag}</span>
                    </div>
                    """,
              unsafe_allow_html=True,
          )

    st.caption("⏱️ 達到大單門檻時，右下角會自動彈出提示框告知內外盤狀況！")

  time.sleep(1)
  st.rerun()
