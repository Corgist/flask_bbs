import uuid
from functools import wraps

from flask import session, request, abort, redirect, url_for

from models.user import User

from utils import log

import json

import redis

cache = redis.StrictRedis()


def current_user():
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        # s = Session.one_for_session_id(session_id=session_id)
        key = 'session_id_{}'.format(session_id)
        user_id = int(cache.get(key))
        log('current_user key <{}> user_id <{}>'.format(key, user_id))
        if user_id is None:
            return User.guest()
        else:
            u = User.one(id=user_id)
            if u is None:
                return User.guest()
            else:
                return u
    else:
        return User.guest()


def login_required(route_function):
    @wraps(route_function)
    def f(*args, **kwargs):
        log('login_required')
        u = current_user()
        if u.username == '【游客】':
            log('游客用户')
            return redirect(url_for('index.index'))
        else:
            log('登录用户', route_function)
            return route_function(*args, **kwargs)
    return f


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        u = current_user()
        k = 'csrf_tokens_{}'.format(u.id)
        if cache.exists(k) and json.loads(cache.get(k)) == token:
            cache.delete(k)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    k = 'csrf_tokens_{}'.format(u.id)
    v = json.dumps(token)
    cache.set(k, v)
    return token
