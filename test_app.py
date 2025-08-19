from shop import app, db
from shop.models import Brand, Category, Addproduct, Register, Rate, CustomerOrder, Admin

def test_models():
    with app.app_context():
        try:
            # Test all models and relationships
            brands = Brand.query.all()
            categories = Category.query.all() 
            products = Addproduct.query.all()
            users = Register.query.all()
            orders = CustomerOrder.query.all()
            ratings = Rate.query.all()
            admins = Admin.query.all()

            print("\n=== Models Test Results ===")
            print(f"Brands: {len(brands)}")
            print(f"Categories: {len(categories)}")
            print(f"Products: {len(products)}")
            print(f"Users: {len(users)}")
            print(f"Orders: {len(orders)}")
            print(f"Ratings: {len(ratings)}")
            print(f"Admins: {len(admins)}")

            # Test relationships
            if products:
                product = products[0]
                print(f"\nTesting Product Relationships:")
                print(f"Product: {product.name}")
                print(f"Brand: {product.brand.name}")
                print(f"Category: {product.category.name}")

        except Exception as e:
            print(f"Error: {str(e)}")

def test_routes():
    with app.test_client() as client:
        print("\n=== Routes Test Results ===")
        
        # Test main routes
        routes = ['/', '/admin', '/products', '/cart']
        for route in routes:
            response = client.get(route)
            print(f"Route {route}: {response.status_code}")

if __name__ == "__main__":
    test_models()
    test_routes()