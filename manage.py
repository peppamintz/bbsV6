from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from app import app
from exts import db
from apps.cms import models as cms_models
from apps.front import models as front_models
from apps.models import BannerModel, BoardModel, PostModel
import random


manager = Manager(app)

CMSUser = cms_models.CmsUser
CMSRole = cms_models.CmsRole
CMSPermission = cms_models.CmsPermission
FrontUser = front_models.FrontUser

Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
@manager.option('-e', '--email', dest='email')
def create_cms_user(username, password, email):
    user = CMSUser(username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()
    print('cms用户添加成功！')


@manager.command
def create_role():
    # 1.访问者（可以修改个人信息）
    visiter = CMSRole(name='访问者', desc='可以修改个人信息')
    visiter.permissions = CMSPermission.VISITOR

    # 2.运营者（修改个人信息，管理帖子，管理评论，管理前台用户，管理后台用户）
    operator = CMSRole(name='运营者', desc='访问者，管理帖子，管理评论，管理前台用户等权限')
    operator.permissions = CMSPermission.VISITOR|CMSPermission.POSTER|CMSPermission.BOARDER|\
                           CMSPermission. COMMENTER|CMSPermission.FRONTUSER|CMSPermission.BANNER

    # 3.管理员
    admin = CMSRole(name='管理员', desc='拥有本系统所有权限')
    admin.permissions = CMSPermission.VISITOR|CMSPermission.POSTER|CMSPermission.COMMENTER|\
                       CMSPermission.BOARDER|CMSPermission.FRONTUSER|CMSPermission.CMSUSER|CMSPermission.BANNER

    # 4.开发员
    developer = CMSRole(name='开发者', desc='开发者')
    developer.permissions = CMSPermission.ALL_PERMISSION

    db.session.add_all([visiter, operator, admin, developer])
    # db.session.add(operator)
    db.session.commit()


@manager.option('-e', '--email', dest='email')
@manager.option('-n', '--name', dest='name')
def add_user_to_role(email, name):
    user = CMSUser.query.filter(CMSUser.email == email).first()
    if user:
        role = CMSRole.query.filter(CMSRole.name == name).first()
        if role:
            role.users.append(user)
            print(role.users)
            db.session.commit()
            print('用户添加到角色成功！')
        else:
            print('没有这个角色：%s' % role)
    else:
        print('%s邮箱没有这个用户' % email)


@manager.option('-t', '--telephone', dest='telephone')
@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def create_front_user(telephone, username, password):
    user = FrontUser(telephone=telephone, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    print('添加front用户成功！')


@manager.command
def test_permission():
    user = CMSUser.query.filter(CMSUser.email == 'testoperate@qq.com').first()
    if user:
        if user.is_developer:
            print("这个用户拥有开发者权限")
        else:
            print("这个用户没有开发者权限")
    else:
        print('没有这个用户')


@manager.command
def create_test_post():
    numbers = [2, 3, 4, 5, 6]
    for x in range(1,205):
        title = '标题%s' % x
        content = '内容：%s' % x
        post = PostModel(title=title, content=content)
        board_id = random.choice(numbers)
        board = BoardModel.query.get(board_id)
        author = FrontUser.query.first()
        post.board = board
        post.author = author
        db.session.add(post)
        db.session.commit()
    print('测试帖子添加成功！')



if __name__ == '__main__':
    manager.run()