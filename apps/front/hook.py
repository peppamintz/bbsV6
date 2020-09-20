from .views import bp
from flask import session, g, render_template
import config
from .models import FrontUser

@bp.before_request
def my_before_request():
    if config.front_user_id in session:
        user_id = session[config.front_user_id]
        user = FrontUser.query.get(user_id)
        if user:
            g.front_user = user


@bp.errorhandler
def page_not_found():
    return render_template('front/front_404.html'), 404