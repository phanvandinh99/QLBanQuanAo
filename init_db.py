#!/usr/bin/env python3
"""
Script để khởi tạo database từ SQLAlchemy models
"""

from shop import app, db
from shop.models import *

def init_database():
    """Khởi tạo database và tạo các bảng cần thiết"""
    try:
        with app.app_context():
            print("Đang tạo các bảng database...")
            db.create_all()
            print("✅ Tất cả các bảng đã được tạo thành công!")

            # Kiểm tra và thêm dữ liệu mẫu nếu cần
            category_count = Category.query.count()
            brand_count = Brand.query.count()
            print(f"Số categories hiện tại: {category_count}")
            print(f"Số brands hiện tại: {brand_count}")

            if category_count == 0:
                print("Đang thêm dữ liệu mẫu...")

                # Thêm categories
                categories = [
                    Category(name='Nam'),
                    Category(name='Nữ'),
                    Category(name='Trẻ Em'),
                    Category(name='Phụ Kiện')
                ]
                db.session.add_all(categories)
                db.session.commit()

                # Thêm brands
                brands = [
                    Brand(name='Áo Khoác Nam', category_id=1),
                    Brand(name='Áo Nam', category_id=1),
                    Brand(name='Quần Nam', category_id=1),
                    Brand(name='Đồ Thể Thao Nam', category_id=1),
                    Brand(name='Áo Khoác Nữ', category_id=2),
                    Brand(name='Áo Nữ', category_id=2),
                    Brand(name='Quần Nữ', category_id=2),
                    Brand(name='Đồ thể Thao Nữ', category_id=2),
                    Brand(name='Túi Xách', category_id=4),
                    Brand(name='Tất', category_id=4),
                    Brand(name='Ví', category_id=4),
                    Brand(name='Giày', category_id=4),
                    Brand(name='Áo Khoác Trẻ Em', category_id=3),
                    Brand(name='Áo Trẻ Em', category_id=3),
                    Brand(name='Quần Trẻ Em', category_id=3)
                ]
                db.session.add_all(brands)
                db.session.commit()

                print("✅ Dữ liệu mẫu đã được thêm!")

            # Kiểm tra riêng brands
            if brand_count == 0 and category_count > 0:
                print("Đang thêm brands...")

                # Thêm brands
                brands = [
                    Brand(name='Áo Khoác Nam', category_id=1),
                    Brand(name='Áo Nam', category_id=1),
                    Brand(name='Quần Nam', category_id=1),
                    Brand(name='Đồ Thể Thao Nam', category_id=1),
                    Brand(name='Áo Khoác Nữ', category_id=2),
                    Brand(name='Áo Nữ', category_id=2),
                    Brand(name='Quần Nữ', category_id=2),
                    Brand(name='Đồ thể Thao Nữ', category_id=2),
                    Brand(name='Túi Xách', category_id=4),
                    Brand(name='Tất', category_id=4),
                    Brand(name='Ví', category_id=4),
                    Brand(name='Giày', category_id=4),
                    Brand(name='Áo Khoác Trẻ Em', category_id=3),
                    Brand(name='Áo Trẻ Em', category_id=3),
                    Brand(name='Quần Trẻ Em', category_id=3)
                ]
                db.session.add_all(brands)
                db.session.commit()

                print("✅ Brands đã được thêm!")

            print("🎉 Database đã sẵn sàng!")
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo database: {e}")
        raise

if __name__ == "__main__":
    init_database()
