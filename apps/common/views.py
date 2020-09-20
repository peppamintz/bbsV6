from flask import Blueprint, render_template, make_response
from utils.alidayu import sms
from flask import request
from utils import restful
from utils.captcha import Captcha
from .forms import SMSCaptchaForm
from utils.cache import cache
from io import BytesIO


bp = Blueprint('common', __name__, url_prefix='/common')


@bp.route('/')
def index():
    return 'common index'


# @bp.route('/sms_captcha/', methods=['POST'])
# def sms_captcha():
#     telephone = request.args.get('telephone')
#     if not telephone:
#         return restful.params_error(message='请传入手机号码！')
#     captcha = Captcha.gene_text(number=4)
#     print(captcha)
#     # alidayu = SMS("python论坛学习", "SMS_200193302")
#     resp = sms.send(telephone, {'code': captcha})
#     data = sms.convert(resp)
#     if data == 'OK':
#         return restful.success()
#     else:
#         return restful.params_error(message='短信验证码发送失败！')
#     # sms.send('13060867339', {'code': '1234'})
#     # return 'success'


@bp.route('/sms_captcha/', methods=['POST'])
def sms_captcha():
    form = SMSCaptchaForm(request.form)
    if form.validate():
        telephone = form.telephone.data
        captcha = Captcha.gene_text(number=6)
        print('发送的短信验证码是：', captcha)
        resp = sms.send(telephone, {'code': captcha})
        print(resp.decode())
        data = sms.convert(resp)

        if data == 'OK':
            cache.set(telephone, captcha)
            print(cache.get(telephone))
            return restful.success()
        else:
            return restful.params_error(message='短信验证码发送失败！')
    else:
        return restful.params_error(message='参数错误')


@bp.route('/captcha/')
def graph_captcha():
    text, image = Captcha.gene_graph_captcha()
    print('存的key为：', text.lower())
    cache.set(text.lower(), text.lower())
    out = BytesIO()
    image.save(out, 'png')
    out.seek(0)
    resp = make_response(out.read())
    resp.content_type = 'image/png'
    print('取出的值为：', cache.get(text.lower()))
    return resp