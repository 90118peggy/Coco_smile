from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import datetime

# Build the database URL
engine = create_engine('sqlite:///mydatabase.db', echo=True)
Base = declarative_base()

# Define the Customer class
class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_email = Column(String)
    customer_address = Column(String)

    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer(customer_name='{self.customer_name}', customer_phone='{self.customer_phone}', customer_email='{self.customer_email}', customer_address='{self.customer_address}')>"
    
    @property
    def totol_orders(self):
        return len(self.orders)
    
    @property
    def total_spent(self):
        return sum(order.total_price for order in self.orders)
    
# Define the Order class
class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    order_date = Column(Date, default=datetime.datetime.utcnow)
    payment_method = Column(String, default='現金')
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    status = Column(String, default='處理中')


    

    customer = relationship("Customer", back_populates="orders")
    objects = relationship("Object", back_populates="orders")

    @property
    def total_price(self):
        return sum(object.object_price for object in self.objects)

    def __repr__(self):
        return f"<Order(order_date='{self.order_date}', total_price='{self.total_price}')>"
    
class Object(Base):
    __tablename__ = 'objects'

    object_id = Column(Integer, primary_key=True)
    object_type = Column(String, default='鞋')
    object_brand = Column(String, default='無')
    object_service = Column(String, nullable=False)
    object_price = Column(Integer, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    note = Column(String)

    orders = relationship("Order", back_populates="objects")

    def __repr__(self):
        return f"<Object(object_type='{self.object_type}', object_price='{self.object_price}')>"
    

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ 資料庫已建立")