from functools import wraps
import config
from flask import session, redirect, url_for, g



def Login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if config.cms_user_id in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('cms.login'))
    return inner

def Permission_required(permission):
    def outter(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if g.cms_user.has_permission(permission):
                return func(*args, **kwargs)
            else:
                return redirect(url_for('cms.index'))
        return inner
    return outter