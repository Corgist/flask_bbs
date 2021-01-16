import time

from sqlalchemy import create_engine

import config
import secret
from app import configured_app
from models.base_model import db
from models.board import Board
from models.reply import Reply
from models.topic import Topic
from models.user import User


def reset_database():
    # 现在 mysql root 默认用 socket 来验证而不是密码
    url = 'mysql+pymysql://root:{}@localhost/?charset=utf8mb4'.format(
        secret.database_password
    )
    e = create_engine(url, echo=True)

    with e.connect() as c:
        c.execute('DROP DATABASE IF EXISTS web21')
        c.execute('CREATE DATABASE web21 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        c.execute('USE web21')

    db.metadata.create_all(bind=e)


def generate_fake_date():
    form = dict(
        username='admin',
        password='admin',
        signature=config.signature,
        image='/images/u=3897107930,3785938129&fm=26&gp=0.jpg',
        email=config.test_mail
    )
    u = User.register(form)

    form = dict(
        username='test',
        password='123',
        signature=config.signature,
        image='/images/timg.jpg',
        email=config.test_mail
    )
    u = User.register(form)

    form = dict(
        username='corgist',
        password='123',
        signature=config.signature,
        image='/images/1.jpg',
        email=config.test_mail
    )
    u = User.register(form)

    form = dict(
        title='测试区'
    )
    b = Board.new(form)
    topic_form = dict(
        title='测试用户发帖',
        board_id=b.id,
        content='test'
    )
    for i in range(3):
        print('begin topic <{}>'.format(i))
        Topic.new(topic_form, u.id)

    form = dict(
        title='发帖区'
    )
    b = Board.new(form)
    with open('markdown_demo.md', encoding='utf8') as f:
        content = f.read()
    topic_form = dict(
        title='markdown 内容测试帖',
        board_id=b.id,
        content=content
    )

    for i in range(3):
        print('begin topic <{}>'.format(i))
        t = Topic.new(topic_form, u.id)

        reply_form = dict(
            content='reply test',
            topic_id=t.id,
        )
        for j in range(2):
            Reply.new(reply_form, u.id)


if __name__ == '__main__':
    app = configured_app()
    with app.app_context():
        reset_database()
        generate_fake_date()
