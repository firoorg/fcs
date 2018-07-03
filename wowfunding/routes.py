from datetime import datetime
from flask import request, redirect, Response, abort, render_template, url_for, flash, make_response, send_from_directory, jsonify
from flask.ext.login import login_user , logout_user , current_user, login_required, current_user
from flask_yoloapi import endpoint, parameter

import settings
from wowfunding.factory import app, db_session
from wowfunding.orm.orm import Proposal, User, Comment


@app.route('/')
def index():
    return redirect(url_for('proposals'))


@app.route('/about')
def about():
    return make_response(render_template('about.html'))


@app.route('/proposal/add')
def proposal_add():
    if current_user.is_anonymous:
        return make_response(redirect(url_for('login')))
    return make_response(render_template(('proposal_edit.html')))


@app.route('/proposal/comment', methods=['POST'])
@endpoint.api(
    parameter('pid', type=int, required=True),
    parameter('text', type=str, required=True),
    parameter('cid', type=int, required=False)
)
def proposal_comment(pid, text, cid):
    if current_user.is_anonymous:
        flash('not logged in', 'error')
        return redirect(url_for('proposal', pid=pid))
    if len(text) <= 3:
        flash('comment too short', 'error')
        return redirect(url_for('proposal', pid=pid))
    try:
        Comment.add_comment(user_id=current_user.id, message=text, pid=pid, cid=cid)
    except Exception as ex:
        flash('Could not add comment: %s' % str(ex), 'error')
        return redirect(url_for('proposal', pid=pid))

    flash('Comment posted.')
    return redirect(url_for('proposal', pid=pid))


@app.route('/proposal/<int:pid>/comment/<int:cid>')
def propsal_comment_reply(cid, pid):
    from wowfunding.orm.orm import Comment
    c = Comment.find_by_id(cid)
    if not c or c.replied_to:
        return redirect(url_for('proposal', pid=pid))
    p = Proposal.find_by_id(pid)
    if not p:
        return redirect(url_for('proposals'))
    if c.proposal_id != p.id:
        return redirect(url_for('proposals'))

    return make_response(render_template('comment_reply.html', c=c, pid=pid, cid=cid))


@app.route('/proposal/<int:pid>')
def proposal(pid):
    p = Proposal.find_by_id(pid=pid)
    p.get_comments()
    if not p:
        return make_response(redirect(url_for('proposals')))
    return make_response(render_template(('proposal.html'), proposal=p))


@app.route('/api/proposal/add', methods=['POST'])
@endpoint.api(
    parameter('title', type=str, required=True, location='json'),
    parameter('content', type=str, required=True, location='json'),
    parameter('pid', type=int, required=False, location='json'),
    parameter('funds_target', type=float, required=True, location='json'),
    parameter('addr_receiving', type=str, required=True, location='json')
)
def proposal_api_add(title, content, pid, funds_target, addr_receiving):
    import markdown2

    if current_user.is_anonymous:
        return make_response(jsonify('err'), 500)

    if len(title) <= 10:
        return make_response(jsonify('title too short'), 500)
    if len(content) <= 20:
        return make_response(jsonify('content too short'), 500)

    try:
        from wowfunding.bin.anti_xss import such_xss
        content_escaped = such_xss(content)
        html = markdown2.markdown(content_escaped, safe_mode=True)
    except Exception as ex:
        return make_response(jsonify('markdown error'), 500)

    if pid:
        p = Proposal.find_by_id(pid=pid)
        if not p:
            return make_response(jsonify('proposal not found'), 500)

        if p.user.id != current_user.id and not current_user.admin:
            return make_response(jsonify('no rights to edit this proposal'), 500)

        p.headline = title
        p.content = content
        p.html = html
        if addr_receiving:
            p.addr_receiving = addr_receiving
        p.last_edited = datetime.now()
    else:
        if funds_target <= 1:
            return make_response(jsonify('proposal asking less than 1 error :)'), 500)
        if len(addr_receiving) != 97:
            return make_response(jsonify('faulty addr_receiving address, should be of length 72'), 500)

        p = Proposal(headline=title, content=content, category='misc', user=current_user)
        p.html = html
        p.last_edited = datetime.now()
        p.funds_target = funds_target
        p.addr_receiving = addr_receiving
        db_session.add(p)

    db_session.commit()
    db_session.flush()
    return make_response(jsonify({'url': url_for('proposal', pid=p.id)}))


@app.route('/proposal/<int:pid>/edit')
def proposal_edit(pid):
    p = Proposal.find_by_id(pid=pid)
    if not p:
        return make_response(redirect(url_for('proposals')))

    return make_response(render_template(('proposal_edit.html'), proposal=p))


@app.route('/search')
@endpoint.api(
    parameter('key', type=str, required=False)
)
def search(key=None):
    if not key:
        return make_response(render_template('search.html', results=None, key='Empty!'))
    results = Proposal.search(key=key)
    return make_response(render_template('search.html', results=results, key=key))


@app.route('/user/<path:name>')
def user(name):
    q = db_session.query(User)
    q = q.filter(User.username == name)
    user = q.first()
    return render_template('user.html', user=user)


@app.route('/proposals')
@endpoint.api(
    parameter('status', type=int, location='args', default=0),
    parameter('page', type=int, location='args'),
    parameter('cat', type=str, location='args')
)
def proposals(status, page, cat):
    try:
        proposals = Proposal.find_by_args(status=status, cat=cat)
    except:
        return make_response(redirect(url_for('proposals') + '?status=0'))

    return make_response(render_template('proposals.html', proposals=proposals, status=status, cat=cat))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if settings.USER_REG_DISABLED:
        return 'user reg disabled ;/'

    if request.method == 'GET':
        return make_response(render_template('register.html'))

    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    try:
        user = User.add(username, password, email)
        flash('Successfully registered. No confirmation email required. You can login!')
        return redirect(url_for('login'))
    except Exception as ex:
        flash('Could not register user: %s' % str(ex), 'error')
        return make_response(render_template('register.html'))


@app.route('/login', methods=['GET', 'POST'])
@endpoint.api(
    parameter('username', type=str, location='form'),
    parameter('password', type=str, location='form')
)
def login(username, password):
    if request.method == 'GET':
        return make_response(render_template('login.html'))

    from wowfunding.factory import bcrypt
    user = User.query.filter_by(username=username).first()
    if user is None or not bcrypt.check_password_hash(user.password, password):
        flash('Username or Password is invalid', 'error')
        return make_response(render_template('login.html'))

    login_user(user)
    response = redirect(request.args.get('next') or url_for('index'))
    response.headers['X-Set-Cookie'] = True
    return response


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    response = redirect(request.args.get('next') or url_for('login'))
    response.headers['X-Set-Cookie'] = True
    flash('Logout successfully')
    return response


@app.route('/static/<path:path>')
def static_route(path):
    return send_from_directory('static', path)