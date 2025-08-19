import os
import re

def fix_rating_in_template(file_path):
    """Sửa rating trong template để xử lý trường hợp không có rating"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern để tìm và thay thế rating
    old_pattern = r'{{ products\[\'average\'\]\[product\.id\]\[0\] }}/5'
    new_pattern = r'{% if product.id in products[\'average\'] %}{{ "%.1f"|format(products[\'average\'][product.id][0]) }}/5{% else %}0/5{% endif %}'
    
    content = re.sub(old_pattern, new_pattern, content)
    
    # Pattern cho vòng lặp star
    old_star_pattern = r'{% for i in range\(products\[\'average\'\]\[product\.id\]\[0\]\|int\+1\) %}'
    new_star_pattern = r'{% if product.id in products[\'average\'] %}{% for i in range(products[\'average\'][product.id][0]|int) %}'
    content = re.sub(old_star_pattern, new_star_pattern, content)
    
    # Pattern cho vòng lặp star empty
    old_empty_pattern = r'{% for i in range\(products\[\'average\'\]\[product\.id\]\[0\]\|int \+ 1, 5\) %}'
    new_empty_pattern = r'{% endfor %}{% for i in range(products[\'average\'][product.id][0]|int, 5) %}'
    content = re.sub(old_empty_pattern, new_empty_pattern, content)
    
    # Pattern cho count
    old_count_pattern = r'{% if products\[\'average\'\]\[product\.id\]\[1\] != 0 %}'
    new_count_pattern = r'{% if products[\'average\'][product.id][1] > 0 %}'
    content = re.sub(old_count_pattern, new_count_pattern, content)
    
    # Thêm else block cho trường hợp không có rating
    content = content.replace(
        '{% endif %}',
        '{% else %}{% for i in range(5) %}<span class="glyphicon glyphicon-star-empty"></span>{% endfor %}(0){% endif %}'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Đã sửa: {file_path}")

def main():
    """Sửa tất cả các template có rating"""
    templates_to_fix = [
        'shop/templates/customers/index.html',
        'shop/templates/products/product.html'
    ]
    
    for template in templates_to_fix:
        if os.path.exists(template):
            fix_rating_in_template(template)
        else:
            print(f"Không tìm thấy file: {template}")

if __name__ == "__main__":
    main()
