from flask import render_template
from flask_mail import Message
from shop import mail, app
import json
from datetime import datetime

def send_order_confirmation_email(customer, order):
    """
    Gửi email xác nhận đơn hàng cho khách hàng

    Args:
        customer: Object Register (thông tin khách hàng)
        order: Object CustomerOrder (thông tin đơn hàng)
    """
    try:
        # Parse order data
        order_data = json.loads(order.orders) if order.orders else {}

        # Calculate totals
        total_quantity = 0
        total_before_discount = 0
        total_discount = 0

        if order_data:
            for key, product in order_data.items():
                quantity = int(product.get('quantity', 0))
                price = float(product.get('price', 0))
                discount = float(product.get('discount', 0))

                product_total = price * quantity
                product_discount = (discount / 100) * product_total

                total_quantity += quantity
                total_before_discount += product_total
                total_discount += product_discount

        final_total = total_before_discount - total_discount

        # Tạo nội dung email
        subject = f"Xác nhận đơn hàng #{order.invoice} - Belluni"

        # Render template email (sẽ tạo sau)
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }}
                .header {{ text-align: center; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 20px; }}
                .order-info {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                .product-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .product-table th, .product-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                .total-section {{ margin-top: 20px; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Belluni</h1>
                    <h2>Xác nhận đơn hàng thành công</h2>
                </div>

                <div class="order-info">
                    <h3>Thông tin đơn hàng</h3>
                    <p><strong>Mã đơn hàng:</strong> {order.invoice}</p>
                    <p><strong>Ngày đặt:</strong> {order.date_created.strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Trạng thái:</strong> {order.status}</p>
                    <p><strong>Phương thức thanh toán:</strong> {order.payment_method.upper()}</p>
                    <p><strong>Trạng thái thanh toán:</strong> {order.payment_status}</p>
                </div>

                <div class="order-info">
                    <h3>Thông tin khách hàng</h3>
                    <p><strong>Họ tên:</strong> {customer.first_name} {customer.last_name}</p>
                    <p><strong>Email:</strong> {customer.email}</p>
                    <p><strong>Số điện thoại:</strong> {customer.phone_number}</p>
                    <p><strong>Địa chỉ giao hàng:</strong> {order.address}</p>
                </div>

                <h3>Chi tiết sản phẩm</h3>
                <table class="product-table">
                    <thead>
                        <tr>
                            <th>Sản phẩm</th>
                            <th>Số lượng</th>
                            <th>Đơn giá</th>
                            <th>Giảm giá</th>
                            <th>Thành tiền</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        # Thêm sản phẩm vào bảng
        for key, product in order_data.items():
            product_name = product.get('name', 'N/A')
            quantity = int(product.get('quantity', 0))
            price = float(product.get('price', 0))
            discount = float(product.get('discount', 0))

            product_total = price * quantity
            discount_amount = (discount / 100) * product_total
            final_product_price = product_total - discount_amount

            html_body += f"""
                        <tr>
                            <td>{product_name}</td>
                            <td>{quantity}</td>
                            <td>{price:,.0f} ₫</td>
                            <td>{discount}%</td>
                            <td>{final_product_price:,.0f} ₫</td>
                        </tr>
            """

        html_body += f"""
                    </tbody>
                </table>

                <div class="total-section">
                    <p><strong>Tổng số lượng:</strong> {total_quantity} sản phẩm</p>
                    <p><strong>Tạm tính:</strong> {total_before_discount:,.0f} ₫</p>
                    <p><strong>Giảm giá:</strong> {total_discount:,.0f} ₫</p>
                    <p><strong><span style="color: #007bff; font-size: 18px;">Tổng cộng:</span></strong> <span style="color: #007bff; font-size: 18px; font-weight: bold;">{final_total:,.0f} ₫</span></p>
                </div>

                <div class="footer">
                    <p>Cảm ơn quý khách đã mua hàng tại Belluni!</p>
                    <p>Chúng tôi sẽ liên hệ với quý khách trong thời gian sớm nhất để xác nhận và giao hàng.</p>
                    <p>Nếu có bất kỳ câu hỏi nào, vui lòng liên hệ với chúng tôi qua email hoặc hotline.</p>
                    <p><strong>Email:</strong> VietHoang@gmail.com | <strong>Hotline:</strong> 1900-xxxx</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Tạo message
        msg = Message(
            subject=subject,
            recipients=[customer.email],
            html=html_body
        )

        # Gửi email
        mail.send(msg)

        print(f"✅ Email xác nhận đơn hàng đã gửi thành công đến {customer.email}")
        return True

    except Exception as e:
        print(f"❌ Lỗi khi gửi email xác nhận đơn hàng: {e}")
        return False


def send_order_status_update_email(customer, order, action_by="system"):
    """
    Gửi email cập nhật trạng thái đơn hàng

    Args:
        customer: Object Register (thông tin khách hàng)
        order: Object CustomerOrder (thông tin đơn hàng)
        action_by: Người thực hiện hành động ('customer', 'admin', 'system')
    """
    try:
        # Xác định loại hành động và nội dung phù hợp
        if order.status == 'Đang xác nhận':
            if action_by == 'admin':
                status_title = "Đơn hàng đã được xác nhận"
                status_message = "Đơn hàng của quý khách đã được xác nhận và đang được chuẩn bị để giao hàng."
                status_color = "#d4edda"  # xanh lá nhạt
                status_border = "#c3e6cb"
                status_text_color = "#155724"
                icon = "✅"
            else:
                status_title = "Đơn hàng đang được xử lý"
                status_message = "Đơn hàng của quý khách đang được chúng tôi xác nhận."
                status_color = "#fff3cd"  # vàng nhạt
                status_border = "#ffeaa7"
                status_text_color = "#856404"
                icon = "⏳"

        elif order.status == 'Đang giao':
            status_title = "Đơn hàng đang được giao"
            status_message = "Đơn hàng của quý khách đã được bàn giao cho đơn vị vận chuyển và đang trên đường đến với quý khách."
            status_color = "#cce5ff"  # xanh dương nhạt
            status_border = "#99d6ff"
            status_text_color = "#004085"
            icon = "🚚"

        elif order.status == 'Đã giao':
            status_title = "Đơn hàng đã giao thành công"
            status_message = "Đơn hàng của quý khách đã được giao thành công. Cảm ơn quý khách đã tin tưởng và sử dụng dịch vụ của chúng tôi!"
            status_color = "#d4edda"  # xanh lá nhạt
            status_border = "#c3e6cb"
            status_text_color = "#155724"
            icon = "🎉"

        elif order.status == 'Hủy đơn':
            if action_by == 'customer':
                status_title = "Đơn hàng đã được hủy"
                status_message = "Đơn hàng của quý khách đã được hủy theo yêu cầu. Nếu quý khách cần hỗ trợ thêm, vui lòng liên hệ với chúng tôi."
                status_color = "#f8d7da"  # đỏ nhạt
                status_border = "#f5c6cb"
                status_text_color = "#721c24"
                icon = "❌"
            else:  # admin hoặc system
                status_title = "Đơn hàng đã bị hủy"
                status_message = "Đơn hàng của quý khách đã bị hủy do một số lý do. Chúng tôi xin lỗi về sự bất tiện này."
                status_color = "#f8d7da"  # đỏ nhạt
                status_border = "#f5c6cb"
                status_text_color = "#721c24"
                icon = "⚠️"
        else:
            status_title = f"Đơn hàng cập nhật trạng thái: {order.status}"
            status_message = "Đơn hàng của quý khách đã được cập nhật trạng thái."
            status_color = "#e2e3e5"  # xám nhạt
            status_border = "#d6d8db"
            status_text_color = "#383d41"
            icon = "📋"

        subject = f"{icon} {status_title} #{order.invoice} - Belluni"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 20px; }}
                .status-update {{ margin: 20px 0; padding: 25px; background-color: {status_color}; border: 2px solid {status_border}; border-radius: 8px; color: {status_text_color}; text-align: center; }}
                .status-icon {{ font-size: 48px; margin-bottom: 10px; }}
                .order-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .action-info {{ background-color: #e9ecef; padding: 10px; border-radius: 5px; margin: 15px 0; font-style: italic; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; }}
                .highlight {{ background-color: #fff3cd; padding: 2px 5px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Belluni</h1>
                    <h2 style="color: #007bff; margin-top: 10px;">Thông báo cập nhật đơn hàng</h2>
                </div>

                <div class="status-update">
                    <div class="status-icon">{icon}</div>
                    <h3 style="margin: 10px 0; color: {status_text_color};">{status_title}</h3>
                    <p style="margin: 5px 0;"><strong>Mã đơn hàng:</strong> <span class="highlight">{order.invoice}</span></p>
                    <p style="margin: 5px 0;"><strong>Thời gian cập nhật:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>

                <div class="order-info">
                    <h4>Thông tin đơn hàng</h4>
                    <p><strong>Ngày đặt hàng:</strong> {order.date_created.strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Phương thức thanh toán:</strong> {order.payment_method.upper()}</p>
                    <p><strong>Trạng thái thanh toán:</strong> {order.payment_status}</p>
                    <p><strong>Địa chỉ giao hàng:</strong> {order.address}</p>
                </div>

                <p>Kính chào <strong>{customer.first_name} {customer.last_name}</strong>,</p>
                <p>{status_message}</p>

                {"<div class='action-info'>Hành động được thực hiện bởi: " + ("Khách hàng" if action_by == "customer" else "Nhân viên Belluni") + "</div>" if action_by != "system" else ""}

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>📧 Hỗ trợ:</strong> Nếu quý khách có bất kỳ câu hỏi nào, vui lòng liên hệ với chúng tôi:</p>
                    <p>• <strong>Email:</strong> VietHoang@gmail.com</p>
                    <p>• <strong>Hotline:</strong> 1900-XXXX</p>
                    <p>• <strong>Website:</strong> <a href="http://localhost:5000" style="color: #007bff;">Belluni.com</a></p>
                </div>

                <div class="footer">
                    <p><strong>Belluni</strong> - Nâng tầm trải nghiệm mua sắm của bạn!</p>
                    <p>© 2025 Belluni. Tất cả quyền được bảo lưu.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = Message(
            subject=subject,
            recipients=[customer.email],
            html=html_body
        )

        mail.send(msg)

        print(f"✅ Email cập nhật trạng thái '{order.status}' đã gửi đến {customer.email} (action by: {action_by})")
        return True

    except Exception as e:
        print(f"❌ Lỗi khi gửi email cập nhật trạng thái: {e}")
        return False

