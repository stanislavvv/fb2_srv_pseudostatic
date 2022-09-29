# -*- coding: utf-8 -*-

from flask import Blueprint, Response
from .opds import main_opds

import xmltodict
# import json

opds = Blueprint("opds", __name__)

redir_all = "opds.opds_root"


@opds.route("/opds", methods=['GET'])
@opds.route("/opds/", methods=['GET'])
def opds_root():
    xml = xmltodict.unparse(main_opds(), pretty=True)
    return Response(xml, mimetype='text/xml')
