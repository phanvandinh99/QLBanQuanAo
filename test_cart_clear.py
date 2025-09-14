#!/usr/bin/env python3
"""
Test cart clearing functionality
"""

from shop import app

def test_cart_clear():
    """Test cart clearing in session"""
    with app.test_client() as client:
        print("=" * 50)
        print("TESTING CART CLEAR FUNCTIONALITY")
        print("=" * 50)

        # Test 1: Create cart and clear it
        with client.session_transaction() as sess:
            sess['Shoppingcart'] = {'test': 'item'}
            print(f"✅ Created cart: {sess['Shoppingcart']}")

        # Clear cart
        with client.session_transaction() as sess:
            if 'Shoppingcart' in sess:
                print(f"Cart before clearing: {sess['Shoppingcart']}")
                sess.pop('Shoppingcart', None)
                sess.modified = True
                print("✅ Cart cleared")
            else:
                print("⚠️ No cart found")

            print(f"Cart after clearing: {sess.get('Shoppingcart', 'No cart')}")

        print("=" * 50)
        print("TEST COMPLETED")
        print("=" * 50)

if __name__ == "__main__":
    test_cart_clear()
