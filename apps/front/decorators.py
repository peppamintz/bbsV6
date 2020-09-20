from functools import wraps
import config
from flask import session, redirect, url_for


def Login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if config.front_user_id in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('front.signin'))
    return inner
