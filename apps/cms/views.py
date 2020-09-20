from flask import Blueprint, views, render_template, request, session,\
    redirect, url_for, g, jsonify
from .forms import LoginForm, ResetpwdForm, ResetemailForm, AddBannerForm, \
    UpdateBannerForm, AddBoardForm, UpdateBoardForm
from .models import CmsUser, CmsPermission
import config
from .decorators import Login_required, Permission_required
from exts import db, mail
from utils import restful, cache
from flask_mail import Message
import string
import random
from ..models import BannerModel, BoardModel, PostModel, HighlightPostModel





bp = Blueprint('cms', __name__, url_prefix="/cms")


@bp.route('/')
@Login_required
def index():
    return render_template('cms/cms_index.html')


@bp.route('/logout')
@Login_required
def logout():
    del session[config.cms_user_id]
    return redirect(url_for('cms.login'))


@bp.route('/profile')
@Login_required
def profile():
    return render_template('cms/cms_profile.html')


# test email 1
@bp.route('/email/')
def sent_email():
    message = Message('邮件发送', recipients=['250972096@qq.com'], body='测试')
    mail.send(message)
    print('success')
    return 'success'


# test email 2
@bp.route('/email_captcha/')
@Login_required
def email_captcha():
    #     /email_captcha/?email=xxx@qq.com
    email = request.args.get('email')
    if not email:
        return restful.params_error("请传入邮箱参数")
    source = list(string.ascii_letters)
    source.extend(map(lambda x: str(x), range(0, 10)))
    captcha = "".join(random.sample(source, 6))

    message = Message('验证码', recipients=[email], body='您的论坛验证码是：%s' % captcha)
    try:
        mail.send(message)
    except:
        return restful.server_error()
    cache.set(email, captcha)
    return restful.success()


@bp.route('/posts/')
@Login_required
@Permission_required(CmsPermission.POSTER)
def posts():
    post_list = PostModel.query.all()
    return render_template('cms/cms_posts.html', posts=post_list)


@bp.route('/hpost/', methods=["POST"])
@Login_required
@Permission_required(CmsPermission.POSTER)
def hpost():
    post_id = request.form.get("post_id")
    if not post_id:
        return restful.params_error('请传入帖子id！')
    post = PostModel.query.get(post_id)
    if not post:
        return restful.params_error('没有这个帖子！')
    highlight = HighlightPostModel()
    highlight.post = post
    db.session.add(highlight)
    db.session.commit()
    return restful.success()


@bp.route('/dhpost/', methods=['POST'])
@Login_required
@Permission_required(CmsPermission.POSTER)
def dhpost():
    post_id = request.form.get("post_id")
    if not post_id:
        return restful.params_error('请传入帖子id！')
    post = PostModel.query.get(post_id)
    if not post:
        return restful.params_error('没有这篇帖子！')

    highlight = HighlightPostModel.query.filter_by(post_id=post_id).first()
    db.session.delete(highlight)
    db.session.commit()
    return restful.success()


@bp.route('/comments/')
@Login_required
@Permission_required(CmsPermission.COMMENTER)
def comments():
    return render_template('cms/cms_comments.html')


@bp.route('/boards/')
@Login_required
@Permission_required(CmsPermission.BOARDER)
def boards():
    board_model = BoardModel.query.all()
    context = {
        'boards': board_model
    }
    return render_template('cms/cms_boards.html', **context)


@bp.route('/aboard/', methods=["POST"])
@Login_required
@Permission_required(CmsPermission.BOARDER)
def aboard():
    form = AddBoardForm(request.form)
    if form.validate():
        name = form.name.data
        board = BoardModel(name=name)
        db.session.add(board)
        db.session.commit()
        return restful.success()
    else:
        return restful.params_error(form.get_error())


@bp.route('/uboard/', methods=["POST"])
@Login_required
@Permission_required(CmsPermission.BOARDER)
def uboard():
    form = UpdateBoardForm(request.form)
    if form.validate():
        board_id = form.board_id.data
        name = form.name.data
        board = BoardModel.query.get(board_id)
        if board:
            board.name = name
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message='没有这个板块')
    else:
        return restful.params_error(message=form.get_error())


@bp.route('/dboard/', methods=['POST'])
@Login_required
@Permission_required(CmsPermission.BOARDER)
def dboard():
    board_id = request.form.get("board_id")
    print(board_id)
    if not board_id:
        return '请传入需要删除板块的id'
    board = BoardModel.query.get(board_id)
    if not board:
        return restful.params_error(message='没有这个板块！')

    db.session.delete(board)
    db.session.commit()
    return restful.success()



@bp.route('/fusers/')
@Login_required
@Permission_required(CmsPermission.FRONTUSER)
def fusers():
    return render_template('cms/cms_fusers.html')


@bp.route('/cusers/')
@Login_required
@Permission_required(CmsPermission.CMSUSER)
def cusers():
    return render_template('cms/cms_cusers.html')


@bp.route('/croles/')
@Login_required
@Permission_required(CmsPermission.ALL_PERMISSION)
def croles():
    return render_template('cms/cms_croles.html')


@bp.route('/banners/')
@Login_required
@Permission_required(CmsPermission.BANNER)
def banners():
    banners = BannerModel.query.order_by(BannerModel.priority.desc()).all()
    return render_template('cms/cms_banners.html', banners=banners)


@bp.route('/addbanner/', methods=['POST'])
@Login_required
@Permission_required(CmsPermission.BANNER)
def addbanner():
    form = AddBannerForm(request.form)
    if form.validate():
        print('banner')
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner = BannerModel(name=name, image_url=image_url, link_url=link_url, priority=priority)
        db.session.add(banner)
        db.session.commit()
        return restful.success()
    else:
        return restful.params_error(message=form.get_error())


@bp.route('/ubanner/', methods=['POST'])
@Login_required
@Permission_required(CmsPermission.BANNER)
def ubanner():
    form = UpdateBannerForm(request.form)
    if form.validate():
        banner_id = form.banner_id.data
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner = BannerModel.query.get(banner_id)
        if banner:
            banner.name = name
            banner.image_url = image_url
            banner.link_url = link_url
            banner.priority = priority
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message='没有这个轮播图！')
    else:
        return restful.params_error(message=form.get_error())


@bp.route('/dbanner/', methods=['POST'])
@Login_required
@Permission_required(CmsPermission.BANNER)
def dbanner():
    banner_id = request.form.get('banner_id')
    if not banner_id:
        return restful.params_error(message='请传入轮播图id！')
    banner = BannerModel.query.get(banner_id)
    if not banner:
        return restful.params_error(message='没有这个轮播图')
    db.session.delete(banner)
    db.session.commit()
    return restful.success()


class LoginView(views.MethodView):

    def get(self, message=None):
        return render_template('cms/cms_login.html', message=message)

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            # 数据库查询时，是查询模型对象，也可以针对模型
            # 过滤有两种方法：filter，filter_by,后者的功能比较强大
            user = CmsUser.query.filter(CmsUser.email == email).first()
            if user and user.check_password(password):
                session[config.cms_user_id] = user.id
                if remember:
                    # 如果设置session.permanent = True,那么过期时间是31天
                    session.permanent = True
                return redirect(url_for('cms.index'))
            else:
                return self.get(message='邮箱或密码错误')
        else:
            message = form.get_error()
            return self.get(message=message)


class ResetPwdView(views.MethodView):
    decorators = [Login_required]

    def get(self):
        return render_template('cms/cms_resetpwd.html')

    def post(self):
        # print('hello')
        form = ResetpwdForm(request.form)
        if form.validate():
            oldpassword = form.oldpwd.data
            newpassword = form.newpwd.data
            user = g.cms_user
            if user.check_password(oldpassword):
                user.password = newpassword
                db.session.commit()
                return restful.success()
            else:
                return restful.params_error('旧密码错误')
        else:
            message = form.get_error()
            print('表单错误')
            return restful.params_error(message)


# 以下为zlbbs3代码
class ResetEmailView(views.MethodView):
    decorators = [Login_required]
    def get(self):
        return render_template('cms/cms_resetemail.html')
    def post(self):
        form = ResetemailForm(request.form)
        if form.validate():
            user = CmsUser.query.filter(CmsUser.email == form.email.data).first()
            if not user:
                email = form.email.data
                g.cms_user.email = email
                db.session.commit()
                return restful.success()
            else:
                return restful.params_error('错误，您输入的邮箱已存在！')
        else:
            return restful.params_error(form.get_error())

bp.add_url_rule('/login/',view_func=LoginView.as_view('login'))
bp.add_url_rule('/resetpwd/',view_func=ResetPwdView.as_view('resetpwd'))
bp.add_url_rule('/resetemail/',view_func=ResetEmailView.as_view('resetemail'))