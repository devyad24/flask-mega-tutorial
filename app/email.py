from threading import Thread
from flask import render_template
from flask_mail import Message
from app import mail, app
from flask_babel import _


def send_async_mail(app, msg):
    with app.app_context():
        email = mail.send(msg)
        print(email)
        print(msg)
def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_mail, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail(_('[Microblog] Reset Your Password'),
              sender=app.config['MAIL_SENDER'],
              recipients=[user.email],
              text_body=render_template('email/reset_password.txt',
                                        user=user, token=token),
            html_body=render_template('email/reset_password.html', user=user, token=token)
              )
    