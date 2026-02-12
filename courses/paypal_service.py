"""
PayPal Payment Service
Handles PayPal payment creation, execution, and verification
"""

import paypalrestsdk
from django.conf import settings


paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


def create_payment(amount, currency, return_url, cancel_url, description):
    """
    Create a PayPal payment
    
    Args:
        amount: Payment amount (Decimal)
        currency: Currency code (e.g., 'USD', 'INR')
        return_url: URL to return after successful payment
        cancel_url: URL to return if payment is cancelled
        description: Payment description
    
    Returns:
        dict: {'success': bool, 'payment_id': str, 'approval_url': str, 'error': str}
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": currency
            },
            "description": description
        }]
    })

    if payment.create():
        approval_url = None
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                break
        
        return {
            'success': True,
            'payment_id': payment.id,
            'approval_url': approval_url,
            'error': None
        }
    else:
        return {
            'success': False,
            'payment_id': None,
            'approval_url': None,
            'error': str(payment.error)
        }


def execute_payment(payment_id, payer_id):
    """
    Execute a PayPal payment after user approval
    
    Args:
        payment_id: PayPal payment ID
        payer_id: PayPal payer ID
    
    Returns:
        dict: {'success': bool, 'payment': Payment object, 'error': str}
    """
    payment = paypalrestsdk.Payment.find(payment_id)
    
    if payment.execute({"payer_id": payer_id}):
        return {
            'success': True,
            'payment': payment,
            'error': None
        }
    else:

        return {
            'success': False,
            'payment': None,
            'error': str(payment.error)
        }


def get_payment_details(payment_id):
    """
    Get details of a PayPal payment
    
    Args:
        payment_id: PayPal payment ID
    
    Returns:
        Payment object or None
    """
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        return payment
    except:
        return None
