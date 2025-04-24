import streamlit as st
from sqlalchemy.orm import sessionmaker
from database import engine, Base, Customer, Order, Object
from manage_fns import delete_customer, delete_order, delete_object

Session = sessionmaker(bind=engine)
session = Session()

st.header("顧客與訂單資料")



customers = session.query(Customer).all()
for customer in customers:
    st.subheader(f"{customer.customer_name}")
    st.write(f"電話: {customer.customer_phone}")
    st.write(f"地址: {customer.customer_address}")
    st.write(f"電子郵件: {customer.customer_email}")
    st.write(f"訂單數量: {customer.totol_orders}")
    st.write(f"目前消費總金額: {customer.total_spent}")
    if st.button("刪除顧客", key=f"delete_customer_{customer.customer_id}"):
        delete_customer(customer.customer_id)
        st.warning("顧客已刪除")
        st.rerun()
    with st.expander(f"#### 顯示客戶訂單"):
        orders = session.query(Order).filter(Order.customer_id == customer.customer_id).all()
        if not orders:
            st.info("此客戶無訂單")
        else:
            for order in orders:
                st.markdown("---")
                st.markdown(f"訂單編號 #{order.order_id} ｜ 日期：{order.order_date}｜訂單總金額：{order.total_price} ｜ 狀態：{order.status}")
                objects = session.query(Object).filter(Object.order_id == order.order_id).all()
                if objects:
                    st.markdown("#### 物品資料")
                for obj in objects:
                    st.markdown(f"@ 物品編號: {obj.object_id} ｜ 品牌: {obj.object_brand} ｜ 種類: {obj.object_type} ｜ 服務項目: {obj.object_service} ｜ 價格: {obj.object_price} 元")
                    st.markdown(f"@ 備註: {obj.note}")
                    if len(objects) > 1:
                        if st.button("刪除物品", key=f"delete_object_{obj.object_id}"):
                            delete_object(obj.object_id)
                            st.warning("物品已刪除")
                            st.rerun()
                
                ### Editing order status ###
                order_status = st.selectbox("訂單狀態", ["處理中", "已完成", "已取件", "取消訂單"], index=["處理中", "已完成", "已取件", "取消訂單"].index(order.status), key=f"order_status_{order.order_id}")
                if st.button("更新狀態", key=f"update_status_{order.order_id}"):
                    order.status = order_status
                    session.commit()
                    st.success("訂單狀態已更新")
                    st.rerun()
                

