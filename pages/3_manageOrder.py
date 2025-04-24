import streamlit as st
from sqlalchemy.orm import sessionmaker
from database import engine, Base, Order, Object, Customer
from manage_fns import input_customer, add_order, add_object, delete_object, delete_order, delete_customer

# --- Initialize session --- #
Session = sessionmaker(bind=engine)
session = Session()

def clear_search_form():
    """Clear the search form."""
    st.session_state.keyword = ""
    st.session_state.search_trigger = False


if "keyword" not in st.session_state:
    st.session_state.keyword = ""
if "search_trigger" not in st.session_state:
    st.session_state.search_trigger = False
if "comfirming_delete_customer_id" not in st.session_state:
    st.session_state.comfirming_delete_customer_id = None


# --- Search for existing orders --- #

st.header("搜尋訂單")


keyword = st.text_input("請輸入客戶電話查詢", value="")

if st.button("搜尋"):
    st.session_state.keyword = keyword
    st.session_state.search_trigger = True

if st.session_state.search_trigger:
    customers = session.query(Customer).filter(
        (Customer.customer_phone.contains(st.session_state.keyword))
    ).all()

    if not customers:
        st.error("查無此客戶")

    for customer in customers:
        st.markdown(f"#### 客戶: {customer.customer_name} ({customer.customer_phone})")
        customer_id = customer.customer_id

        # --- Step 2: Confirm delete customer --- #
        if st.session_state.comfirming_delete_customer_id == customer_id:
            st.warning(f"⚠️ 確定要刪除客戶 {customer.customer_name} ({customer.customer_phone}) 及其所有訂單嗎？此操作無法復原！")

            col_confirm, col_cancel = st.columns([1, 1])
            with col_confirm:
                if st.button("確定", key=f"confirming_delete_customer_{customer.customer_id}", type="primary"):
                    try:
                        delete_customer(customer.customer_id)
                        st.session_state.comfirming_delete_customer_id = None
                        st.success("客戶已刪除")
                        import time
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")
                        st.session_state.comfirming_delete_customer_id = None
            with col_cancel:
                if st.button("取消", key=f"cancel_delete_customer_{customer.customer_id}"):
                    st.session_state.comfirming_delete_customer_id = None
                    st.rerun()

        # --- Step 1: show botton --- #
        elif st.session_state.comfirming_delete_customer_id is None:
            if st.button("刪除客戶", key=f"delete_customer_{customer.customer_id}"):
                st.session_state.comfirming_delete_customer_id = customer.customer_id
                st.rerun()

        # --- Show Orders --- #
        if st.session_state.comfirming_delete_customer_id != customer_id:

            orders = session.query(Order).filter(Order.customer_id == customer.customer_id).all()
            if not orders:
                st.info("此客戶無訂單")
            else:
                for order in orders:
                    with st.expander(f"📦 訂單編號 #{order.order_id} ｜ 日期：{order.order_date} ｜總金額：{order.total_price} ｜  狀態：{order.status}"):
                        if st.button("刪除訂單", key=f"delete_order_{order.order_id}"):
                            delete_order(order.order_id)
                            st.warning("訂單已刪除")
                            st.rerun()
                    
                        objects = session.query(Object).filter(Object.order_id == order.order_id).all()

                        st.markdown(f"訂單總金額 {order.total_price} 元")
                        if objects:
                            st.markdown("### 物品資料")
                        for obj in objects:
                            st.markdown(f"物品編號: {obj.object_id} ｜ 品牌: {obj.object_brand} ｜ 種類: {obj.object_type} ｜ 服務項目: {obj.object_service} ｜ 價格: {obj.object_price} 元")
                            st.markdown(f"備註: {obj.note}")
                            if len(objects) > 1:
                                if st.button("刪除物品", key=f"delete_object_{obj.object_id}"):
                                    delete_object(obj.object_id)
                                    st.warning("物品已刪除")
                                    st.rerun()
                            st.markdown("---")

                        ### Editing order status ###
                        order_status = st.selectbox("訂單狀態", ["處理中", "已完成", "已取件", "取消訂單"], index=["處理中", "已完成", "已取件", "取消訂單"].index(order.status), key=f"order_status_{order.order_id}")
                        if st.button("更新狀態", key=f"update_status_{order.order_id}"):
                            order.status = order_status
                            session.commit()
                            st.success("訂單狀態已更新")
                            st.rerun()

# if st.button("顯示所有顧客資料"):
#     customers = session.query(Customer).all()
#     for customer in customers:
#         st.subheader(f"{customer.customer_name}")
#         st.write(f"電話: {customer.customer_phone}")
#         st.write(f"地址: {customer.customer_address}")
#         st.write(f"電子郵件: {customer.customer_email}")
#         st.write(f"訂單數量: {customer.totol_orders}")
#         st.write(f"目前消費總金額: {customer.total_spent}")
#         st.write("---")
#         if st.button("刪除顧客", key=f"delete_customer_{customer.customer_id}"):
#             delete_customer(customer.customer_id)
#             st.warning("顧客已刪除")
#             st.rerun()
#         if st.button("顯示客戶訂單"):
#             orders = session.query(Order).filter(Order.customer_id == customer.customer_id).all()
#             if st.button("刪除訂單", key=f"delete_order_{order.order_id}"):
#                         delete_order(order.order_id)
#                         st.warning("訂單已刪除")
#                         st.rerun()

#             if not orders:
#                 st.info("此客戶無訂單")
#             else:
#                 for order in orders:
#                     st.markdown(f"訂單編號 #{order.order_id} ｜ 日期：{order.order_date} ｜ 狀態：{order.status}")
#                     objects = session.query(Object).filter(Object.order_id == order.order_id).all()
#                     if objects:
#                         st.markdown("物品資料")
#                     for obj in objects:
#                         st.markdown(f"物品編號: {obj.object_id} ｜ 品牌: {obj.object_brand} ｜ 種類: {obj.object_type} ｜ 服務項目: {obj.object_service} ｜ 價格: {obj.object_price} 元")
#                         st.markdown(f"備註: {obj.note}")
#                         if len(objects) > 1:
#                             if st.button("刪除物品", key=f"delete_object_{obj.object_id}"):
#                                 delete_object(obj.object_id)
#                                 st.warning("物品已刪除")
#                                 st.rerun()
#                         st.markdown("---")
#                     ### Editing order status ###
#                     order_status = st.selectbox("訂單狀態", ["處理中", "已完成", "已取件", "取消訂單"], index=["處理中", "已完成", "已取件", "取消訂單"].index(order.status), key=f"order_status_{order.order_id}")
#                     if st.button("更新狀態", key=f"update_status_{order.order_id}"):
#                         order.status = order_status
#                         session.commit()
#                         st.success("訂單狀態已更新")
#                         st.rerun()
                    