"""
Brevo Email Service using Transactional Email API
This module provides email sending functionality using Brevo's API instead of SMTP.
"""
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings


def send_brevo_email(to_email, subject, html_content, sender_name="Learning Platform"):
    """
    Send email using Brevo Transactional Email API
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_content (str): HTML content of the email
        sender_name (str): Name of the sender
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        # Configure API key authorization
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        
        # Create an instance of the API class
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Prepare sender
        sender = {
            "name": sender_name,
            "email": settings.BREVO_SENDER_EMAIL
        }
        
        # Prepare recipient
        to = [{"email": to_email}]
        
        # Create email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            subject=subject,
            html_content=html_content
        )
        
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        return {
            'success': True,
            'message': f'Email sent successfully. Message ID: {api_response.message_id}'
        }
        
    except ApiException as e:
        return {
            'success': False,
            'message': f'Brevo API error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error sending email: {str(e)}'
        }
