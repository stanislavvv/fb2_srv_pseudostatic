# -*- coding: utf-8 -*-

from flask import Blueprint, Response
from .opds import main_opds, opds_str, opds_books, opds_seq_cnt
from .validate import validate_prefix

import xmltodict
# import json

opds = Blueprint("opds", __name__)

redir_all = "opds.opds_root"


@opds.route("/opds", methods=['GET'])
@opds.route("/opds/", methods=['GET'])
def opds_root():
    xml = xmltodict.unparse(main_opds(), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/sequencesindex", methods=['GET'])
@opds.route("/opds/sequencesindex/", methods=['GET'])
def opds_seq_root():
    idx = "sequencesindex"
    self = "/opds/sequencesindex/"
    baseref = self
    upref = "/opds/"
    tag = "tag:root:sequences"
    title = "Серии книг"
    subtag = "tag:sequences:"
    subtitle = "Книги на "
    data = opds_str(idx, tag, title, baseref, self, upref, subtag, subtitle)
    print(data)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/sequencesindex/<sub>", methods=['GET'])
def opds_seq_sub(sub):
    sub = validate_prefix(sub)
    data = []
    if len(sub) == 3:
        idx = "sequencesindex/" + sub
        self = "/opds/sequencesindex/" + sub
        baseref = "/opds/sequence/"
        upref = "/opds/sequencesindex/"
        tag = "tag:sequences:" + sub
        title = "Серии книг"
        subtag = "tag:sequences:"
        subtitle = "Книги на "
        data = opds_seq_cnt(idx, tag, title, baseref, self, upref, subtag, subtitle)
    elif len(sub) == 1:
        idx = "sequencesindex/" + sub
        self = "/opds/sequencesindex/" + sub
        upref = "/opds/sequencesindex/"
        baseref = "/opds/sequencesindex/"
        tag = "tag:sequences:" + sub
        title = "Серии на '" + sub + "'"
        subtag = "tag:sequence:"
        subtitle = "Серия "
        data = opds_str(idx, tag, title, baseref, self, upref, subtag, subtitle)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


