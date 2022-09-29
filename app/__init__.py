# -*- coding: utf-8 -*-

from flask import Flask
from .config import config, SELECTED_CONFIG
from .views_dl import dl
from .get_fb2 import init_xslt


def create_app():
    global xslt
    app = Flask(__name__, static_url_path='/st')
    app.config.from_object(config[SELECTED_CONFIG])
    app.register_blueprint(dl, url_prefix=app.config['APPLICATION_ROOT'])
    xslt = init_xslt(app.config['FB2_XSLT'])
    return app
