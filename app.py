from flask import Flask
from apps.cms.views import bp as cms_bp
from apps.front.views import bp as front_bp
from apps.common.views import bp as common_bp
from exts import db, mail
import config
import apps.cms.hooks
import apps.front.hook
from flask_wtf import CSRFProtect
from utils.captcha import Captcha
from apps.ueditor.ueditor import bp as ueditor_bp



app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

app.register_blueprint(cms_bp)
app.register_blueprint(front_bp)
app.register_blueprint(common_bp)
app.register_blueprint(ueditor_bp)

CSRFProtect(app)
mail.init_app(app)
# alidayu.init_app(app)

Captcha.gene_graph_captcha()


if __name__ == '__main__':
    app.run(port=9000, debug=True)
