from flask import current_app, render_template
from app.email import send_mail
from flask_babel import _


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail(_('[Microblog] Reset Your Password'),
              sender=current_app.config['MAIL_SENDER'],
              recipients=[user.email],
              text_body=render_template('email/reset_password.txt',
                                        user=user, token=token),
            html_body=render_template('email/reset_password.html', user=user, token=token)
              )