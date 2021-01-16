#!/usr/bin/env python3

from flask import Flask
from flask_admin import Admin

import time
import secret
from models.user import User
from models.board import Board
from models.base_model import db

from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.board import main as board_routes
from routes.message import main as mail_routes
from flask_admin.contrib.sqla import ModelView
from utils import log


class UserModelView(ModelView):
    column_searchable_list = ('username', 'password')


def remove_script(content: str):
    log('remove_script <{}>'.format(content))
    c = str(content)
    c = c.replace('>', '&gt')
    c = c.replace('<', '&lt')
    print('remove_script after <{}>'.format(c))
    return c


def format_time(unix_timestamp):
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def history_time(unix_timestamp):
    time_diff = time.time() - int(unix_timestamp)
    time_dict = {}
    time_dict['年'] = time_diff // 31536000
    time_dict['个月'] = time_diff // 2592000
    time_dict['天'] = time_diff // 86400
    time_dict['小时'] = time_diff // 3600
    time_dict['分钟'] = time_diff // 60
    time_dict['秒'] = time_diff // 1
    for i in time_dict:
        if time_dict[i] != 0:
            timeago = str(int(time_dict[i])) + i
            break
    return timeago


def configured_app():
    # web framework
    # web application
    # __main__
    app = Flask(__name__)
    app.secret_key = secret.secret_key

    uri = 'mysql+pymysql://root:{}@localhost/web21?charset=utf8mb4'.format(
        secret.database_password
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    app.template_filter()(format_time)
    app.template_filter()(history_time)

    admin = Admin(app, name='admin', template_mode='bootstrap3')
    mv = UserModelView(User, db.session)
    admin.add_view(mv)
    mv = ModelView(Board, db.session)
    admin.add_view(mv)

    register_routes(app)
    return app


def register_routes(app):
    """
    在 flask 中，模块化路由的功能由 Blueprints提供
    蓝图可以拥有自己的静态资源路径、模板路径
    """
    # 注册蓝图
    # url_prefix 可以用来给蓝图中的每个路由加一个前缀

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(board_routes, url_prefix='/board')
    app.register_blueprint(mail_routes, url_prefix='/mail')


# 运行代码
if __name__ == '__main__':
    app = configured_app()
    # debug 模式可以自动加载你对代码的变动, 不用重启程序
    # host 参数指定为 '0.0.0.0' 可以让别的机器访问你的代码
    # 自动 reload jinja
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    config = dict(
        debug=True,
        host='localhost',
        port=3000,
        threaded=True,
    )
    app.run(**config)
