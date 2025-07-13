from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail 


def send_async_mail(app, msg):
    with app.app_context():
        email = mail.send(msg)
        print(email)
        print(msg)

def send_mail(subject, sender, recipients, text_body, html_body, attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)

    msg.body = text_body
    msg.html = html_body

    if sync:
        email = mail.send(msg)
        print(email)
        print(msg)
    else:
        Thread(target=send_async_mail, args=(current_app._get_current_object(), msg)).start()


    