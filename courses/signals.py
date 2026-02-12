from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .brevo_email import send_brevo_email


@receiver(user_logged_in)
def send_login_notification(sender, request, user, **kwargs):
    """
    Send an email notification when a user logs in using Brevo API.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown device')
    timestamp = timezone.now().strftime('%B %d, %Y at %I:%M %p %Z')
    context = {
        'username': user.username,
        'timestamp': timestamp,
        'ip_address': ip_address,
        'user_agent': user_agent,
    }
    html_message = render_to_string('emails/login_notification.html', context)
    subject = 'New Login to Your Account - Learning Platform'
    try:
        result = send_brevo_email(
            to_email=user.email,
            subject=subject,
            html_content=html_message
        )
        if not result['success']:
            print(f"Failed to send login notification: {result['message']}")
    except Exception as e:
        print(f"Failed to send login notification: {e}")


