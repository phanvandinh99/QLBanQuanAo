import urllib
import os
import secrets
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import current_user
from shop import app, db, photos
from shop.models import Brand, Category, Product, Rating, Customer, Admin, Article, ProductVariant, Size, Color, StockMovement
from shop.utils.response_utils import ajax_response, is_ajax_request, success_response, error_response
from .forms import Rates, Addproducts, AddProductsForm, ProductVariantRowForm

def get_products_with_stock():
    """Helper function to get products that have variants with stock > 0"""
    return Product.query.join(ProductVariant).filter(
        ProductVariant.product_id == Product.id,
        ProductVariant.is_active == True,
        ProductVariant.stock > 0
    ).distinct()

@app.route('/toast-debug')
def toast_debug():
    """Debug page for toast system"""
    return render_template('toast_debug.html')

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = get_products_with_stock().paginate(page=page, per_page=8)

    # Get published articles for the articles section
    articles = Article.query.filter_by(status='published').order_by(Article.created_at.desc()).limit(3).all()

    return render_template('products/index.html', products=products, articles=articles, categories=categories(), brands=brands())


@app.route('/category')
def get_all_category():
    page = request.args.get('page', 1, type=int)
    products_all = get_products_with_stock().order_by(Product.id.desc()).paginate(page=page, per_page=9)
    products_new = get_products_with_stock().order_by(Product.id.desc()).limit(2).all()
    products = {'all': products_all, 'new': products_new, 'average': medium()}
    return render_template('products/category.html', products=products, brands=brands(), categories=categories())


@app.route('/category/brand/<string:name>')
def get_brand(name):
    page = request.args.get('page', 1, type=int)
    get_brand = Brand.query.filter_by(name=name).first_or_404()
    brand = Product.query.filter_by(brand=get_brand).paginate(page=page, per_page=9)

    products_new = get_products_with_stock().order_by(Product.id.desc()).limit(2).all()
    products = {'all': brand, 'new': products_new, 'average': medium()}
    return render_template('products/category.html', products=products, brand=name, brands=brands(),
                           categories=categories(),
                           get_brand=get_brand)


@app.route('/categories/<string:name>')
def get_category(name):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(name=name).first_or_404()
    get_cat_prod = Product.query.filter_by(category=get_cat).paginate(page=page, per_page=9)
    products_new = get_products_with_stock().order_by(Product.id.desc()).limit(2).all()
    products = {'all': get_cat_prod, 'new': products_new, 'average': medium()}
    get_cat_prod = {'name': name, 'id': get_cat.id}
    return render_template('products/category.html', products=products, get_cat_prod=get_cat_prod, brands=brands(),
                           categories=categories(),
                           get_cat=get_cat)


@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        if is_ajax_request():
            return error_response('Yêu cầu đăng nhập')
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
        
    if request.method == "POST":
        try:
            getbrand = request.form.get('brand')
            category = request.form.get('category')
            
            if not getbrand or not category:
                error_msg = 'Vui lòng điền đầy đủ thông tin thương hiệu và danh mục'
                if is_ajax_request():
                    return error_response(error_msg)
                flash(error_msg, 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                categories = Category.query.all()
                return render_template('products/addbrand.html', title='Add brand', categories=categories, brands='brands',
                                       user=user[0])
            
            brand = Brand(name=getbrand, category_id=category)
            db.session.add(brand)
            db.session.commit()
            
            success_msg = f'Thương hiệu {getbrand} đã thêm thành công'
            if is_ajax_request():
                return success_response(success_msg, reset_form=True)
            flash(success_msg, 'success')
            return redirect(url_for('addbrand'))
            
        except Exception as e:
            db.session.rollback()
            error_msg = f'Lỗi khi thêm thương hiệu: {str(e)}'
            if is_ajax_request():
                return error_response(error_msg)
            flash(error_msg, 'danger')
            user = Admin.query.filter_by(email=session['email']).all()
            categories = Category.query.all()
            return render_template('products/addbrand.html', title='Add brand', categories=categories, brands='brands',
                                   user=user[0])
    
    user = Admin.query.filter_by(email=session['email']).all()
    categories = Category.query.all()
    return render_template('products/addbrand.html', title='Add brand', categories=categories, brands='brands',
                           user=user[0])


@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash('Login first please', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == "POST":
        updatebrand.name = brand
        flash(f'Thương hiệu {updatebrand.name} đã được cập nhật', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('products/updatebrand.html', title='Uppdate brand', brands='brands', updatebrand=updatebrand,
                           categories=categories(), user=user[0])


@app.route('/deletebrand/<int:id>', methods=['GET', 'POST'])
def deletebrand(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        try:
            products = Product.query.filter(Product.category_id == id).all()
            for product in products:
                rates = Rating.query.filter(Rating.product_id == product.id).all()
                for rate in rates:
                    db.session.delete(rate)
                db.session.delete(product)
            db.session.delete(brand)
            db.session.commit()
            flash(f"Thương hiệu {brand.name} đã xóa thành công", "success")
            return redirect(url_for('brands'))
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi khi xóa thương hiệu: {str(e)}", "danger")
            return redirect(url_for('brands'))
    flash(f"Thương hiệu {brand.name} không thể xóa", "warning")
    return redirect(url_for('brands'))


@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
    if 'email' not in session:
        if is_ajax_request():
            return error_response('Yêu cầu đăng nhập')
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
        
    if request.method == "POST":
        try:
            getcat = request.form.get('category')
            
            if not getcat:
                error_msg = 'Vui lòng nhập tên danh mục'
                if is_ajax_request():
                    return error_response(error_msg)
                flash(error_msg, 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addbrand.html', title='Add category', user=user[0])
            
            cat = Category(name=getcat)
            db.session.add(cat)
            db.session.commit()
            
            success_msg = f'Danh mục {getcat} đã được thêm thành công'
            if is_ajax_request():
                return success_response(success_msg, reset_form=True)
            flash(success_msg, 'success')
            return redirect(url_for('addcat'))
            
        except Exception as e:
            db.session.rollback()
            error_msg = f'Lỗi khi thêm danh mục: {str(e)}'
            if is_ajax_request():
                return error_response(error_msg)
            flash(error_msg, 'danger')
            user = Admin.query.filter_by(email=session['email']).all()
            return render_template('products/addbrand.html', title='Add category', user=user[0])
    
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('products/addbrand.html', title='Add category', user=user[0])


@app.route('/updatecat/<int:id>', methods=['GET', 'POST'])
def updatecat(id):
    if 'email' not in session:
        flash('Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == "POST":
        updatecat.name = category
        flash(f'Loại sản phẩm {updatecat.name} đã được cập nhật', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('products/updatebrand.html', title='Update cat', updatecat=updatecat, user=user[0])


@app.route('/deletecat/<int:id>', methods=['GET', 'POST'])
def deletecat(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        try:
            products = Product.query.filter(Product.category_id == id).all()
            for product in products:
                rates = Rating.query.filter(Rating.product_id == product.id).all()
                for rate in rates:
                    db.session.delete(rate)
                db.session.delete(product)

            brands = Brand.query.filter(Brand.category_id == id).all()
            for brand in brands:
                db.session.delete(brand)

            db.session.delete(category)
            db.session.commit()
            flash(f"Danh mục {category.name} đã được xóa thành công", "success")
            return redirect(url_for('categories'))
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi khi xóa danh mục: {str(e)}", "danger")
            return redirect(url_for('categories'))
    flash(f"Danh mục {category.name} không thể xóa", "warning")
    return redirect(url_for('categories'))


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    form = Addproducts()
    brands = Brand.query.all()
    categories = Category.query.all()
    sizes = Size.query.order_by(Size.sort_order).all()
    colors = Color.query.order_by(Color.name).all()


    if request.method == "POST":
        try:
            # Populate form with request data and files
            form = Addproducts(request.form)
            form.image_1.data = request.files.get('image_1')
            form.image_2.data = request.files.get('image_2')
            form.image_3.data = request.files.get('image_3')


            # Manual validation for required images
            if not form.image_1.data or not form.image_1.data.filename:
                form.image_1.errors.append('Vui lòng chọn ảnh 1')
            if not form.image_2.data or not form.image_2.data.filename:
                form.image_2.errors.append('Vui lòng chọn ảnh 2')
            if not form.image_3.data or not form.image_3.data.filename:
                form.image_3.errors.append('Vui lòng chọn ảnh 3')

            # Validate form data
            if not form.validate():
                # Hiển thị lỗi chi tiết từ form validation
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                if error_messages:
                    # Hiển thị thông báo lỗi chi tiết hơn
                    if len(error_messages) == 1 and 'Chỉ chấp nhận file ảnh' in error_messages[0]:
                        flash('Vui lòng chọn file ảnh có định dạng đúng (JPG, PNG, GIF, JPEG, WEBP, BMP, SVG, ICO)', 'danger')
                    else:
                        flash('Lỗi xác thực dữ liệu: ' + '; '.join(error_messages), 'danger')
                else:
                    flash('Lỗi khi thêm mới sản phẩm vào hệ thống', 'danger')

                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, sizes=sizes, colors=colors, user=user[0])
            
            name = form.name.data
            discount = form.discount.data or 0
            desc = form.description.data
            brand = request.form.get('brand')
            category = request.form.get('category')
            
            # Tất cả sản phẩm đều có variants
            has_variants = True  # Luôn True
            
            # Bỏ price và stock vì lấy từ variants
            # price = 0  # Không còn cần
            # stock = 0  # Không còn cần
            colors = ''  # Không còn cần vì có variants

            # Additional server-side validation
            if discount < 0 or discount > 100:
                flash('Giảm giá phải nằm trong khoảng 0-100%', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, sizes=sizes, colors=colors, user=user[0])

            image_1 = request.files.get('image_1')
            image_2 = request.files.get('image_2')
            image_3 = request.files.get('image_3')

            if not image_1 or not image_2 or not image_3:
                flash('Vui lòng chọn đầy đủ 3 ảnh cho sản phẩm', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, sizes=sizes, colors=colors, user=user[0])

            name_random_1 = secrets.token_hex(10) + "."
            name_random_2 = secrets.token_hex(10) + "."
            name_random_3 = secrets.token_hex(10) + "."

            save_link_1 = "" + name_random_1 + image_1.filename.split('.')[-1]
            save_link_2 = "" + name_random_2 + image_2.filename.split('.')[-1]
            save_link_3 = "" + name_random_3 + image_3.filename.split('.')[-1]

            # save static/images
            try:
                image_1 = photos.save(image_1, name=name_random_1)
                image_2 = photos.save(image_2, name=name_random_2)
                image_3 = photos.save(image_3, name=name_random_3)
            except Exception as img_error:
                flash(f'Lỗi khi lưu ảnh: {str(img_error)}', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, sizes=sizes, colors=colors, user=user[0])

            try:
                # Create product - tất cả sản phẩm đều có variants
                product = Product(
                    name=name, 
                    # Bỏ price và stock vì lấy từ variants
                    # price=price,
                    # stock=stock,
                    sold_quantity=0, 
                    colors=colors,  # Không còn cần thiết
                    description=desc,
                    category_id=category, 
                    brand_id=brand, 
                    image_1=image_1, 
                    image_2=image_2, 
                    image_3=image_3,
                    has_variants=True  # Luôn True
                )
                db.session.add(product)
                db.session.flush()  # Get product.id

                # Tất cả sản phẩm đều có variants
                user = Admin.query.filter_by(email=session['email']).first()
                variants_data = []
                
                # Get variants from form data
                variant_count = 0
                while f'variant_{variant_count}_price' in request.form:
                    size_id = request.form.get(f'variant_{variant_count}_size_id')
                    color_id = request.form.get(f'variant_{variant_count}_color_id')
                    variant_price = request.form.get(f'variant_{variant_count}_price')
                    variant_stock = request.form.get(f'variant_{variant_count}_stock')
                    sku = request.form.get(f'variant_{variant_count}_sku')

                    if variant_price:  # Only create if price is provided (stock will be 0 initially)
                        variants_data.append({
                            'size_id': int(size_id) if size_id and size_id != '0' else None,
                            'color_id': int(color_id) if color_id and color_id != '0' else None,
                            'price': float(variant_price),
                            'stock': 0,  # Always 0, will be updated via purchase orders
                            'sku': sku if sku else None
                        })
                    variant_count += 1

                if not variants_data:
                    raise Exception('Sản phẩm phải có ít nhất một biến thể!')

                # Create variants
                total_stock = 0
                for variant_data in variants_data:
                    # Check for duplicate combinations
                    existing = ProductVariant.query.filter_by(
                        product_id=product.id,
                        size_id=variant_data['size_id'],
                        color_id=variant_data['color_id']
                    ).first()

                    if existing:
                        continue  # Skip duplicates

                    variant = ProductVariant(
                        product_id=product.id,
                        size_id=variant_data['size_id'],
                        color_id=variant_data['color_id'],
                        price=variant_data['price'],
                        stock=variant_data['stock'],
                        sku=variant_data['sku'],
                        is_active=True
                    )

                    db.session.add(variant)
                    db.session.flush()  # Ensure variant has ID before creating stock movement

                    # Generate SKU if not provided
                    if not variant.sku:
                        variant.sku = variant.generate_sku()

                    total_stock += variant_data['stock']

                    # Note: Stock movements will be created via purchase orders, not during product creation

                # Update product min/max price from variants
                if variants_data:
                    prices = [v['price'] for v in variants_data]
                    product.min_price = min(prices)
                    product.max_price = max(prices)
                else:
                    product.min_price = 0
                    product.max_price = 0

                db.session.commit()

                # Tất cả sản phẩm đều có variants
                flash(f'Sản phẩm {product.name} với {len(variants_data)} biến thể đã được thêm thành công!', 'success')
                return redirect(url_for('addproduct'))

            except Exception as db_error:
                raise  # Re-raise để catch block bên ngoài xử lý
            
        except Exception as e:
            # Rollback session nếu có lỗi
            db.session.rollback()
            flash(f'Lỗi khi thêm sản phẩm: {str(e)}', 'danger')
            user = Admin.query.filter_by(email=session['email']).all()
            return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                   categories=categories, sizes=sizes, colors=colors, user=user[0])
    
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                           categories=categories, sizes=sizes, colors=colors, user=user[0])




@app.route('/api/brands/<int:category_id>')
def get_brands_by_category(category_id):
    """API endpoint to get brands by category"""
    brands = Brand.query.filter_by(category_id=category_id).order_by(Brand.name).all()
    return jsonify([{
        'id': brand.id,
        'name': brand.name
    } for brand in brands])


@app.route('/api/products/<int:product_id>')
def get_product_info(product_id):
    """API endpoint to get product information"""
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'category': product.category.name if product.category else None,
        'brand': product.brand.name if product.brand else None,
        'stock': product.total_stock,
        'price': float(product.current_price) if not product.has_variants else None,
        'display_price': product.display_price,
        'has_variants': product.has_variants,
        'discount': product.discount,
        'colors': product.colors
    })

@app.route('/api/colors')
def get_colors():
    """API endpoint to get all colors"""
    colors = Color.query.order_by(Color.name).all()
    return jsonify([{
        'id': color.id,
        'name': color.name,
        'hex_code': color.hex_code
    } for color in colors])

@app.route('/api/sizes')
def get_sizes():
    """API endpoint to get all sizes"""
    sizes = Size.query.order_by(Size.sort_order).all()
    return jsonify([{
        'id': size.id,
        'name': size.name,
        'display_name': size.display_name,
        'sort_order': size.sort_order
    } for size in sizes])





@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    if 'email' not in session:
        if is_ajax_request():
            return error_response('Yêu cầu đăng nhập')
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    form = Addproducts(request.form)
    product = Product.query.get_or_404(id)
    brands = Brand.query.all()
    categories = Category.query.all()
    brand = request.form.get('brand')
    category = request.form.get('category')

    if request.method == "POST":
        try:
            product.name = form.name.data
            # product.current_price = form.price.data  # Đã bỏ vì sử dụng variants
            product.discount = form.discount.data
            # Do not allow direct stock editing here; stock is managed via purchases
            product.colors = form.colors.data
            product.description = form.description.data
            product.category_id = category
            product.brand_id = brand
            
            if request.files.get('image_1'):
                image_1 = request.files.get('image_1')
                name_random_1 = secrets.token_hex(10) + "."
                save_link_1 = "" + name_random_1 + image_1.filename.split('.')[-1]
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                    product.image_1 = photos.save(image_1, name=name_random_1)
                except Exception as img_error:
                    if is_ajax_request():
                        current_app.logger.warning(f'Lỗi khi cập nhật ảnh 1: {str(img_error)}')
                    else:
                        flash(f'Lỗi khi cập nhật ảnh 1: {str(img_error)}', 'warning')
                    product.image_1 = photos.save(image_1, name=name_random_1)
            
            if request.files.get('image_2'):
                image_2 = request.files.get('image_2')
                name_random_2 = secrets.token_hex(10) + "."
                save_link_2 = "" + name_random_2 + image_2.filename.split('.')[-1]
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                    product.image_2 = photos.save(image_2, name=name_random_2)
                except Exception as img_error:
                    if is_ajax_request():
                        current_app.logger.warning(f'Lỗi khi cập nhật ảnh 2: {str(img_error)}')
                    else:
                        flash(f'Lỗi khi cập nhật ảnh 2: {str(img_error)}', 'warning')
                    product.image_2 = photos.save(image_2, name=name_random_2)
            
            if request.files.get('image_3'):
                image_3 = request.files.get('image_3')
                name_random_3 = secrets.token_hex(10) + "."
                save_link_3 = "" + name_random_3 + image_3.filename.split('.')[-1]
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                    product.image_3 = photos.save(image_3, name=name_random_3)
                except Exception as img_error:
                    if is_ajax_request():
                        current_app.logger.warning(f'Lỗi khi cập nhật ảnh 3: {str(img_error)}')
                    else:
                        flash(f'Lỗi khi cập nhật ảnh 3: {str(img_error)}', 'warning')
                    product.image_3 = photos.save(image_3, name=name_random_3)
            
            db.session.commit()
            success_msg = f'Sản phẩm {product.name} đã được cập nhật thành công'
            
            if is_ajax_request():
                return success_response(success_msg, redirect_url=url_for('product'))
            flash(success_msg, 'success')
            return redirect(url_for('product'))
            
        except Exception as e:
            # Rollback session nếu có lỗi
            db.session.rollback()
            error_msg = f'Lỗi khi cập nhật sản phẩm: {str(e)}'
            
            if is_ajax_request():
                return error_response(error_msg)
            flash(error_msg, 'danger')
            user = Admin.query.filter_by(email=session['email']).all()
            return render_template('products/updateproduct.html', form=form, product=product, title='Update Product', brands=brands,
                                   categories=categories, user=user[0])

    form.name.data = product.name
    # form.price.data = product.current_price  # Đã bỏ vì sử dụng variants
    form.discount.data = product.discount
    # form.stock.data = product.total_stock  # Đã bỏ vì sử dụng variants
    # form.colors.data = product.colors  # Đã bỏ vì sử dụng variants
    form.description.data = product.description
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('products/updateproduct.html', form=form, product=product, title='Update Product', brands=brands,
                           categories=categories, user=user[0])






@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        try:
            # Delete image files
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
            except Exception:
                pass  # Ignore file deletion errors

            # Delete ratings and product in a single transaction
            rates = Rating.query.filter(Rating.product_id == id).all()
            for rate in rates:
                db.session.delete(rate)
            db.session.delete(product)
            db.session.commit()

            flash(f'Sản phẩm {product.name} đã được xóa khỏi hệ thống', 'success')
            return redirect(url_for('product'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi xóa sản phẩm: {str(e)}', 'danger')
            return redirect(url_for('product'))
    flash(f'Không thể xóa sản phẩm', 'warning')
    return redirect(url_for('product'))


@app.route('/addrate', methods=['GET', 'POST'])
def addrate():
    form = Rates(request.form)
    products_hot = get_products_with_stock().order_by(Product.min_price.desc()).limit(3).all()
    products_new = get_products_with_stock().order_by(Product.id.desc()).all()
    products_sell = get_products_with_stock().order_by(Product.discount.desc()).limit(10).all()
    products = {'hot': products_hot, 'new': products_new, 'sell': products_sell, 'average': medium()}
    product_id = -1
    if request.method == "POST":
        register_id = request.form.get('register_id')
        product_id = request.form.get('product_id')
        desc = request.form.get('desc')
        rate_number = request.form.get('select')
        rate = Rating(register_id=register_id, product_id=product_id, desc=desc, rate_number=rate_number)
        db.session.add(rate)
        flash(f'The rate {register_id} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('detail', id=product_id))
        # return "OK this is a post method"
    rates = Rating.query.filter(Rating.product_id == product_id).order_by(Rating.id.desc()).all()
    product = Product.query.get_or_404(product_id)
    return render_template('products/product.html', title='Add rate', form=form, products=products, rates=rates,
                           product=product, brands=brands(), registers=registers(), categories=categories())


@app.route('/detail/id_<int:id>')
def detail(id):
    kt = False
    customer = None
    if current_user.is_authenticated:
        customer = Customer.query.get_or_404(current_user.id)
        rates = Rating.query.order_by(Rating.id.desc()).all()
        for rate in rates:
            if id == rate.product_id and customer.id == rate.register_id:
                kt = True
    form = Rates(request.form)
    rates = Rating.query.filter(Rating.product_id == id).order_by(Rating.id.desc()).all()
    products_hot = get_products_with_stock().order_by(Product.min_price.desc()).limit(3).all()
    products_new = get_products_with_stock().order_by(Product.id.desc()).limit(2).all()
    products_sell = get_products_with_stock().order_by(Product.discount.desc()).limit(10).all()
    products = {'hot': products_hot, 'new': products_new, 'sell': products_sell, 'average': medium()}
    product = Product.query.get_or_404(id)
    # products = Product.query.filter_by(id='id')
    return render_template('products/product.html', product=product, products=products, brands=brands(), form=form,
                           rates=rates, registers=registers(), categories=categories(), customer=customer, kt=kt)


@app.route('/category/discount/<int:start>-<int:end>')
def get_discount(start, end):
    page = request.args.get('page', 1, type=int)
    product_discount = Product.query.filter(Product.discount >= start, Product.discount < end) \
        .order_by(Product.id.desc()).paginate(page=page, per_page=9)
    products_new = get_products_with_stock().order_by(Product.id.desc()).limit(2).all()
    products = {'all': product_discount, 'new': products_new, 'average': medium()}
    return render_template('products/category.html', products=products, brands=brands(), categories=categories())


@app.route('/search', methods=['GET', 'POST'])
def search():
    value = request.form['search']
    search = "%{}%".format(value.lower())
    page = request.args.get('page', 1, type=int)
    product = Product.query.filter(Product.name.ilike(search)).paginate(page=page, per_page=9)
    products = {'all': product, 'average': medium()}
    return render_template('products/category.html', get_search=value, products=products, brands=brands(),
                           categories=categories())




# ============= ARTICLE ROUTES =============

@app.route('/articles')
def articles_list():
    """Display list of all published articles"""
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter_by(status='published').order_by(Article.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('articles/list.html', articles=articles, brands=brands(), categories=categories())


@app.route('/article/<string:slug>')
def article_detail(slug):
    """Display individual article"""
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()

    # Get related articles (other published articles, excluding current one)
    related_articles = Article.query.filter(
        Article.status == 'published',
        Article.id != article.id
    ).order_by(Article.created_at.desc()).limit(3).all()

    return render_template('articles/detail.html', article=article, related_articles=related_articles,
                         brands=brands(), categories=categories())


def brands():
    return Brand.query.all()


def categories():
    return Category.query.order_by(Category.name.desc()).all()


def medium():
    # Calculate average rating for each product
    from shop.models import Rating
    from sqlalchemy import func
    
    # Get all products with their average ratings and count
    ratings = db.session.query(
        Rating.product_id,
        func.avg(Rating.rating).label('avg_rating'),
        func.count(Rating.id).label('count')
    ).group_by(Rating.product_id).all()
    
    # Create a dictionary with product_id as key and [avg_rating, count] as value
    rating_dict = {}
    for rating in ratings:
        rating_dict[rating.product_id] = [float(rating.avg_rating), rating.count]
    
    return rating_dict


def registers():
    # Get all registered users
    return Customer.query.all()
