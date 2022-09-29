# -*- coding: utf-8 -*-

from flask import Blueprint, Response, render_template
from .opds import main_opds

# import json

html = Blueprint("html", __name__)

redir_all = "html.html_root"


@html.route("/html", methods=['GET'])
@html.route("/html/", methods=['GET'])
def html_root():
    data = main_opds()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')
