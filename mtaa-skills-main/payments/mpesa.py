import requests
import base64
from datetime import datetime
import json
from django.conf import settings

class MpesaGateway:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.business_shortcode = settings.MPESA_BUSINESS_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        
    def get_access_token(self):
        """Get M-Pesa API access token"""
        try:
            url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                print(f"✅ Access token obtained: {access_token[:20]}...")
                return access_token
            else:
                print(f"❌ Failed to get access token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting access token: {e}")
            return None
    
    def get_encoded_password(self):
        """Generate encoded password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data = f"{self.business_shortcode}{self.passkey}{timestamp}"
        encoded = base64.b64encode(data.encode()).decode()
        return encoded, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK push payment"""
        # Get access token
        access_token = self.get_access_token()
        if not access_token:
            return {'error': 'Unable to get access token'}
        
        # Generate password and timestamp
        password, timestamp = self.get_encoded_password()
        
        # Format phone number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]
        elif len(phone_number) == 9:
            phone_number = '254' + phone_number
        
        # Prepare payload - CORRECT FORMAT for M-Pesa
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),  # Must be integer
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🔧 STK Push Details:")
        print(f"   URL: https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest")
        print(f"   Phone: {phone_number}")
        print(f"   Amount: {amount}")
        print(f"   Headers: {headers}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            # Make the STK Push request
            url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            print(f"📡 STK Push Response:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ STK Push initiated successfully!")
                return result
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ STK Push failed: {error_msg}")
                return {'error': error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ STK Push error: {error_msg}")
            return {'error': error_msg}
