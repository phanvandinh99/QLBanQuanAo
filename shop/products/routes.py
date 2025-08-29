import urllib
import os
import secrets
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import current_user
from shop import app, db, photos
from shop.models import Brand, Category, Addproduct, Rate, Register, Admin
from .forms import Rates, Addproducts

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).paginate(page=page, per_page=8)
    return render_template('products/index.html', products=products, categories=categories(), brands=brands())


@app.route('/category')
def get_all_category():
    page = request.args.get('page', 1, type=int)
    products_all = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page,
                                                                                                         per_page=9)
    products_new = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).limit(2).all()
    products = {'all': products_all, 'new': products_new, 'average': medium()}
    return render_template('products/category.html', products=products, brands=brands(), categories=categories())


@app.route('/category/brand/<string:name>')
def get_brand(name):
    page = request.args.get('page', 1, type=int)
    get_brand = Brand.query.filter_by(name=name).first_or_404()
    brand = Addproduct.query.filter_by(brand=get_brand).paginate(page=page, per_page=9)

    products_new = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).limit(2).all()
    products = {'all': brand, 'new': products_new, 'average': medium()}
    return render_template('products/category.html', products=products, brand=name, brands=brands(),
                           categories=categories(),
                           get_brand=get_brand)


@app.route('/categories/<string:name>')
def get_category(name):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(name=name).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=9)
    products_new = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).limit(2).all()
    products = {'all': get_cat_prod, 'new': products_new, 'average': medium()}
    get_cat_prod = {'name': name, 'id': get_cat.id}
    return render_template('products/category.html', products=products, get_cat_prod=get_cat_prod, brands=brands(),
                           categories=categories(),
                           get_cat=get_cat)


@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        try:
            getbrand = request.form.get('brand')
            category = request.form.get('category')
            
            if not getbrand or not category:
                flash('Vui lòng điền đầy đủ thông tin thương hiệu và danh mục', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                categories = Category.query.all()
                return render_template('products/addbrand.html', title='Add brand', categories=categories, brands='brands',
                                       user=user[0])
            
            brand = Brand(name=getbrand, category_id=category)
            db.session.add(brand)
            db.session.commit()
            flash(f'Thương hiệu {getbrand} đã thêm thành công', 'success')
            return redirect(url_for('addbrand'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm thương hiệu: {str(e)}', 'danger')
            print(f"Error adding brand: {str(e)}")  # Log lỗi để debug
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
        print("Brand", brand)
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
        products = Addproduct.query.filter(Addproduct.category_id == id).all()
        for product in products:
            rates = Rate.query.filter(Rate.product_id == product.id).all()
            for rate in rates:
                db.session.delete(rate)
                db.session.commit()
            db.session.delete(product)
            db.session.commit()
        db.session.delete(brand)
        db.session.commit()
        flash(f"Thương hiệu {brand.name} đã xóa thành công", "success")
        return redirect(url_for('brands'))
    flash(f"Thương hiệu {brand.name} không thể xóa", "warning")
    return redirect(url_for('brands'))


@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        try:
            getcat = request.form.get('category')
            
            if not getcat:
                flash('Vui lòng nhập tên danh mục', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addbrand.html', title='Add category', user=user[0])
            
            cat = Category(name=getcat)
            db.session.add(cat)
            db.session.commit()
            flash(f'Danh mục {getcat} đã được thêm thành công', 'success')
            return redirect(url_for('addcat'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm danh mục: {str(e)}', 'danger')
            print(f"Error adding category: {str(e)}")  # Log lỗi để debug
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
        products = Addproduct.query.filter(Addproduct.category_id == id).all()
        for product in products:
            rates = Rate.query.filter(Rate.product_id == product.id).all()
            for rate in rates:
                db.session.delete(rate)
                db.session.commit()
            db.session.delete(product)
            db.session.commit()
        brands = Brand.query.filter(Brand.category_id == id).all()
        for brand in brands:
            db.session.delete(brand)
            db.session.commit()

        db.session.delete(category)
        db.session.commit()
        flash(f"The brand {category.name} was deleted from your database", "success")
        return redirect(url_for('categories'))
    flash(f"The brand {category.name} can't be  deleted from your database", "warning")
    return redirect(url_for('categories'))


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    form = Addproducts()
    brands = Brand.query.all()
    categories = Category.query.all()

    print(f"Request method: {request.method}")
    print(f"Request files: {request.files}")
    print(f"Request form data: {dict(request.form)}")

    if request.method == "POST":
        try:
            # Populate form with request data and files
            form = Addproducts(request.form)
            form.image_1.data = request.files.get('image_1')
            form.image_2.data = request.files.get('image_2')
            form.image_3.data = request.files.get('image_3')

            print(f"Form image_1 data: {form.image_1.data}")
            print(f"Form image_2 data: {form.image_2.data}")
            print(f"Form image_3 data: {form.image_3.data}")

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

                print(f"Form validation errors: {form.errors}")  # Log chi tiết
                print(f"Form data after validation: {form.data}")
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, user=user[0])
            
            name = form.name.data
            price = form.price.data
            discount = form.discount.data or 0
            stock = form.stock.data
            colors = form.colors.data
            desc = form.description.data
            brand = request.form.get('brand')
            category = request.form.get('category')

            print(f"Received data: name={name}, price={price}, discount={discount}, stock={stock}")
            print(f"Brand: {brand}, Category: {category}")

            # Additional server-side validation
            if price <= 0:
                flash('Giá sản phẩm phải lớn hơn 0', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, user=user[0])

            if discount < 0 or discount > 100:
                flash('Giảm giá phải nằm trong khoảng 0-100%', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, user=user[0])

            if stock < 0:
                flash('Số lượng tồn kho phải lớn hơn hoặc bằng 0', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, user=user[0])

            # Kiểm tra file ảnh
            image_1 = request.files.get('image_1')
            image_2 = request.files.get('image_2')
            image_3 = request.files.get('image_3')

            print(f"Image files: image_1={bool(image_1)}, image_2={bool(image_2)}, image_3={bool(image_3)}")
            print(f"Image filenames: {image_1.filename if image_1 else 'None'}, {image_2.filename if image_2 else 'None'}, {image_3.filename if image_3 else 'None'}")

            if not image_1 or not image_2 or not image_3:
                flash('Vui lòng chọn đầy đủ 3 ảnh cho sản phẩm', 'danger')
                print("Missing image files - validation failed")
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, user=user[0])

            name_random_1 = secrets.token_hex(10) + "."
            name_random_2 = secrets.token_hex(10) + "."
            name_random_3 = secrets.token_hex(10) + "."

            print(f"Generated random names: {name_random_1}, {name_random_2}, {name_random_3}")

            # Save in firebase database
            save_link_1 = "" + name_random_1 + image_1.filename.split('.')[-1]
            save_link_2 = "" + name_random_2 + image_2.filename.split('.')[-1]
            save_link_3 = "" + name_random_3 + image_3.filename.split('.')[-1]

            print(f"Save links: {save_link_1}, {save_link_2}, {save_link_3}")

            # save static/images
            try:
                print("Attempting to save images...")
                image_1 = photos.save(image_1, name=name_random_1)
                image_2 = photos.save(image_2, name=name_random_2)
                image_3 = photos.save(image_3, name=name_random_3)
                print(f"Images saved successfully: {image_1}, {image_2}, {image_3}")
            except Exception as img_error:
                print(f"Error saving images: {str(img_error)}")
                print(f"Error type: {type(img_error)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                flash(f'Lỗi khi lưu ảnh: {str(img_error)}', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, user=user[0])

            # Assuming 'storage' is defined elsewhere or needs to be imported
            # from firebase_admin import storage
            # storage = storage.bucket() # Assuming 'storage' is a bucket object

            # storage.child("images/" + save_link_1).put(os.path.join(current_app.root_path, "static/images/" + save_link_1))
            # storage.child("images/" + save_link_2).put(os.path.join(current_app.root_path, "static/images/" + save_link_2))
            # storage.child("images/" + save_link_3).put(os.path.join(current_app.root_path, "static/images/" + save_link_3))

            print("Creating product object...")
            try:
                product = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors, desc=desc,
                                     category_id=category, brand_id=brand, image_1=image_1, image_2=image_2, image_3=image_3)
                print(f"Product object created: {product}")
                print(f"Product attributes: name={product.name}, price={product.price}, category_id={product.category_id}, brand_id={product.brand_id}")

                print("Adding product to database session...")
                db.session.add(product)

                print("Committing to database...")
                db.session.commit()
                print(f"Product successfully committed with ID: {product.id}")

                flash(f'Sản phẩm {product.name} đã được thêm thành công vào cơ sở dữ liệu', 'success')
                return redirect(url_for('addproduct'))

            except Exception as db_error:
                print(f"Database error: {str(db_error)}")
                print(f"Error type: {type(db_error)}")
                import traceback
                print(f"Database traceback: {traceback.format_exc()}")
                raise  # Re-raise để catch block bên ngoài xử lý
            
        except Exception as e:
            # Rollback session nếu có lỗi
            db.session.rollback()
            flash(f'Lỗi khi thêm sản phẩm: {str(e)}', 'danger')
            print(f"Error adding product: {str(e)}")  # Log lỗi để debug
            user = Admin.query.filter_by(email=session['email']).all()
            return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                   categories=categories, user=user[0])
    
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                           categories=categories, user=user[0])


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))

    # bucket.child('images').delete("30d516e59ed7deb97ed8.png")
    form = Addproducts(request.form)
    product = Addproduct.query.get_or_404(id)
    brands = Brand.query.all()
    categories = Category.query.all()
    brand = request.form.get('brand')
    category = request.form.get('category')

    if request.method == "POST":
        try:
            product.name = form.name.data
            product.price = form.price.data
            product.discount = form.discount.data
            product.stock = form.stock.data
            product.colors = form.colors.data
            product.desc = form.description.data
            product.category_id = category
            product.brand_id = brand
            
            if request.files.get('image_1'):
                image_1 = request.files.get('image_1')
                name_random_1 = secrets.token_hex(10) + "."
                save_link_1 = "" + name_random_1 + image_1.filename.split('.')[-1]
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                    # Assuming 'storage' is defined elsewhere or needs to be imported
                    # from firebase_admin import storage
                    # storage = storage.bucket() # Assuming 'storage' is a bucket object
                    # storage.delete("images/" + product.image_1)
                    product.image_1 = photos.save(image_1, name=name_random_1)
                    # storage.child("images/" + save_link_1).put(
                    #     os.path.join(current_app.root_path, "static/images/" + save_link_1))
                except Exception as img_error:
                    flash(f'Lỗi khi cập nhật ảnh 1: {str(img_error)}', 'warning')
                    product.image_1 = photos.save(image_1, name=name_random_1)
                    # storage.child("images/" + save_link_1).put(
                    #     os.path.join(current_app.root_path, "static/images/" + save_link_1))
            
            if request.files.get('image_2'):
                image_2 = request.files.get('image_2')
                name_random_2 = secrets.token_hex(10) + "."
                save_link_2 = "" + name_random_2 + image_2.filename.split('.')[-1]
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                    # Assuming 'storage' is defined elsewhere or needs to be imported
                    # from firebase_admin import storage
                    # storage = storage.bucket() # Assuming 'storage' is a bucket object
                    # storage.delete("images/" + product.image_2)
                    product.image_2 = photos.save(image_2, name=name_random_2)
                    # storage.child("images/" + save_link_2).put(
                    #     os.path.join(current_app.root_path, "static/images/" + save_link_2))
                except Exception as img_error:
                    flash(f'Lỗi khi cập nhật ảnh 2: {str(img_error)}', 'warning')
                    product.image_2 = photos.save(image_2, name=name_random_2)
                    # storage.child("images/" + save_link_2).put(
                    #     os.path.join(current_app.root_path, "static/images/" + save_link_2))
            
            if request.files.get('image_3'):
                image_3 = request.files.get('image_3')
                name_random_3 = secrets.token_hex(10) + "."
                save_link_3 = "" + name_random_3 + image_3.filename.split('.')[-1]
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                    # Assuming 'storage' is defined elsewhere or needs to be imported
                    # from firebase_admin import storage
                    # storage = storage.bucket() # Assuming 'storage' is a bucket object
                    # storage.delete("images/" + product.image_3)
                    product.image_3 = photos.save(image_3, name=name_random_3)
                    # storage.child("images/" + save_link_3).put(
                    #     os.path.join(current_app.root_path, "static/images/" + save_link_3))
                except Exception as img_error:
                    flash(f'Lỗi khi cập nhật ảnh 3: {str(img_error)}', 'warning')
                    product.image_3 = photos.save(image_3, name=name_random_3)
                    # storage.child("images/" + save_link_3).put(
                    #     os.path.join(current_app.root_path, "static/images/" + save_link_3))
            
            db.session.commit()
            flash(f'Sản phẩm {product.name} đã được cập nhật thành công', 'success')
            return redirect(url_for('product'))
            
        except Exception as e:
            # Rollback session nếu có lỗi
            db.session.rollback()
            flash(f'Lỗi khi cập nhật sản phẩm: {str(e)}', 'danger')
            print(f"Error updating product: {str(e)}")  # Log lỗi để debug
            user = Admin.query.filter_by(email=session['email']).all()
            return render_template('products/updateproduct.html', form=form, product=product, title='Update Product', brands=brands,
                                   categories=categories, user=user[0])

    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.desc
    brand = product.brand.name
    category = product.category.name
    user = Admin.query.filter_by(email=session['email']).all()
    return render_template('products/updateproduct.html', form=form, title='Update Product', product=product,
                           brands=brands, categories=categories, user=user[0])


@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    if 'email' not in session:
        flash(f'Yêu cầu đăng nhập', 'danger')
        return redirect(url_for('login'))
    product = Addproduct.query.get_or_404(id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            print(e)
        rates = Rate.query.filter(Rate.product_id == id).all()
        for rate in rates:
            db.session.delete(rate)
            db.session.commit()
        db.session.delete(product)
        db.session.commit()
        flash(f'Sản phẩm {product.name} đã được xóa khỏi hệ thống', 'success')
        return redirect(url_for('product'))
    flash(f'Can not delete the product', 'success')
    return redirect(url_for('product'))


@app.route('/addrate', methods=['GET', 'POST'])
def addrate():
    form = Rates(request.form)
    products_hot = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.price.desc()).limit(3).all()
    products_new = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).all()
    products_sell = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.discount.desc()).limit(10).all()
    products = {'hot': products_hot, 'new': products_new, 'sell': products_sell, 'average': medium()}
    product_id = -1
    if request.method == "POST":
        register_id = request.form.get('register_id')
        product_id = request.form.get('product_id')
        desc = request.form.get('desc')
        rate_number = request.form.get('select')
        rate = Rate(register_id=register_id, product_id=product_id, desc=desc, rate_number=rate_number)
        db.session.add(rate)
        flash(f'The rate {register_id} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('detail', id=product_id))
        # return "OK this is a post method"
    rates = Rate.query.filter(Rate.product_id == product_id).order_by(Rate.id.desc()).all()
    product = Addproduct.query.get_or_404(product_id)
    return render_template('products/product.html', title='Add rate', form=form, products=products, rates=rates,
                           product=product, brands=brands(), registers=registers(), categories=categories())


@app.route('/detail/id_<int:id>')
def detail(id):
    kt = False
    customer = None
    if current_user.is_authenticated:
        customer = Register.query.get_or_404(current_user.id)
        rates = Rate.query.order_by(Rate.id.desc()).all()
        for rate in rates:
            if id == rate.product_id and customer.id == rate.register_id:
                kt = True
    form = Rates(request.form)
    rates = Rate.query.filter(Rate.product_id == id).order_by(Rate.id.desc()).all()
    products_hot = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.price.desc()).limit(3).all()
    products_new = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).limit(2).all()
    products_sell = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.discount.desc()).limit(10).all()
    products = {'hot': products_hot, 'new': products_new, 'sell': products_sell, 'average': medium()}
    product = Addproduct.query.get_or_404(id)
    # products = Addproduct.query.filter_by(id='id')
    return render_template('products/product.html', product=product, products=products, brands=brands(), form=form,
                           rates=rates, registers=registers(), categories=categories(), customer=customer, kt=kt)


@app.route('/category/discount/<int:start>-<int:end>')
def get_discount(start, end):
    page = request.args.get('page', 1, type=int)
    product_discount = Addproduct.query.filter(Addproduct.discount >= start, Addproduct.discount < end) \
        .order_by(Addproduct.id.desc()).paginate(page=page, per_page=9)
    products_new = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).limit(2).all()
    products = {'all': product_discount, 'new': products_new, 'average': medium()}
    return render_template('products/category.html', products=products, brands=brands(), categories=categories())


@app.route('/search', methods=['GET', 'POST'])
def search():
    value = request.form['search']
    search = "%{}%".format(value.lower())
    page = request.args.get('page', 1, type=int)
    product = Addproduct.query.filter(Addproduct.name.ilike(search)).paginate(page=page, per_page=9)
    products = {'all': product, 'average': medium()}
    return render_template('products/category.html', get_search=value, products=products, brands=brands(),
                           categories=categories())


@app.route('/test_db')
def test_db():
    try:
        # Test query to database
        brands = Brand.query.all()
        return f"Connected to database successfully! Found {len(brands)} brands."
    except Exception as e:
        return f"Database connection failed: {str(e)}"


def brands():
    # brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    brands = Brand.query.all()
    return brands


def categories():
    # categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    categories = Category.query.order_by(Category.name.desc()).all()
    return categories


def medium():
    # Calculate average rating for each product
    from shop.models import Rate
    from sqlalchemy import func
    
    # Get all products with their average ratings and count
    ratings = db.session.query(
        Rate.product_id,
        func.avg(Rate.rate_number).label('avg_rating'),
        func.count(Rate.id).label('count')
    ).group_by(Rate.product_id).all()
    
    # Create a dictionary with product_id as key and [avg_rating, count] as value
    rating_dict = {}
    for rating in ratings:
        rating_dict[rating.product_id] = [float(rating.avg_rating), rating.count]
    
    return rating_dict


def registers():
    # Get all registered users
    return Register.query.all()
