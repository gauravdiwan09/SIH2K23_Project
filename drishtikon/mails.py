from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings

port='http://127.0.0.1:8000/'

def contact_us_email(message,email):
    try:
        subject="Donot Reply"
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True

def otp_email(subject,message,email):
    try:
        email_from=settings.EMAIL_HOST_USER
        recipient_list=[email,]
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True

def share_details_email(subject,message,emaillist):
    try:
        email_from=settings.EMAIL_HOST_USER
        recipient_list=emaillist
        print(recipient_list)
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        return False
    return True