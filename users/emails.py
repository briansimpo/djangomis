
from djangospice.core.mail import Email
from djangospice.utils import get_template_name
from .apps import namespace


class CredentialsEmail(Email):
    template = get_template_name("email/account_credentials.html", namespace)
    subject = "New Account Credentials"
   
