import os
import shutil
from shop import app, db
from shop.models import Addproduct

def create_placeholder_images():
    """Tạo các file ảnh placeholder cho sản phẩm"""
    with app.app_context():
        # Lấy tất cả sản phẩm từ database
        products = Addproduct.query.all()
        
        # File ảnh gốc để copy
        source_image = "shop/static/images/phone.jpg"
        
        if not os.path.exists(source_image):
            print(f"Không tìm thấy file ảnh gốc: {source_image}")
            return
        
        created_count = 0
        for product in products:
            # Tạo ảnh cho image_1, image_2, image_3
            for image_field in ['image_1', 'image_2', 'image_3']:
                image_name = getattr(product, image_field)
                if image_name:
                    target_path = f"shop/static/images/{image_name}"
                    if not os.path.exists(target_path):
                        try:
                            shutil.copy2(source_image, target_path)
                            created_count += 1
                            print(f"Đã tạo: {image_name}")
                        except Exception as e:
                            print(f"Lỗi khi tạo {image_name}: {e}")
        
        print(f"\nHoàn thành! Đã tạo {created_count} file ảnh placeholder.")

if __name__ == "__main__":
    create_placeholder_images()
