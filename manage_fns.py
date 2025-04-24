from sqlalchemy.orm import sessionmaker
import streamlit as st
from database import engine, Base, Order, Object, Customer
import time

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

def input_customer():
    st.markdown("### 請填寫新顧客資料")
    new_c_name = st.text_input("客戶姓名")
    new_c_phone = st.text_input("客戶電話")
    new_c_address = st.text_input("客戶地址")
    new_c_email = st.text_input("客戶電子郵件")

    return new_c_name, new_c_phone, new_c_address, new_c_email

def add_order(customer_id):
    order_status = st.selectbox("訂單狀態", ["處理中", "已完成", "已取件", "取消訂單"])
    new_order = Order(customer_id=customer_id, status=order_status)

    return new_order

def add_object():
    st.markdown("### 請填寫物品資料")
    
    brand = st.text_input(f"品牌", key="obj_brand")
    type = st.text_input(f"種類", key="obj_type")
    service = st.text_input(f"服務項目", key="obj_service")
    price = st.number_input(f"價格", value=0, step=10, format="%d", key="obj_price")
    note = st.text_input(f"備註", key="obj_note")

    return {
            "brand":brand,
            "type": type,
            "service": service,
            "price": price,
            "note": note}

def clear_object_form():
    """Clear the object form."""
    st.session_state.obj_brand = ""
    st.session_state.obj_type = ""
    st.session_state.obj_service = ""
    st.session_state.obj_price = 0
    st.session_state.obj_note = ""
    return 0
    # if not type or not service:
    #     st.error("物品種類與服務項目為必填")
    # else:
    #     object = Object(
    #                 order_id=order_id,
    #                 object_brand=brand,
    #                 object_type=type,
    #                 object_service=service,
    #                 object_price=price,
    #                 note=note
    #             )
    #     return object

def delete_object(object_id):
    """Delete an object from the order."""
    object_to_delete = session.query(Object).filter_by(object_id=object_id).first()
    if object_to_delete:
        session.delete(object_to_delete)
        session.commit()
        st.success("物品已刪除")
        time.sleep(1)
    else:
        st.error("物品不存在")

def delete_order(order_id):
    """Delete an order."""
    order_to_delete = session.query(Order).filter_by(order_id=order_id).first()
    if order_to_delete:
        session.query(Object).filter(Object.order_id==order_to_delete.order_id).delete()
        session.delete(order_to_delete)
        session.commit()
        st.success(f"訂單 {order_to_delete.order_id} 已刪除")
    else:
        st.error("訂單不存在")

def delete_customer(customer_id):
    """Delete a customer."""
    customer_to_delete = session.query(Customer).filter_by(customer_id=customer_id).first()
    st.write(customer_to_delete)
    if customer_to_delete:
            
        for order in customer_to_delete.orders:
            delete_order(order.order_id)
        session.delete(customer_to_delete)
        session.commit()
        # session.commit()
    else:
        st.error("顧客不存在")
        
