from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings


@receiver(user_logged_in)
def send_login_notification(sender, request, user, **kwargs):
    """
    Send an email notification when a user logs in.
    """
    # Get user's IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    # Get user agent (browser info)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown device')
    
    # Prepare email
    subject = 'New Login to Your Account'
    message = f"""
Hello {user.username},

We detected a new login to your account:

- Time: {request.META.get('HTTP_DATE', 'Just now')}
- IP Address: {ip_address}
- Device/Browser: {user_agent}

If this was you, you can safely ignore this email.

If you did not log in, please secure your account immediately by changing your password.

Best regards,
Learning Platform Team
"""
    
    # Send email
    try:
        email = EmailMessage(subject, message, to=[user.email])
        email.send()
    except Exception as e:
        # Log the error but don't prevent login
        print(f"Failed to send login notification: {e}")
