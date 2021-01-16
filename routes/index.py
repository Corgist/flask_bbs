import os
import time
import uuid

from flask import (
    abort,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    current_app,
    make_response,
    render_template,
    send_from_directory,
)
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from models.message import Messages
from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import current_user, cache, login_required

import json

from utils import log


main = Blueprint('index', __name__)

"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


# class TopicEncoder(json.JSONEncoder ):
#     def default(self, obj):
#         if isinstance(obj, Topic):
#             return obj.__str__()
#         return json.JSONEncoder.default(self, obj)


def topichook(dic):
    print("cache.ts", dic)
    if dic['id']:
        return Topic.one(id=dic['id'])
    return dic


@main.route("/")
def index():
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    form = request.form.to_dict()
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    if u is None:
        return redirect(url_for('.index'))
    else:
        # 将session 存写入 redis
        session_id = str(uuid.uuid4())
        key = 'session_id_{}'.format(session_id)
        cache.set(key, u.id)
        # 设置header中set-cookie字段 并指定跳转路由
        redirect_to_index = redirect(url_for('topic.index'))
        response = current_app.make_response(redirect_to_index)
        response.set_cookie('session_id', value=session_id)
        # 转到 topic.index 页面
        return response


def created_topic(user_id):
    # O(n)
    ts = Topic.query.filter_by(user_id=user_id)\
                    .order_by(Topic.created_time.desc())\
                    .all()
    # ts = Topic.all(user_id=user_id)
    return ts
    #
    # k = 'created_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     ts = Topic.all(user_id=user_id)
    #     ts = sorted(ts, key=lambda x: x.created_time, reverse=True)
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #     return ts


def replied_topic(user_id):
    # 避免ORM的n+1问题
    k = 'replied_topic_{}'.format(user_id)
    if cache.exists(k):
        v = cache.get(k)
        ts = json.loads(v, object_hook=topichook)
        return ts
    else:
        # 调用SQLAlchemy join拼接table；filter查询；order_by排序；desc()倒序
        # 解决ORM的n+1问题
        ts = Topic.query.join(Reply, Reply.topic_id == Topic.id)\
                        .filter(Reply.user_id == user_id)\
                        .order_by(Reply.created_time.desc())\
                        .all()
        # rs = Reply.all(user_id=user_id)
        # ts = []
        # for r in rs:
        #     t = Topic.one(id=r.topic_id)
        #     ts.append(t)
        # ts = sorted(ts, key=lambda x: x.updated_time, reverse=True)
        v = json.dumps([t.json() for t in ts])
        cache.set(k, v)
        return ts


@main.route('/profile')
@login_required
def profile():
    print('running profile route')
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        created = created_topic(u.id)
        replied = replied_topic(u.id)
        return render_template(
            'profile.html',
            user=u,
            created=created,
            replied=replied
        )


@main.route('/setting')
@login_required
def setting():
    u = current_user()
    return render_template('setting.html', user=u)


@main.route('/change', methods=['POST'])
def change():
    u = current_user()
    form = request.form.to_dict()
    print('change', form)
    form['updated_time'] = int(time.time())
    User.update(u.id, **form)
    return redirect(url_for('.setting'))


@main.route('/change_pass', methods=['POST'])
def change_pass():
    u = current_user()
    form = request.form.to_dict()
    if u.password == User.salted_password(form['old_pass']):
        u.password = User.salted_password(form['password'])
        form['password'] = u.password
        form['updated_time'] = int(time.time())
        form.pop('old_pass')
        User.update(u.id, **form)
    return redirect(url_for('.setting'))


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        created = created_topic(u.id)
        replied = replied_topic(u.id)
        return render_template(
            'profile.html',
            user=u,
            created=created,
            replied=replied
        )


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    # 不能直接存用戶使用的文件名
    # 有可能被讀取到server文件
    # ../../root/.ssh/authorized_keys
    # images/../../root/.ssh/authorized_keys
    # 可以使用flask的安全文件名函數進行保護
    # filename = secure_filename(file.filename)
    # 文件名后綴也可以被省略
    # suffix = file.filename.split('.')[-1]
    # filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    filename = str(uuid.uuid4())
    path = os.path.join('images', filename)
    file.save(path)

    u = current_user()
    User.update(u.id, image='/images/{}'.format(filename))

    return redirect(url_for('.profile'))


@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:2000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    # if filename in os.listdir('images'):
    #     return
    return send_from_directory('images', filename)


@main.route("/reset/send", methods=["POST"])
def send():
    form = request.form.to_dict()
    username = form['username']
    u = User.one(username=username)
    if u is not None:
        token = str(uuid.uuid4())
        cache.set(token, u.id)
        cache.expire(token, 1800)
        title = '来自 {} 的密码找回信件'.format(u.username)
        content = 'http://www.corgist.xyz/reset/view?token={}'.format(token)
        Messages.send(
            title=title,
            content=content,
            sender_id=1,
            receiver_id=u.id
        )
    else:
        abort(404)
    return redirect(url_for('.index'))


@main.route("/reset/view")
def view():
    token = request.args.get('token')
    if cache.exists(token):
        return render_template('seek_secret.html', token=token)
    else:
        abort(404)


@main.route("/reset/update", methods=['POST'])
def update():
    form = request.form.to_dict()
    password = form['password']
    token = form['token']
    if cache.exists(token):
        u = User.one(id=int(cache.get(token)))
        form['password'] = User.salted_password(password)
        form['updated_time'] = int(time.time())
        form.pop('token')
        User.update(u.id, **form)
    return redirect(url_for('.index'))
