from sqlalchemy.orm import sessionmaker
import streamlit as st
from database import engine, Base, Order, Object, Customer
from manage_fns import input_customer, add_order, add_object, delete_object, delete_order, delete_customer, clear_object_form

def new_customer_adding(name, phone):
    """Add a new customer to the database if not existing."""
    existing = session.query(Customer).filter_by(customer_name=name, customer_phone=phone).first()
    if existing:
        st.error("顧客已存在")
        return None
    else:
        new_customer = Customer(customer_name=name, customer_phone=phone)
        session.add(new_customer)
        session.commit()
        return new_customer.customer_id

def check_current_customer(customer_id):
    """Check if the current customer exists."""
    customer = session.query(Customer).filter_by(customer_id=customer_id).first()
    if customer:
        st.write(f"正在為客戶新增訂單: {customer.customer_name} ({customer.customer_phone})")
    else:
        st.error("找不到客戶")
        if st.button("返回選擇客戶"):
            st.session_state.customer_id = None
            st.session_state.current_order_id = None
            st.session_state.object_added_success = False
            st.rerun()
        st.stop()

# --- Define Callback Function ---
def save_and_clear_object_form_state():
    """
    Resets the session state variables tied to the object form input keys.
    This function runs immediately when the submit button is clicked,
    *before* the main script reruns with the button value as True.
    """
    input_keys = ["obj_brand", "obj_type", "obj_service", "obj_note", "obj_price"]
    
    temp_keys = {key: f"submitted_{key}" for key in input_keys}
    
    for key in input_keys:
        temp_key = temp_keys[key]
        if key in st.session_state:
            st.session_state[temp_key] = st.session_state[key] # Save the current value to a temporary key
        else:
            st.session_state[temp_key] = "" if key != "obj_price" else 0
            st.session_state[key] = "" # Reset text inputs to empty string
    keys_to_reset_text = input_keys.copy()
    for key in keys_to_reset_text:
        if key in st.session_state:
            st.session_state[key] = ""
    if "obj_price" in st.session_state:
        st.session_state["obj_price"] = 0
  
# --- Session Setup --- #

Session = sessionmaker(bind=engine)
session = Session()

# --- Initialization --- #

keys_defaults = {
    # Original keys
    "obj_brand": "",
    "obj_type": "",
    "obj_service": "",
    "obj_note": "",
    "obj_price": 0,
    # Temporary keys
    "submitted_obj_brand": "",
    "submitted_obj_type": "",
    "submitted_obj_service": "",
    "submitted_obj_note": "",
    "submitted_obj_price": 0,
}
for key, default_value in keys_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

if "current_order_id" not in st.session_state:
    st.session_state.current_order_id = None

if "object_added_success" not in st.session_state:
    st.session_state.object_added_success = False

# --- Stage 1: Select Customer / Creation --- #
if st.session_state.customer_id is None:
    st.header("選擇或新增客戶")

    # --- Customer Selection --- #
    customers = session.query(Customer).all()
    customer_options = [f"{c.customer_name} ({c.customer_phone})" for c in customers]
    customer_map = {f"{c.customer_name} ({c.customer_phone})": c.customer_id for c in customers}
    selected_option = st.selectbox("選擇已有客戶，或建立新客戶", ["新增客戶"] + customer_options)
    is_new_customer = selected_option == "新增客戶"

    # --- Customer Form --- #
    with st.form("customer_form"):
        selected_c_id = None # deal with customer_id in the form

        if is_new_customer:
            # Get new customer details
            new_c_name, new_c_phone, new_c_address, new_c_email = input_customer()
        else:
            # Get selected customer ID
            selected_c_id = customer_map[selected_option]
            if selected_c_id:
                st.write(f"選擇的客戶: {selected_option}")
            else:
                st.info("請選擇客戶")
        
        ### Submit Button ###
        submit_customer = st.form_submit_button("確認客戶並新增訂單")

        if submit_customer:
            customer_validated = False
            final_customer_id = None

            if is_new_customer:
                ### New Customer Validation ###
                if not new_c_name or not new_c_phone:
                    st.error("顧客姓名與電話為必填")
                else:
                    try:
                        final_customer_id = new_customer_adding(new_c_name, new_c_phone)
                        st.success(f"新增顧客成功: {new_c_name} ({new_c_phone})")
                        customer_validated = True
                    except Exception as e:
                        session.rollback()
                        st.error(f"新增顧客失敗: {e}")
            else:
                ### Existing Customer Validation ###
                final_customer_id = selected_c_id
                if final_customer_id:
                    customer_validated = True
                else:
                    st.error("顧客不存在，請重新選擇")

            ### Set State and Rerun on Success ###
            if customer_validated and final_customer_id:
                st.session_state.customer_id = final_customer_id
                st.session_state.current_order_id = None # Reset current order ID
                st.rerun() # go into the next elif

# --- Stage 2: Add Object to Order --- #
elif st.session_state.customer_id is not None:
    st.header("新增訂單")

    ### Display Current Customer ###
    check_current_customer(st.session_state.customer_id)

    ### Display Successfully Added Orders ###
    if st.session_state.object_added_success:
        st.success("物品新增成功")
        st.session_state.object_added_success = False
    
    # Oder Status
    order_status_default = "處理中"
    check_empty_order = 0

    ### Object Form ###
    with st.form("object_form"):
        add_object()
        
        submit_object = st.form_submit_button("新增物品到訂單", 
                                              on_click=save_and_clear_object_form_state)
        
        if submit_object:
            ### Create New Order ###
            order_to_use =  None
            
            if st.session_state.current_order_id:
                order_to_use = session.query(Order).get(st.session_state.current_order_id)
            
            if not order_to_use:
                try:
                    new_order = Order(customer_id=st.session_state.customer_id, status="處理中")
                    session.add(new_order)
                    session.commit()
                    st.session_state.current_order_id = new_order.order_id
                    order_to_use = new_order
                except Exception as e:
                    session.rollback()
                    st.error(f"新增訂單失敗: {e}")
                    st.stop()

            ### Save Temporary Object Form State ###
            submitted_brand = st.session_state.get("submitted_obj_brand", "")
            submitted_type = st.session_state.get("submitted_obj_type", "")
            submitted_service = st.session_state.get("submitted_obj_service", "")
            submitted_price = st.session_state.get("submitted_obj_price", 0)
            submitted_note = st.session_state.get("submitted_obj_note", "")

            
            ### Object Validation  and Creation ###
            if not submitted_type or not submitted_service:
                st.error("物品種類與服務項目為必填")
            elif order_to_use: # the order is successfully created
                try:
                    print("Creating new object...")
                    db_object_to_add = Object(
                        order_id=order_to_use.order_id,
                        object_brand=submitted_brand,
                        object_type=submitted_type,
                        object_service=submitted_service,
                        object_price=submitted_price,
                        note=submitted_note
                    )
                    session.add(db_object_to_add)
                    session.commit()
                    st.session_state.object_added_success = True
                    
                    ### Clear Temporary Object Form State ###
                    temp_keys_to_clear = [  "submitted_obj_brand",
                                            "submitted_obj_type",
                                            "submitted_obj_service",
                                            "submitted_obj_note"]
                    for temp_key in temp_keys_to_clear:
                        if temp_key in st.session_state:
                            del st.session_state[temp_key]

                except Exception as e:
                    session.rollback()
                    st.error(f"新增物品失敗: {e}")
                    st.stop()

    if st.session_state.current_order_id:
        st.divider()
        st.subheader("目前訂單中的物品：")
        try:
            added_objects = session.query(Object).filter(Object.order_id == st.session_state.current_order_id).order_by(Object.object_id).all()
            if added_objects:
                # 使用 st.dataframe 或自訂格式顯示
                object_data = []
                for i, obj in enumerate(added_objects):
                     object_data.append({
                        "項次": i + 1,
                        "品牌": obj.object_brand,
                        "種類": obj.object_type,
                        "服務": obj.object_service,
                        "價格": obj.object_price,
                        "備註": obj.note,
                        #"ID": obj.object_id # 內部使用，不一定顯示
                    })
                st.dataframe(object_data, use_container_width=True)
                # 你可以在這裡為每一行添加刪除按鈕，呼叫 delete_object(obj.object_id)

                check_empty_order = 1 # There is object in the order
            else:
                st.info("目前訂單中沒有物品")
        except Exception as e:
            st.error(f"查詢訂單物品時出錯: {e}")
    
    # --- Finish Order / Add Another Order --- #
    st.divider()
    if st.button("完成訂單/新增下一筆訂單") and check_empty_order == 1:
        st.session_state.current_order_id = None
        st.session_state.customer_id = None
        st.session_state.object_added_success = False
        st.success("訂單已完成")
        import time
        time.sleep(1)
        st.rerun()
    else:
        st.info("請先新增物品到訂單")
        st.stop()