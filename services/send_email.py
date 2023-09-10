from django.conf import settings
from django.contrib.auth.models import User

from django.core.mail import EmailMessage
from django.template.loader import get_template

from authentication.models import AccountVerification

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator


def send_user_activation_mail(request, user):
    
    # Generate a token for email verification
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    AccountVerification.objects.filter(user=user).delete()

    AccountVerification.objects.create(user=user, uid=uid, token=token)
    
    # Construct the verification URL
    verification_url = f"http://{get_current_site(request)}/api/verify/{uid}/{token}"

    subject = "Verify Your Email"
    data = {"verification_url": verification_url,}
    message = get_template("email/account_verification.html").render(data)
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
        reply_to=[settings.EMAIL_HOST_USER],
    )
    mail.content_subtype = "html"
    mail.send()
    return True

# def send_forget_password_mail(email):
#     otp = random.randint(1000, 9999)

#     user = User.objects.get(email=email)

#     if ForgetPasswordOTP.objects.filter(user=user).exists():
#         ForgetPasswordOTP.objects.filter(user=user).delete()

#     opt_obj = ForgetPasswordOTP(user=user, otp=otp)
#     opt_obj.save()

#     subject = "Forget Password OTP"
#     data = {"otp": otp, "title": "Verify your OTP"}
#     message = get_template("otp_email.html").render(data)
#     mail = EmailMessage(
#         subject=subject,
#         body=message,
#         from_email=settings.EMAIL_HOST_USER,
#         to=[email],
#         reply_to=[settings.EMAIL_HOST_USER],
#     )
#     mail.content_subtype = "html"
#     mail.send()
#     return True



