#!/usr/bin/env python3
"""
VNPAY Setup Test Script
This script helps you test your VNPAY configuration and provides setup instructions.
"""

import requests

def test_local_endpoints():
    """Test if local VNPAY endpoints are accessible"""
    print("=" * 60)
    print("TESTING LOCAL VNPAY ENDPOINTS")
    print("=" * 60)

    endpoints = [
        'http://localhost:5000/debug_vnpay',
        'http://localhost:5000/vnpay_return',
        'http://localhost:5000/vnpay_ipn'
    ]

    for endpoint in endpoints:
        try:
            print(f"\nTesting: {endpoint}")

            # Test GET request
            response = requests.get(endpoint, timeout=5)
            print(f"GET Status: {response.status_code}")

            # Test POST request for IPN
            if 'ipn' in endpoint:
                response = requests.post(endpoint, data={'test': 'data'}, timeout=5)
                print(f"POST Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
            print("💡 Make sure Flask app is running: python app.py")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def check_ngrok_setup():
    """Provide ngrok setup instructions"""
    print("\n" + "=" * 60)
    print("NGROK SETUP INSTRUCTIONS")
    print("=" * 60)

    print("📥 To install ngrok:")
    print("1. Go to: https://ngrok.com/download")
    print("2. Download and install ngrok for your OS")
    print("3. Add ngrok to your system PATH")
    print()
    print("🚀 To expose your local server:")
    print("1. Run: ngrok http 5000")
    print("2. Copy the HTTPS URL (e.g., https://abcd1234.ngrok.io)")
    print("3. Update VNPAY_RETURN_URL and VNPAY_IPN_URL in shop/__init__.py")
    print("4. Restart your Flask app")

def main():
    """Main test function"""
    print("🔧 VNPAY SETUP TEST")
    print("This script will help you verify your VNPAY integration setup.\n")

    # Test local endpoints
    test_local_endpoints()

    # Check ngrok setup
    check_ngrok_setup()

    print("\n" + "=" * 60)
    print("📋 NEXT STEPS")
    print("=" * 60)

    print("\n1. ✅ Make sure Flask app is running")
    print("2. ✅ Install ngrok if not already installed")
    print("3. 🚀 Run: ngrok http 5000")
    print("4. 🔧 Update VNPAY URLs in shop/__init__.py with ngrok URL")
    print("5. 🔄 Restart Flask app")
    print("6. 🧪 Test VNPAY payment flow")

    print("\n" + "=" * 60)
    print("💡 VNPAY CONFIGURATION EXAMPLE")
    print("=" * 60)

    print("""
# After running 'ngrok http 5000', update these in shop/__init__.py:

app.config['VNPAY_RETURN_URL'] = 'https://abcd1234.ngrok.io/vnpay_return'
app.config['VNPAY_IPN_URL'] = 'https://abcd1234.ngrok.io/vnpay_ipn'

# Replace 'abcd1234' with your actual ngrok subdomain
""")

if __name__ == "__main__":
    main()
