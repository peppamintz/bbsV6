from .views import bp
import config
from flask import session, g
from .models import CmsUser, CmsPermission

@bp.before_request
def before_request():
    if config.cms_user_id in session:
        user_id = session[config.cms_user_id]
        user = CmsUser.query.get(user_id)
        if user:
            g.cms_user = user


@bp.context_processor
def cms_context_processor():
    print({'CmsPermission': CmsPermission})
    print(CmsPermission)
    return {'CmsPermission': CmsPermission}