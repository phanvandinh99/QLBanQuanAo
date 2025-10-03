"""
Routes for managing product variants (size, color, stock)
"""
import os
from flask import render_template, session, request, redirect, url_for, flash, jsonify
from shop import app, db
from shop.models import (Product, ProductVariant, Size, Color, StockMovement, 
                        Admin, Purchase, PurchaseItem)
from shop.products.forms import ProductVariantForm, SizeForm, ColorForm
from shop.admin.forms import PurchaseItemVariantForm, VariantStockAdjustmentForm, BulkVariantForm
from shop.admin_decorators import admin_required, role_required, get_current_admin
from sqlalchemy import func, desc
from datetime import datetime


# ================= SIZE MANAGEMENT =================

@app.route('/admin/sizes')
@admin_required
def sizes_list():
    """Manage product sizes"""
    user = get_current_admin()
    sizes = Size.query.order_by(Size.sort_order, Size.name).all()
    return render_template('admin/sizes/index.html', 
                         title='Quản lý kích thước', 
                         user=user, 
                         sizes=sizes)


@app.route('/admin/sizes/add', methods=['GET', 'POST'])
@admin_required
def add_size():
    """Add new size"""
    user = get_current_admin()
    form = SizeForm()
    
    if form.validate_on_submit():
        # Check if size name already exists
        existing_size = Size.query.filter_by(name=form.name.data).first()
        if existing_size:
            flash('Tên size đã tồn tại!', 'danger')
            return render_template('admin/sizes/add.html', form=form, user=user)
        
        try:
            size = Size(
                name=form.name.data,
                display_name=form.display_name.data,
                sort_order=form.sort_order.data
            )
            db.session.add(size)
            db.session.commit()
            flash(f'Đã thêm size "{form.name.data}" thành công!', 'success')
            return redirect(url_for('sizes_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm size: {str(e)}', 'danger')
    
    return render_template('admin/sizes/add.html', form=form, user=user)


@app.route('/admin/sizes/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_size(id):
    """Edit size"""
    user = get_current_admin()
    size = Size.query.get_or_404(id)
    form = SizeForm(obj=size)
    
    if form.validate_on_submit():
        # Check if size name already exists (excluding current size)
        existing_size = Size.query.filter(Size.name == form.name.data, Size.id != id).first()
        if existing_size:
            flash('Tên size đã tồn tại!', 'danger')
            return render_template('admin/sizes/edit.html', form=form, user=user, size=size)
        
        try:
            size.name = form.name.data
            size.display_name = form.display_name.data
            size.sort_order = form.sort_order.data
            db.session.commit()
            flash(f'Đã cập nhật size "{size.name}" thành công!', 'success')
            return redirect(url_for('sizes_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật size: {str(e)}', 'danger')
    
    return render_template('admin/sizes/edit.html', form=form, user=user, size=size)


@app.route('/admin/sizes/delete/<int:id>', methods=['POST'])
@admin_required
def delete_size(id):
    """Delete size"""
    size = Size.query.get_or_404(id)
    
    # Check if size is being used by any variants
    variant_count = ProductVariant.query.filter_by(size_id=id).count()
    if variant_count > 0:
        flash(f'Không thể xóa size "{size.name}" vì đang được sử dụng bởi {variant_count} biến thể sản phẩm!', 'danger')
        return redirect(url_for('sizes_list'))
    
    try:
        db.session.delete(size)
        db.session.commit()
        flash(f'Đã xóa size "{size.name}" thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa size: {str(e)}', 'danger')
    
    return redirect(url_for('sizes_list'))


# ================= COLOR MANAGEMENT =================

@app.route('/admin/colors')
@admin_required
def colors_list():
    """Manage product colors"""
    user = get_current_admin()
    colors = Color.query.order_by(Color.name).all()
    return render_template('admin/colors/index.html', 
                         title='Quản lý màu sắc', 
                         user=user, 
                         colors=colors)


@app.route('/admin/colors/add', methods=['GET', 'POST'])
@admin_required
def add_color():
    """Add new color"""
    user = get_current_admin()
    form = ColorForm()
    
    if form.validate_on_submit():
        # Check if color name already exists
        existing_color = Color.query.filter_by(name=form.name.data).first()
        if existing_color:
            flash('Tên màu đã tồn tại!', 'danger')
            return render_template('admin/colors/add.html', form=form, user=user)
        
        try:
            color = Color(
                name=form.name.data,
                hex_code=form.hex_code.data if form.hex_code.data else None
            )
            db.session.add(color)
            db.session.commit()
            flash(f'Đã thêm màu "{form.name.data}" thành công!', 'success')
            return redirect(url_for('colors_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm màu: {str(e)}', 'danger')
    
    return render_template('admin/colors/add.html', form=form, user=user)


@app.route('/admin/colors/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_color(id):
    """Edit color"""
    user = get_current_admin()
    color = Color.query.get_or_404(id)
    form = ColorForm(obj=color)
    
    if form.validate_on_submit():
        # Check if color name already exists (excluding current color)
        existing_color = Color.query.filter(Color.name == form.name.data, Color.id != id).first()
        if existing_color:
            flash('Tên màu đã tồn tại!', 'danger')
            return render_template('admin/colors/edit.html', form=form, user=user, color=color)
        
        try:
            color.name = form.name.data
            color.hex_code = form.hex_code.data if form.hex_code.data else None
            db.session.commit()
            flash(f'Đã cập nhật màu "{color.name}" thành công!', 'success')
            return redirect(url_for('colors_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật màu: {str(e)}', 'danger')
    
    return render_template('admin/colors/edit.html', form=form, user=user, color=color)


@app.route('/admin/colors/delete/<int:id>', methods=['POST'])
@admin_required
def delete_color(id):
    """Delete color"""
    color = Color.query.get_or_404(id)
    
    # Check if color is being used by any variants
    variant_count = ProductVariant.query.filter_by(color_id=id).count()
    if variant_count > 0:
        flash(f'Không thể xóa màu "{color.name}" vì đang được sử dụng bởi {variant_count} biến thể sản phẩm!', 'danger')
        return redirect(url_for('colors_list'))
    
    try:
        db.session.delete(color)
        db.session.commit()
        flash(f'Đã xóa màu "{color.name}" thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa màu: {str(e)}', 'danger')
    
    return redirect(url_for('colors_list'))


# ================= PRODUCT VARIANT MANAGEMENT =================

@app.route('/admin/products/<int:product_id>/variants')
@admin_required
def manage_product_variants(product_id):
    """Manage variants for a specific product"""
    user = get_current_admin()
    product = Product.query.get_or_404(product_id)
    variants = ProductVariant.query.filter_by(product_id=product_id).order_by(
        ProductVariant.is_active.desc(),
        ProductVariant.created_at.desc()
    ).all()
    
    return render_template('admin/variants/index.html', 
                         title=f'Quản lý biến thể - {product.name}', 
                         user=user, 
                         product=product,
                         variants=variants)


@app.route('/admin/products/<int:product_id>/variants/add', methods=['GET', 'POST'])
@admin_required
def add_product_variant(product_id):
    """Add new variant to product"""
    user = get_current_admin()
    product = Product.query.get_or_404(product_id)
    form = ProductVariantForm()
    
    if form.validate_on_submit():
        size_id = form.size_id.data if form.size_id.data != 0 else None
        color_id = form.color_id.data if form.color_id.data != 0 else None
        
        # Check if variant combination already exists
        existing_variant = ProductVariant.query.filter_by(
            product_id=product_id,
            size_id=size_id,
            color_id=color_id
        ).first()
        
        if existing_variant:
            flash('Biến thể với kích thước và màu sắc này đã tồn tại!', 'danger')
            return render_template('admin/variants/add.html', form=form, user=user, product=product)
        
        try:
            variant = ProductVariant(
                product_id=product_id,
                size_id=size_id,
                color_id=color_id,
                price=form.price.data,
                stock=form.stock.data,
                is_active=form.is_active.data
            )
            
            # Generate SKU if not provided
            if form.sku.data:
                variant.sku = form.sku.data
            else:
                variant.sku = variant.generate_sku()
            
            db.session.add(variant)
            
            # Update product to use variants
            if not product.has_variants:
                product.has_variants = True
            
            db.session.commit()
            
            # Create stock movement record
            if form.stock.data > 0:
                stock_movement = StockMovement(
                    product_variant_id=variant.id,
                    movement_type='in',
                    quantity=form.stock.data,
                    reference_type='adjustment',
                    notes='Tạo biến thể mới',
                    admin_id=user.id
                )
                db.session.add(stock_movement)
                db.session.commit()
            
            flash(f'Đã thêm biến thể thành công!', 'success')
            return redirect(url_for('manage_product_variants', product_id=product_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm biến thể: {str(e)}', 'danger')
    
    return render_template('admin/variants/add.html', form=form, user=user, product=product)


@app.route('/admin/variants/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product_variant(id):
    """Edit product variant"""
    user = get_current_admin()
    variant = ProductVariant.query.get_or_404(id)
    product = variant.product
    
    form = ProductVariantForm(obj=variant)
    # Set form values for select fields
    form.size_id.data = variant.size_id if variant.size_id else 0
    form.color_id.data = variant.color_id if variant.color_id else 0
    
    if form.validate_on_submit():
        size_id = form.size_id.data if form.size_id.data != 0 else None
        color_id = form.color_id.data if form.color_id.data != 0 else None
        
        # Check if variant combination already exists (excluding current variant)
        existing_variant = ProductVariant.query.filter(
            ProductVariant.product_id == variant.product_id,
            ProductVariant.size_id == size_id,
            ProductVariant.color_id == color_id,
            ProductVariant.id != id
        ).first()
        
        if existing_variant:
            flash('Biến thể với kích thước và màu sắc này đã tồn tại!', 'danger')
            return render_template('admin/variants/edit.html', form=form, user=user, variant=variant, product=product)
        
        try:
            old_stock = variant.stock
            
            variant.size_id = size_id
            variant.color_id = color_id
            variant.price = form.price.data
            variant.stock = form.stock.data
            variant.is_active = form.is_active.data
            variant.updated_at = datetime.utcnow()
            
            if form.sku.data:
                variant.sku = form.sku.data
            
            db.session.commit()
            
            # Create stock movement record if stock changed
            stock_diff = form.stock.data - old_stock
            if stock_diff != 0:
                movement_type = 'in' if stock_diff > 0 else 'out'
                stock_movement = StockMovement(
                    product_variant_id=variant.id,
                    movement_type=movement_type,
                    quantity=abs(stock_diff),
                    reference_type='adjustment',
                    notes=f'Cập nhật biến thể: {old_stock} → {form.stock.data}',
                    admin_id=user.id
                )
                db.session.add(stock_movement)
                db.session.commit()
            
            flash(f'Đã cập nhật biến thể thành công!', 'success')
            return redirect(url_for('manage_product_variants', product_id=variant.product_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật biến thể: {str(e)}', 'danger')
    
    return render_template('admin/variants/edit.html', form=form, user=user, variant=variant, product=product)


@app.route('/admin/variants/<int:id>/delete', methods=['POST'])
@admin_required
def delete_product_variant(id):
    """Delete product variant"""
    variant = ProductVariant.query.get_or_404(id)
    product_id = variant.product_id
    
    # Check if variant is being used in orders
    order_count = variant.order_items.count()
    if order_count > 0:
        flash(f'Không thể xóa biến thể vì đã được sử dụng trong {order_count} đơn hàng!', 'danger')
        return redirect(url_for('manage_product_variants', product_id=product_id))
    
    try:
        # Delete related stock movements
        StockMovement.query.filter_by(product_variant_id=id).delete()
        
        db.session.delete(variant)
        db.session.commit()
        flash('Đã xóa biến thể thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa biến thể: {str(e)}', 'danger')
    
    return redirect(url_for('manage_product_variants', product_id=product_id))


# ================= STOCK MANAGEMENT =================

@app.route('/admin/stock/variants')
@admin_required
def variant_stock_overview():
    """Overview of all variant stock levels"""
    user = get_current_admin()
    
    # Get variants with low stock (less than 10)
    low_stock_variants = ProductVariant.query.join(Product).filter(
        ProductVariant.is_active == True,
        ProductVariant.stock < 10
    ).order_by(ProductVariant.stock.asc()).all()
    
    # Get variants with no stock
    out_of_stock_variants = ProductVariant.query.join(Product).filter(
        ProductVariant.is_active == True,
        ProductVariant.stock == 0
    ).all()
    
    # Get all variants for general overview
    page = request.args.get('page', 1, type=int)
    variants = ProductVariant.query.join(Product).filter(
        ProductVariant.is_active == True
    ).order_by(Product.name, ProductVariant.created_at).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/stock/variants_overview.html',
                         title='Tổng quan tồn kho biến thể',
                         user=user,
                         variants=variants,
                         low_stock_variants=low_stock_variants,
                         out_of_stock_variants=out_of_stock_variants)


@app.route('/admin/stock/adjust', methods=['GET', 'POST'])
@admin_required
def adjust_variant_stock():
    """Adjust variant stock"""
    user = get_current_admin()
    form = VariantStockAdjustmentForm()
    
    if form.validate_on_submit():
        variant = ProductVariant.query.get_or_404(form.product_variant_id.data)
        
        try:
            old_stock = variant.stock
            adjustment_type = form.adjustment_type.data
            quantity = form.quantity.data
            
            if adjustment_type == 'increase':
                new_stock = old_stock + quantity
                movement_type = 'in'
                movement_quantity = quantity
            elif adjustment_type == 'decrease':
                new_stock = max(0, old_stock - quantity)
                movement_type = 'out'
                movement_quantity = min(quantity, old_stock)
            else:  # set
                new_stock = quantity
                if new_stock > old_stock:
                    movement_type = 'in'
                    movement_quantity = new_stock - old_stock
                else:
                    movement_type = 'out'
                    movement_quantity = old_stock - new_stock
            
            variant.stock = new_stock
            variant.updated_at = datetime.utcnow()
            
            # Create stock movement record
            if movement_quantity > 0:
                stock_movement = StockMovement(
                    product_variant_id=variant.id,
                    movement_type=movement_type,
                    quantity=movement_quantity,
                    reference_type='adjustment',
                    notes=form.notes.data or f'Điều chỉnh tồn kho: {old_stock} → {new_stock}',
                    admin_id=user.id
                )
                db.session.add(stock_movement)
            
            db.session.commit()
            flash(f'Đã điều chỉnh tồn kho thành công! {old_stock} → {new_stock}', 'success')
            return redirect(url_for('variant_stock_overview'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi điều chỉnh tồn kho: {str(e)}', 'danger')
    
    return render_template('admin/stock/adjust.html', form=form, user=user)


# ================= AJAX ENDPOINTS =================

@app.route('/admin/api/products/<int:product_id>/variants')
@admin_required
def get_product_variants_api(product_id):
    """Get variants for a product (AJAX endpoint)"""
    variants = ProductVariant.query.filter_by(
        product_id=product_id, 
        is_active=True
    ).all()
    
    return jsonify([{
        'id': variant.id,
        'display_name': variant.display_name,
        'price': float(variant.price),
        'stock': variant.stock,
        'sku': variant.sku
    } for variant in variants])


@app.route('/admin/api/all-products-with-variants')
@admin_required
def get_all_products_with_variants_api():
    """Get all products with their variants (AJAX endpoint)"""
    try:
        # Get all products with variants
        products = Product.query.filter(Product.variants.any()).all()
        
        all_variants = []
        for product in products:
            variants = ProductVariant.query.filter_by(
                product_id=product.id,
                is_active=True
            ).join(Size, isouter=True).join(Color, isouter=True).all()
            
            for variant in variants:
                all_variants.append({
                    'id': variant.id,
                    'product_id': variant.product_id,
                    'product_name': product.name,
                    'size_id': variant.size_id,
                    'size_name': variant.size.name if variant.size else 'No Size',
                    'color_id': variant.color_id,
                    'color_name': variant.color.name if variant.color else 'No Color',
                    'price': float(variant.price),
                    'stock': variant.stock,
                    'sku': variant.sku or '',
                    'display_name': variant.display_name
                })
        
        return jsonify({
            'success': True,
            'variants': all_variants,
            'total': len(all_variants)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-variants')
def get_test_variants_api():
    """Test API endpoint without authentication"""
    try:
        # Get all products with variants
        products = Product.query.filter(Product.variants.any()).all()
        
        all_variants = []
        for product in products:
            variants = ProductVariant.query.filter_by(
                product_id=product.id,
                is_active=True
            ).join(Size, isouter=True).join(Color, isouter=True).all()
            
            for variant in variants:
                all_variants.append({
                    'id': variant.id,
                    'product_id': variant.product_id,
                    'product_name': product.name,
                    'size_id': variant.size_id,
                    'size_name': variant.size.name if variant.size else 'No Size',
                    'color_id': variant.color_id,
                    'color_name': variant.color.name if variant.color else 'No Color',
                    'price': float(variant.price),
                    'stock': variant.stock,
                    'sku': variant.sku or '',
                    'display_name': variant.display_name
                })
        
        return jsonify({
            'success': True,
            'variants': all_variants,
            'total': len(all_variants)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/admin/api/variants/<int:variant_id>')
@admin_required
def get_variant_details_api(variant_id):
    """Get variant details (AJAX endpoint)"""
    variant = ProductVariant.query.get_or_404(variant_id)
    
    return jsonify({
        'id': variant.id,
        'product_id': variant.product_id,
        'product_name': variant.product.name,
        'size_name': variant.size.name if variant.size else None,
        'color_name': variant.color.name if variant.color else None,
        'display_name': variant.display_name,
        'price': float(variant.price),
        'stock': variant.stock,
        'sku': variant.sku,
        'is_active': variant.is_active
    })


# ================= STOCK MOVEMENT HISTORY =================

@app.route('/admin/stock/movements')
@admin_required
def stock_movements():
    """View stock movement history"""
    user = get_current_admin()
    page = request.args.get('page', 1, type=int)
    
    movements = StockMovement.query.join(ProductVariant).join(Product).order_by(
        StockMovement.created_at.desc()
    ).paginate(page=page, per_page=50, error_out=False)
    
    return render_template('admin/stock/movements.html',
                         title='Lịch sử xuất nhập kho',
                         user=user,
                         movements=movements)


@app.route('/admin/stock/movements/<int:variant_id>')
@admin_required
def variant_stock_movements(variant_id):
    """View stock movements for specific variant"""
    user = get_current_admin()
    variant = ProductVariant.query.get_or_404(variant_id)
    page = request.args.get('page', 1, type=int)
    
    movements = StockMovement.query.filter_by(
        product_variant_id=variant_id
    ).order_by(StockMovement.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/stock/variant_movements.html',
                         title=f'Lịch sử xuất nhập - {variant.display_name}',
                         user=user,
                         variant=variant,
                         movements=movements)
