from shop import app, db
from shop.models import Category, Brand, Addproduct

def test_database():
    with app.app_context():
        print("Testing database connection...")

        try:
            # Test categories
            categories = Category.query.all()
            print(f"✅ Categories: {len(categories)}")

            # Test brands
            brands = Brand.query.all()
            print(f"✅ Brands: {len(brands)}")

            # Test products
            products = Addproduct.query.all()
            print(f"✅ Products: {len(products)}")

            print("🎉 Database is working!")

        except Exception as e:
            print(f"❌ Database error: {e}")
            raise

if __name__ == "__main__":
    test_database()
