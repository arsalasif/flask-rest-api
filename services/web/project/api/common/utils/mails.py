from flask import render_template, request, url_for, current_app

from ....tasks.mail_tasks import send_async_registration_email, send_async_password_recovery_email,\
    send_async_email_verification_email


def send_password_recovery_email(user, token):
    """
    Send email for password recovery
    """
    href = request.base_url + '/' + token
    app_name = current_app.config.get('APP_NAME')
    send_async_password_recovery_email.delay(subject=f'Password Recovery for {app_name}',
                                             recipient=user.email,
                                             text_body=render_template("auth/password_recovery_user.txt", user=user),
                                             html_body=render_template("auth/password_recovery_user.html", user=user, href=href))


def send_registration_email(user, token):
    """
    Send email for registration
    """
    href = request.url_root + url_for('email_verification.verify_email', token='')[1:] + token
    app_name = current_app.config.get('APP_NAME')
    send_async_registration_email.delay(subject=f'Welcome to {app_name}!',
                                        recipient=user.email,
                                        text_body=render_template("auth/welcome_new_user.txt", user=user),
                                        html_body=render_template("auth/welcome_new_user.html", user=user, href=href))


def send_email_verification_email(user, token):
    """
    Send email for verification
    """
    href = request.base_url + '/' + token
    app_name = current_app.config.get('APP_NAME')
    send_async_email_verification_email.delay(subject=f'Email confirmation for {app_name}',
                                              recipient=user.email,
                                              text_body=render_template("auth/email_verification_user.txt", user=user),
                                              html_body=render_template("auth/email_verification_user.html", user=user, href=href))
