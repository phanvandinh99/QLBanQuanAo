#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Vietnamese PDF generation
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

def test_vietnamese_pdf():
    """Test PDF generation with Vietnamese characters"""

    # Create buffer
    buffer = io.BytesIO()

    try:
        # Register Arial font
        arial_font_path = r"C:\Windows\Fonts\arial.ttf"
        arial_bold_path = r"C:\Windows\Fonts\arialbd.ttf"

        pdfmetrics.registerFont(TTFont('ArialUnicode', arial_font_path))
        pdfmetrics.registerFont(TTFont('ArialUnicode-Bold', arial_bold_path))

        default_font = 'ArialUnicode'
        print("Successfully registered Arial font for Vietnamese support")

    except Exception as e:
        print(f"Failed to register Arial font: {e}")
        default_font = 'Helvetica'

    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Update font for styles
    try:
        styles['Heading1'].fontName = default_font
        styles['Normal'].fontName = default_font
    except:
        pass

    # Create title style
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=1,
        spaceAfter=20,
        fontName=default_font
    )

    # Create info style
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        fontName=default_font
    )

    # Test Vietnamese text
    vietnamese_texts = [
        "HÓA ĐƠN BÁN HÀNG",
        "CỬA HÀNG Belluni",
        "Địa chỉ: Số 298 Đ. Cầu Diễn, Minh Khai, Bắc Từ Liêm, Hà Nội",
        "Điện thoại: 0332194677",
        "Email: TruongVietHoang@gmail..com",
        "Mã đơn hàng: #12345",
        "Ngày đặt: 10/09/2025 15:34",
        "Trạng thái: Đang xác nhận",
        "THÔNG TIN KHÁCH HÀNG",
        "Họ tên: Nguyễn Văn An",
        "Email: nguyenvanan@gmail.com",
        "SĐT: 0987 654 321",
        "Địa chỉ: 456 Đường XYZ, Quận 2, TP.HCM",
        "CHI TIẾT SẢN PHẨM",
        "STT, Tên sản phẩm, SL, Đơn giá, Giảm giá, Thành tiền",
        "Áo Phông Bé Trai Túi Hộp",
        "Bộ Đồ Vải Hiệu Ứng",
        "Cảm ơn quý khách đã mua hàng tại Belluni!"
    ]

    # Add title
    elements.append(Paragraph(vietnamese_texts[0], title_style))
    elements.append(Spacer(1, 0.5*inch))

    # Add store info
    for text in vietnamese_texts[1:5]:
        elements.append(Paragraph(text, info_style))

    elements.append(Spacer(1, 0.3*inch))

    # Add order info
    for text in vietnamese_texts[5:8]:
        elements.append(Paragraph(text, info_style))

    elements.append(Spacer(1, 0.2*inch))

    # Add customer info
    elements.append(Paragraph(vietnamese_texts[8], title_style))
    for text in vietnamese_texts[9:13]:
        elements.append(Paragraph(text, info_style))

    elements.append(Spacer(1, 0.3*inch))

    # Add product details
    elements.append(Paragraph(vietnamese_texts[13], title_style))
    elements.append(Paragraph("Ví dụ sản phẩm: " + vietnamese_texts[15], info_style))
    elements.append(Paragraph("Ví dụ sản phẩm: " + vietnamese_texts[16], info_style))

    elements.append(Spacer(1, 0.5*inch))

    # Add footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=11,
        fontName=default_font,
        alignment=1,
        textColor=colors.grey
    )
    elements.append(Paragraph(vietnamese_texts[17], footer_style))

    # Build PDF
    doc.build(elements)

    # Save to file
    buffer.seek(0)
    with open('test_vietnamese.pdf', 'wb') as f:
        f.write(buffer.getvalue())

    print("Test PDF created successfully: test_vietnamese.pdf")
    print(f"Used font: {default_font}")

if __name__ == '__main__':
    test_vietnamese_pdf()
