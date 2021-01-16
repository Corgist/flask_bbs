import hashlib

from sqlalchemy import Column, String, Text
from flask import redirect, url_for
import config
import secret
import random
import smtplib
import logging
import time
# import dns.resolver
from models.base_model import SQLMixin, db


class User(SQLMixin, db.Model):
    __tablename__ = 'User'
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    image = Column(String(100), nullable=False, default='/images/register.jpg')
    email = Column(String(50), nullable=False, default=config.test_mail)
    signature = Column(String(100), nullable=False, default=config.signature)

    @staticmethod
    def salted_password(password, salt='$!@><?>HUI&DWQa`'):
        salted = hashlib.sha256((password + salt).encode('ascii')).hexdigest()
        return salted

    # @staticmethod
    # def fetch_mx(host):
    #     '''
    #     解析服务邮箱
    #     :param host:
    #     :return:
    #     '''
    #     try:
    #         answers = dns.resolver.query(host, 'MX')
    #     except:
    #         return redirect(url_for('.index'))
    #     res = [str(rdata.exchange)[:-1] for rdata in answers]
    #     return res
    #
    # @staticmethod
    # def verify_istrue(email):
    #     '''
    #     :param email:
    #     :return:
    #     '''
    #     email_list = []
    #     email_obj = {}
    #     final_res = {}
    #
    #     if isinstance(email, str) or isinstance(email, bytes):
    #         email_list.append(email)
    #     else:
    #         email_list = email
    #     for em in email_list:
    #         name, host = em.split('@')
    #         if email_obj.get(host):
    #             email_obj[host].append(em)
    #         else:
    #             email_obj[host] = [em]
    #
    #     for key in email_obj.keys():
    #         host = random.choice(User.fetch_mx(key))
    #         s = smtplib.SMTP(host, timeout=10)
    #         for need_verify in email_obj[key]:
    #             helo = s.docmd('HELO chacuo.net')
    #
    #             send_from = s.docmd('MAIL FROM:<3121113@chacuo.net>')
    #             send_from = s.docmd('RCPT TO:<%s>' % need_verify)
    #             if send_from[0] == 250 or send_from[0] == 451:
    #                 final_res[need_verify] = True  # 存在
    #             elif send_from[0] == 550:
    #                 final_res[need_verify] = False  # 不存在
    #             else:
    #                 final_res[need_verify] = None  # 未知
    #
    #         s.close()
    #
    #     return final_res[need_verify]

    @classmethod
    def register(cls, form):
        name = form.get('username', '')
        pwd = form.get('password', '')
        email = form.get('email', '')
        print('register', form)
        if len(name) > 2 and len(pwd) > 2 and User.one(username=name) is None:
            # 错误，只应该 commit 一次
            # u = User.new(form)
            # u.password = u.salted_password(pwd)
            # User.session.add(u)
            # User.session.commit()
            form['password'] = User.salted_password(form['password'])
            u = User.new(form)
            return u
        else:
            return None

    @classmethod
    def validate_login(cls, form):
        query = dict(
            username=form['username'],
            password=User.salted_password(form['password']),
        )
        print('validate_login', form, query)
        return User.one(**query)

    @staticmethod
    def guest():
        u = User()
        u.username = '【游客】'
        return u
