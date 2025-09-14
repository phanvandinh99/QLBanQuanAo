#!/usr/bin/env python3
"""
Script để debug VNPAY payment step by step
"""

from shop import app, db
from shop.models import CustomerOrder, Register
from flask import session
import json
import secrets

def debug_vnpay():
    """Debug VNPAY payment process step by step"""
    with app.app_context():
        print("=" * 80)
        print("DEBUGGING VNPAY PAYMENT PROCESS")
        print("=" * 80)

        # Step 1: Check user
        user = Register.query.filter_by(email='Hoang@gmail.com').first()
        if not user:
            print("❌ User not found!")
            return

        print(f"✅ User found: ID={user.id}, Email={user.email}")

        # Step 2: Simulate shopping cart
        test_cart = {
            '1': {
                'name': 'Test Product',
                'price': 100000.0,
                'discount': 10,
                'color': 'Black',
                'quantity': 1,
                'image': 'test.jpg',
                'colors': 'Black,White',
                'brand': 'Test Brand'
            }
        }

        print(f"✅ Test cart created: {len(test_cart)} items")

        # Step 3: Calculate amounts
        subtotals = 0
        discounttotal = 0
        for key, product in test_cart.items():
            discounttotal += (product.get('discount', 0) / 100) * float(product['price']) * int(product['quantity'])
            subtotals += float(product['price']) * int(product['quantity'])

        final_amount = int(subtotals - discounttotal)
        print(f"✅ Amount calculation: subtotals={subtotals}, discount={discounttotal}, final={final_amount}")

        # Step 4: Generate invoice
        invoice = secrets.token_hex(5)
        customer_id = user.id
        customer_address = '123 Test Street, Hanoi'

        print(f"✅ Invoice generated: {invoice}")

        # Step 5: Create order
        print("\n--- STEP 5: Creating Order ---")
        try:
            new_order = CustomerOrder(
                invoice=invoice,
                customer_id=customer_id,
                orders=json.dumps(test_cart),
                status="Chờ thanh toán",
                address=customer_address,
                amount=final_amount,
                payment_method='vnpay'
            )
            db.session.add(new_order)
            db.session.commit()
            print(f"✅ Order created: ID={new_order.id}, Invoice={invoice}, Status={new_order.status}")
        except Exception as e:
            print(f"❌ ERROR creating order: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return

        # Step 6: Simulate VNPAY return success
        print("\n--- STEP 6: Simulating VNPAY Success Return ---")

        # Find order by invoice
        try:
            found_order = CustomerOrder.query.filter_by(invoice=invoice).first()
            if found_order:
                print(f"✅ Order found for update: ID={found_order.id}, Current Status={found_order.status}")

                # Update status
                found_order.status = 'Đã thanh toán'
                db.session.commit()
                print(f"✅ Order updated to: Status={found_order.status}")

                # Verify
                verify_order = CustomerOrder.query.filter_by(invoice=invoice).first()
                print(f"✅ Verification: Status={verify_order.status}")

            else:
                print(f"❌ Order not found for invoice: {invoice}")
                all_orders = CustomerOrder.query.order_by(CustomerOrder.id.desc()).limit(5).all()
                print("Recent orders:")
                for o in all_orders:
                    print(f"  ID: {o.id}, Invoice: {o.invoice}, Status: {o.status}")

        except Exception as e:
            print(f"❌ ERROR updating order: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 80)
        print("DEBUGGING COMPLETED")
        print("=" * 80)

if __name__ == "__main__":
    debug_vnpay()
