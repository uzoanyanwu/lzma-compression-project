"""
Custom email backend that stores emails in memory for display on a web page.
This is for development/demo purposes only.
"""
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User


class InMemoryEmailBackend(BaseEmailBackend):
    """
    Email backend that stores emails in a class variable for display.
    Only keeps the most recent email.
    Only stores emails if the recipient exists in the database.
    """
    latest_email = None

    def send_messages(self, email_messages):
        """
        Store the email messages in memory instead of sending them.
        Only stores if the recipient email exists in the User database.
        """
        if not email_messages:
            return 0

        # Store only the latest email, and only if the user exists
        for message in email_messages:
            # Check if any of the recipients exist in the database
            user_exists = False
            for recipient in message.to:
                if User.objects.filter(email=recipient).exists():
                    user_exists = True
                    break

            # Only store the email if the user exists
            if user_exists:
                InMemoryEmailBackend.latest_email = {
                    'subject': message.subject,
                    'body': message.body,
                    'from_email': message.from_email,
                    'to': message.to,
                    'date': message.extra_headers.get('Date', 'Now'),
                }
            else:
                # Clear any existing email if the user doesn't exist
                InMemoryEmailBackend.latest_email = None

        return len(email_messages)

    @classmethod
    def get_latest_email(cls):
        """
        Retrieve the latest email stored in memory.
        """
        return cls.latest_email

    @classmethod
    def clear_email(cls):
        """
        Clear the stored email.
        """
        cls.latest_email = None
