import time
from rq import get_current_job
from app import create_app, db
from app.models import User, Post, Task
from app.email import send_mail
from flask import render_template
import json
import sys
import sqlalchemy as sa

app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        print("progress of job insdie _set_progress", progress)
        job.save_meta()
        print("job meta", job.meta)
        task = db.session.get(Task, job.get_id())
        print("Task inside _set_progress", task)
        task.user.add_notification('task_progress', {'task_id': job.get_id(), 'progress': progress})
        if progress == 100:
            print("progress 100")
            task.complete = True
        db.session.commit()

def export_posts(user_id):
    print("EMAIL",app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    try:
        user = db.session.get(User, user_id)
        _set_task_progress(0)
        total_posts = db.session.scalar(sa.select(sa.func.count()).select_from(user.posts.select().subquery()))
        print("total_posts", total_posts)
        data = []
        i = 0 
        for post in db.session.scalars(user.posts.select().order_by(Post.timestamp.asc())):
            data.append({'body': post.body, 'timestamp': post.timestamp.isoformat() + 'Z'})
            i += 1
            time.sleep(1)
            _set_task_progress(100 * i // total_posts)
        #enable when use SES
        # send_mail(
        #     '[Microblog] Your blog posts',
        #     sender=app.config['ADMINS'][0], recipients=[user.email],
        #     text_body=render_template('email/export_posts.txt', user=user),
        #     html_body=render_template('email/export_posts.html', user=user),
        #     attachments=[('posts.json', 'application/json',
        #                   json.dumps({'posts': data}, indent=4))],
        #     sync=True)
    except Exception:
        _set_task_progress(100)
        app.logger.error('Unhanlded exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)

