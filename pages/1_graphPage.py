# 4_report.py
import datetime
import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker
from database import engine, Customer, Order, Object   # ← 直接沿用你的 models

# ---------- 初始化 ---------- #
Session = sessionmaker(bind=engine)
session = Session()

today = datetime.date.today()
current_year = today.year

# ---------- 取出本年度訂單 ---------- #
orders_this_year = (
    session.query(Order)
    .filter(Order.order_date.between(datetime.date(current_year, 1, 1),
                                     datetime.date(current_year, 12, 31)))
    .all()
)

# 將訂單展平成 DataFrame（方便群組統計）
records = []
for order in orders_this_year:
    month = order.order_date.month
    # 每張訂單的收入 = 該訂單的所有物件價格和
    order_revenue = sum(obj.object_price for obj in order.objects)
    records.append(
        {
            "month": month,
            "order_id": order.order_id,
            "revenue": order_revenue,
            "object_count": len(order.objects),
        }
    )

df = pd.DataFrame(records)

# 如果今年還沒有紀錄，給空白資料避免報錯
if df.empty:
    df = pd.DataFrame(
        {
            "month": range(1, 13),
            "revenue": [0] * 12,
            "order_id": [None] * 12,
            "object_count": [0] * 12,
        }
    )

# ---------- 聚合：月收入、月訂單數、月物件量 ---------- #
month_stats = (
    df.groupby("month")
    .agg(
        monthly_revenue=("revenue", "sum"),
        monthly_orders=("order_id", "count"),
        monthly_objects=("object_count", "sum"),
    )
    .sort_index()
)

# 補齊 1–12 月（若某月沒資料）
for m in range(1, 13):
    if m not in month_stats.index:
        month_stats.loc[m] = [0, 0, 0]

month_stats = month_stats.sort_index()

# ---------- Streamlit UI ---------- #
st.title("📊 年度營運儀表板")

total_revenue = month_stats["monthly_revenue"].sum()
st.markdown(
    f"### 💰 {current_year} 年總收入： **{total_revenue:,.0f} 元**"
)

# 1 & 2. 同圖：收入 + 訂單數 -------------------------------------------- #
st.markdown("##### 每月收入")
# set x and y axis labels
st.markdown(
    """
    <style>
        .stLineChart .stText {
            font-size: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
        .stLineChart .stText {
            font-size: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.line_chart(
    month_stats["monthly_revenue"],
    height=350,
    use_container_width=True,
)



st.markdown("#### 每月訂單數")
st.bar_chart(
    month_stats["monthly_orders"],
    height=350,
    use_container_width=True,
)

# 3. 物件量 ------------------------------------------------------------- #
st.markdown("#### 每月物件量")
st.line_chart(
    month_stats["monthly_objects"],
    height=350,
    use_container_width=True,
)

# 4. 年度總收入 --------------------------------------------------------- #

# ---------- 結束 ---------- #
