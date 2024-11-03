from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail 


def send_async_mail(app, msg):
    with app.app_context():
        email = mail.send(msg)
        print(email)
        print(msg)

def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_mail, args=(current_app._get_current_object(), msg)).start()

    