import requests
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def test_mpesa_credentials():
    """Test if M-Pesa credentials are working"""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    
    print("=" * 50)
    print("M-PESA CREDENTIALS TEST")
    print("=" * 50)
    
    print(f"Consumer Key: {consumer_key}")
    print(f"Consumer Secret: {consumer_secret[:10]}...")  # Show first 10 chars for security
    
    # Test access token
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    print(f"\nTesting access token request...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, auth=(consumer_key, consumer_secret), timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS: Access token obtained!")
            print(f"Access Token: {data.get('access_token', 'None')}")
            print(f"Token Type: {data.get('token_type', 'None')}")
            print(f"Expires In: {data.get('expires_in', 'None')} seconds")
        else:
            print("\n❌ FAILED: Could not get access token")
            print(f"Error Details: {response.text}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

def test_environment_variables():
    """Test if environment variables are loaded correctly"""
    print("\n" + "=" * 50)
    print("ENVIRONMENT VARIABLES TEST")
    print("=" * 50)
    
    variables = [
        'MPESA_CONSUMER_KEY',
        'MPESA_CONSUMER_SECRET', 
        'MPESA_BUSINESS_SHORTCODE',
        'MPESA_PASSKEY',
        'MPESA_CALLBACK_URL'
    ]
    
    for var in variables:
        value = getattr(settings, var, 'NOT SET')
        if value and var in ['MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET']:
            print(f"{var}: {value[:10]}... (hidden for security)")
        else:
            print(f"{var}: {value}")

if __name__ == "__main__":
    test_environment_variables()
    test_mpesa_credentials()
