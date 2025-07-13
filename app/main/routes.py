from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import  current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm, EmptyForm, MessageForm, PostForm, SearchForm 
from app.models import Notification, User, Post, Message
from langdetect import detect, LangDetectException
from app.utils import googleSignup
from app.main import bp
from celery.result import AsyncResult


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))
    
@bp.route('/translate', methods=['POST']) 
# @login_required
def translate():
    data = request.get_json()
    try:
        translated_text = googleSignup.translate_text(data['target'], data['text'])
        print(f"transledtexttt:{translated_text['translatedText']}")
    except Exception as e:
        print(e)
    return {'text': translated_text['translatedText']}

@bp.route('/search', methods=['GET'])
def search():
    # not using .validate_on_submit as this is a GET form and not a POST form
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page+1) if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page-1) if page  > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)

@bp.route('/send_message/<receiver>', methods=['GET','POST'])
@login_required
def send_message(receiver):
    user = db.first_or_404(sa.select(User).where(User.username == receiver))
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, receiver=user, body=form.message.data)
        db.session.add(msg)
        #note that the notification is for the user that the msg is being sent and not for current_user!
        user.add_notification('unread_message_count', user.unread_messages_count())
        db.session.commit()
        flash(_("Your message has been sent."))
        return redirect(url_for('main.user', username=receiver))
    return render_template('send_message.html', title=_('Send Message'), form=form, receiver=receiver)

@bp.route('/messages', methods=['GET'])
@login_required
def view_messages():
    '''
        we need to fetch all the message the user has gotten sorted by the message timestamp
        just query messages_received first and render that
    '''
    current_user.last_message_read_time = datetime.now(timezone.utc)
    #once the user opens the messages page meaning they read all notifications, so its safe to assume unread msgs = 0
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    print("current_user.messages_received", current_user.messages_received)
    query = current_user.messages_received.select().order_by(Message.timestamp.desc())
    msgs = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'],
                           error_out=False)
    next_url = url_for('main.messages', page=msgs.next_num) if msgs.has_next else None
    prev_url = url_for('main.messages', page=msgs.prev_num) if msgs.has_prev else None

    return render_template('messages.html', messages=msgs, next_url=next_url, prev_url=prev_url)

@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    query = current_user.notifications.select().where(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    notifications = db.session.scalars(query)
    return [
        {
            'name': n.name,
            'data': n.get_data(),
            'timestamp': n.timestamp
        } for n in notifications
    ]

#@bp.route('/callceleryapp', methods=['POST'])
#def call_celery_task():
#    time_delay = request.form.get('delay')
#    result = example.delay(int(time_delay))
#    return {"result_id": result.id, "result_status": result.status, "result_data": result.result, "result_info":result.info}

# @bp.route('/getjob', methods=['GET'])
# def get_celery_task():
#     job_id = request.form.get('job_id')
#     result = AsyncResult(job_id)
#     print(result)
#     if result:
#         return {"result_id": result.id, "result_status": result.status, "result_data": result.result, "result_info":result.info}
#     else:
#         return "ok job found"

@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export posts task is currently in process'))
    else:
        current_user.launch_task('export_posts', _('Exporting Posts...'))
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))