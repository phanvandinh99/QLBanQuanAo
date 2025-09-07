#!/usr/bin/env python3
"""
Script để cập nhật database schema cho articles table
"""
import pymysql
from datetime import datetime

def update_articles_table():
    try:
        # Kết nối database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='myshop',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            print("🔄 Đang cập nhật bảng articles...")

            # Cập nhật schema để updated_at có thể null
            alter_sql = """
            ALTER TABLE `articles`
            MODIFY `updated_at` datetime DEFAULT NULL;
            """

            cursor.execute(alter_sql)
            connection.commit()

            print("✅ Đã cập nhật bảng articles thành công!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    update_articles_table()
