from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    Request)

from models.message import Messages
from models.topic import Topic
from routes import *

from models.reply import Reply
from routes.index import topichook

main = Blueprint('reply', __name__)


def users_from_content(content):
    # 内容 @123 内容
    # 如果用户名含有空格 就不行了 @name 123
    # 'a b c' -> ['a', 'b', 'c']
    parts = content.split()
    users = []

    for p in parts:
        if p.startswith('@'):
            username = p[1:]
            u = User.one(username=username)
            print('users_from_content <{}> <{}> <{}>'.format(username, p, parts))
            if u is not None:
                users.append(u)

    return users


def send_mails(sender, receivers, reply_link, reply_content):
    print('send_mail', sender, receivers, reply_content)
    content = '链接：{}\n内容：{}'.format(
        reply_link,
        reply_content
    )
    for r in receivers:
        title = '你被 {} AT 了'.format(sender.username)
        Messages.send(
            title=title,
            content=content,
            sender_id=sender.id,
            receiver_id=r.id
        )


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    # 在回复中判断@对象 并发送私信
    content = form['content']
    users = users_from_content(content)
    send_mails(u, users, request.referrer, content)
    # 添加回复，并更新topic的updated_time
    form = form.to_dict()
    m = Reply.new(form, user_id=u.id)
    Topic.update(m.topic_id, updated_time=m.updated_time)
    # 更新redis内的replied_topic
    k = 'replied_topic_{}'.format(u.id)
    if cache.exists(k):
        cache.delete(k)
    # rs = Reply.all(user_id=u.id)
    # ts = []
    # for r in rs:
    #     t = Topic.one(id=r.topic_id)
    #     ts.append(t)
    # v = json.dumps([t.json() for t in ts])
    # cache.set(k, v)
    return redirect(url_for('topic.detail', id=m.topic_id))
