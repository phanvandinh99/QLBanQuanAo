import urllib
import os
import secrets
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import current_user
from shop import app, db, photos
from shop.models import Brand, Category, Product, Rating, Customer, Admin, Article
from .forms import Rates, Addproducts

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter(Product.stock > 0).paginate(page=page, per_page=8)

    # Get published articles for the articles section
    articles = Article.query.filter_by(status='published').order_by(Article.created_at.desc()).limit(3).all()

    return render_template('products/index.html', products=products, articles=articles, categories=categories(), brands=brands())


@app.route('/category')
def get_all_category():
    page = request.args.get('page', 1, type=int)
    products_all = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).paginate(page=page,
                                                                                                         per_page=9)
    products_new = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).limit(2).all()
    products = {'all': products_all, 'new': products_new, 'average': medium()}
    return render_template('products/category.html', products=products, brands=brands(), categories=categories())


@app.route('/category/brand/<string:name>')
def get_brand(name):
    page = request.args.get('page', 1, type=int)
    get_brand = Brand.query.filter_by(name=name).first_or_404()
    brand = Product.query.filter_by(brand=get_brand).paginate(page=page, per_page=9)

    products_new = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).limit(2).all()
    products = {'all': brand, 'new': products_new, 'average': medium()}
    return render_template('products/category.html', products=products, brand=name, brands=brands(),
                           categories=categories(),
                           get_brand=get_brand)


@app.route('/categories/<string:name>')
def get_category(name):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(name=name).first_or_404()
    get_cat_prod = Product.query.filter_by(category=get_cat).paginate(page=page, per_page=9)
    products_new = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).limit(2).all()
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
        products = Product.query.filter(Product.category_id == id).all()
        for product in products:
            rates = Rating.query.filter(Rating.product_id == product.id).all()
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
        products = Product.query.filter(Product.category_id == id).all()
        for product in products:
            rates = Rating.query.filter(Rating.product_id == product.id).all()
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
                                       categories=categories, user=user[0])
            
            name = form.name.data
            price = form.price.data
            discount = form.discount.data or 0
            stock = form.stock.data
            colors = form.colors.data
            desc = form.description.data
            brand = request.form.get('brand')
            category = request.form.get('category')


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

            if not image_1 or not image_2 or not image_3:
                flash('Vui lòng chọn đầy đủ 3 ảnh cho sản phẩm', 'danger')
                user = Admin.query.filter_by(email=session['email']).all()
                return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                                       categories=categories, user=user[0])

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
                                       categories=categories, user=user[0])

            try:
                product = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors, desc=desc,
                                     category_id=category, brand_id=brand, image_1=image_1, image_2=image_2, image_3=image_3)
                db.session.add(product)
                db.session.commit()

                flash(f'Sản phẩm {product.name} đã được thêm thành công vào cơ sở dữ liệu', 'success')
                return redirect(url_for('addproduct'))

            except Exception as db_error:
                raise  # Re-raise để catch block bên ngoài xử lý
            
        except Exception as e:
            # Rollback session nếu có lỗi
            db.session.rollback()
            flash(f'Lỗi khi thêm sản phẩm: {str(e)}', 'danger')
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

    form = Addproducts(request.form)
    product = Product.query.get_or_404(id)
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
                    product.image_1 = photos.save(image_1, name=name_random_1)
                except Exception as img_error:
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
                    flash(f'Lỗi khi cập nhật ảnh 3: {str(img_error)}', 'warning')
                    product.image_3 = photos.save(image_3, name=name_random_3)
            
            db.session.commit()
            flash(f'Sản phẩm {product.name} đã được cập nhật thành công', 'success')
            return redirect(url_for('product'))
            
        except Exception:
            # Rollback session nếu có lỗi
            db.session.rollback()
            flash(f'Lỗi khi cập nhật sản phẩm: {str(e)}', 'danger')
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
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception:
            pass
        rates = Rating.query.filter(Rating.product_id == id).all()
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
    products_hot = Product.query.filter(Product.stock > 0).order_by(Product.price.desc()).limit(3).all()
    products_new = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).all()
    products_sell = Product.query.filter(Product.stock > 0).order_by(Product.discount.desc()).limit(10).all()
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
    products_hot = Product.query.filter(Product.stock > 0).order_by(Product.price.desc()).limit(3).all()
    products_new = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).limit(2).all()
    products_sell = Product.query.filter(Product.stock > 0).order_by(Product.discount.desc()).limit(10).all()
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
    products_new = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).limit(2).all()
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
