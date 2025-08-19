from shop import app, db
from shop.products.models import Brand, Category, Addproduct, Rate

def create_tables():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()