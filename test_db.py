from shop import app, db
from shop.models import Brand, Category, Addproduct, Register, Rate, CustomerOrder
import pymysql

def test_db_connection1():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='myshop',
            charset='utf8mb4',
            port=3306
        )
        print("kết nối thành công!")
        connection.close()
    except Exception as e:
        print(f"Kết nối thất bại: {str(e)}")

def test_db_connection():
    with app.app_context():
        try:
            # Test each model
            brands = Brand.query.all()
            categories = Category.query.all()
            products = Addproduct.query.all()
            orders = CustomerOrder.query.all()
            
            print("\nDatabase Connection Test Results:")
            print("---------------------------------")
            print(f"Connected successfully to database 'myshop'")
            print(f"Found {len(brands)} brands")
            print(f"Found {len(categories)} categories")
            print(f"Found {len(products)} products")
            print(f"Found {len(orders)} orders")
            
            # Show sample data
            if brands:
                print("\nSample Brands:")
                for brand in brands[:3]:
                    print(f"- {brand.name}")
            
            if categories:
                print("\nSample Categories:")
                for category in categories[:3]:
                    print(f"- {category.name}")
                    
            return True
            
        except Exception as e:
            print(f"\nError connecting to database:")
            print(f"Error message: {str(e)}")
            return False

if __name__ == "__main__":
    test_db_connection1()
    test_db_connection()