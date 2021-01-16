from flask import (
    request,
    url_for,
    redirect,
    Blueprint,
    render_template,
)
from routes import *
from models.message import Messages

main = Blueprint('mail', __name__)


@main.route("/add", methods=["POST"])
@login_required
def add():
    form = request.form.to_dict()
    u = current_user()
    receiver_id = int(form['receiver_id'])
    # 发邮件
    Messages.send(
        title=form['title'],
        content=form['content'],
        sender_id=u.id,
        receiver_id=receiver_id
    )

    return redirect(url_for('.index'))


@main.route('/')
@login_required
def index():
    u = current_user()
    if u is None:
        return redirect("../")
    else:
        send = Messages.all(sender_id=u.id)
        received = Messages.all(receiver_id=u.id)

        t = render_template(
            'mail/index.html',
            send=send,
            received=received,
        )
        return t


@main.route('/view/<int:id>')
def view(id):
    message = Messages.one(id=id)
    u = current_user()
    token = new_csrf_token()
    # if u.id == mail.receiver_id or u.id == mail.sender_id:
    if u.id in [message.receiver_id, message.sender_id]:
        sender = User.one(id=message.sender_id)
        receiver = User.one(id=message.receiver_id)
        return render_template('mail/detail.html', message=message, sender=sender, receiver=receiver, token=token)
    else:
        return redirect(url_for('.index'))


@main.route("/delete")
@csrf_required
@login_required
def delete():
    id = int(request.args.get('id'))
    u = current_user()
    print('删除用户{}的邮件,编号为{}'.format(u.username, id))
    Messages.delete(id)
    return redirect(url_for('mail.index'))
