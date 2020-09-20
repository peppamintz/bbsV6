from flask import Blueprint, render_template, views, make_response, request, \
    url_for, session, redirect, g, abort
from utils.captcha import Captcha
from io import BytesIO
from utils.alidayu import sms
from .forms import SignupForm, SigninForm, AddPostFrom, AddCommentForm
from .models import FrontUser
from exts import db
from utils import restful, safeutils
import config
from ..models import BannerModel, BoardModel, PostModel, CommentModel, HighlightPostModel
from .decorators import Login_required
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.sql import func

bp = Blueprint('front', __name__)


@bp.route('/')
def index():
    board_id = request.args.get('bd', type=int, default=None)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    sort = request.args.get('st', type=int, default=1)
    banners = BannerModel.query.order_by(BannerModel.priority.desc()).limit(3)
    boards = BoardModel.query.all()
    start = (page-1)*config.per_page
    end = start + config.per_page
    posts = None
    total = 0

    query_obj = None
    if sort == 1:
        query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 2:
        query_obj = db.session.query(PostModel).outerjoin(HighlightPostModel).\
            order_by(HighlightPostModel.create_time.desc(), PostModel.create_time.desc())
    elif sort == 3:
        query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 4:
        query_obj = db.session.query(PostModel).outerjoin(CommentModel).group_by(PostModel.id)\
            .order_by(func.count(CommentModel.id).desc(), PostModel.create_time.desc())
    if board_id:
        posts = query_obj.filter(PostModel.board_id == board_id).slice(start, end)
        total = query_obj.filter(PostModel.board_id == board_id).count()
        # outer_window,inner_window是调整显示页面标志的样式的
    else:
        posts = query_obj.slice(start, end)
        total = query_obj.count()
    pagination = Pagination(bs_version=3, page=page, total=total,
                            outer_window=0, inner_window=2)
    context = {
        'banners': banners,
        'boards': boards,
        'posts': posts,
        'pagination': pagination,
        'current_board': board_id,
        'current_sort': sort
    }
    return render_template('front/front_index.html', **context)


@bp.route('/apost/', methods=['GET', 'POST'])
@Login_required
def apost():
    if request.method == 'GET':
        boards = BoardModel.query.all()
        return render_template('front/front_apost.html', boards=boards)
    else:
        form = AddPostFrom(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            board = BoardModel.query.get(board_id)
            if not board:
                return restful.params_error(message='没有这个板块')
            post = PostModel(title=title, content=content)
            post.board = board
            post.author = g.front_user
            db.session.add(post)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(message=form.get_error())


@bp.route('/p/<post_id>')
def post_detail(post_id):
    post = PostModel.query.get(post_id)
    if not post:
        abort(404)
    return render_template('front/front_pdetail.html', post=post)


@bp.route('/acomment/', methods=['POST'])
@Login_required
def add_comment():
    form = AddCommentForm(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data
        post = PostModel.query.get(post_id)
        if post:
            comment = CommentModel(content=content)
            comment.post = post
            comment.author = g.front_user
            db.session.add(comment)
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error("没有这篇帖子！")
    else:
        return restful.params_error(form.get_error())


# @bp.route('/captcha/')
# def graph_captcha():
#     text, image = Captcha.gene_graph_captcha()
#     out = BytesIO()
#     image.save(out, 'png')
#     out.seek(0)
#     resp = make_response(out.read())
#     resp.content_type = 'image/png'
#     return resp
#
#
# @bp.route('/sms-captcha/')
# def sms_captcha():
#     result = sms.send('13060867339', {'code': 'asdf'})
#     if result:
#         return '发送成功'
#     else:
#         return '发送失败'


class SignupView(views.MethodView):
    def get(self):
        return_to = request.referrer
        if return_to and return_to != request.url and safeutils.is_safe_url(return_to):
            return render_template("front/front_signup.html", return_to=return_to)
        return render_template("front/front_signup.html")



    def post(self):
        form = SignupForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            username = form.username.data
            password = form.password1.data
            user = FrontUser(telephone=telephone, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return restful.success()
        else:
            print(form.errors)
            return restful.params_error(message=form.get_error())



class SigninView(views.MethodView):
    def get(self):
        return_to = request.referrer
        if return_to and return_to != request.url and safeutils.is_safe_url(return_to):
            return render_template('front/front_signin.html', return_to=return_to)
        else:
            return render_template('front/front_signin.html')

    def post(self):
        form = SigninForm(request.form)
        if form.validate():
            telephone = form.telephone.data
            password = form.password.data
            remember = form.remember.data
            user = FrontUser.query.filter(FrontUser.telephone == telephone).first()
            if user and user.check_password(password):
                session[config.front_user_id] = user.id
                if remember:
                    # 如果设置session.permanent = True
                    # 那么过期时间是31天
                    session.permanent = True
                return restful.success()
            else:

                return restful.params_error(message='手机号或密码错误！')
        else:
            print(form.errors)
            return restful.params_error(message=form.get_error())


bp.add_url_rule('/signup/', view_func=SignupView.as_view('signup'))
bp.add_url_rule('/signin/', view_func=SigninView.as_view('signin'))