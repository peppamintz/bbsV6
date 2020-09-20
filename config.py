#encoding:utf-8
import os

SECRET_KEY = os.urandom(24)
# SECRET_KEY = "fghejikhslalhbgcxz"

DEBUG = True

# PERMANENT_SESSION_LIFETIME = 120

DB_USERNAME = ''       """mysql的用户名"""
DB_PASSWORD = ''       """mysql的密码"""
DB_HOST = '127.0.0.1'
DB_PORT = '3306'
DB_NAME = ''           """数据库名"""

DB_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MIDIFICATIONS = False


cms_user_id = 'shbjkkk'
front_user_id = 'sj'


MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = '587'
MAIL_USE_TLS = True
MAIL_USERNAME = ""    """发送邮件的邮箱"""
MAIL_PASSWORD = " "     """发送邮件的邮箱的密匙"""
MAIL_DEFAULT_SENDER = ""   """默认发送邮件的邮箱"""



# Ueditor的图片上传配置
UEDITOR_UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'files')

# flask-paginate的相关配置
per_page = 10