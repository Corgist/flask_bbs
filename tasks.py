import time
from celery import Celery
from marrow.mailer import Mailer

import secret
from config import admin_mail

celery = Celery('tasks', backend='redis://localhost', broker='redis://localhost')


def configured_mailer():
    config = {
        # 'manager.use': 'futures',
        'transport.debug': True,
        'transport.timeout': 1,
        'transport.use': 'smtp',
        'transport.host': 'smtp.exmail.qq.com',
        'transport.port': 465,
        'transport.tls': 'ssl',
        'transport.username': admin_mail,
        'transport.password': secret.mail_password,
    }
    m = Mailer(config)
    m.start()
    return m


mailer = configured_mailer()


@celery.task(bind=True)
def send_async(self, subject, author, to, plain):
    # 需要 bind 拿到 self 调用当前 task 的一些功能
    try:
        m = mailer.new(
            subject=subject,
            author=author,
            to=to,
        )
        m.plain = plain
        mailer.send(m)
        # time.sleep(5)
        # raise ValueError('email error')
    except Exception as exc:
        # 每3秒试一次 最多5次
        raise self.retry(exc=exc, countdown=3, max_retries=5)
