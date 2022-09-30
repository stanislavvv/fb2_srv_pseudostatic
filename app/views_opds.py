# -*- coding: utf-8 -*-

from flask import Blueprint, Response
from .opds import main_opds, str_list, books_list, seq_cnt_list, auth_list, main_author
from .opds import author_seqs
from .validate import validate_prefix, validate_id

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
    data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
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
        data = seq_cnt_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    elif len(sub) == 1:
        idx = "sequencesindex/" + sub
        self = "/opds/sequencesindex/" + sub
        upref = "/opds/sequencesindex/"
        baseref = "/opds/sequencesindex/"
        tag = "tag:sequences:" + sub
        title = "Серии на '" + sub + "'"
        subtag = "tag:sequence:"
        subtitle = "Серия "
        data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/sequence/<sub1>/<sub2>/<id>", methods=['GET'])
def opds_seq(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "sequence/%s/%s/%s" % (sub1, sub2, id)
    baseref = ""
    self = "/opds/" + idx
    upref = "/opds/"
    tag = "tag:root:sequence:" + id
    title = "Серия "
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/authorsindex", methods=['GET'])
@opds.route("/opds/authorsindex/", methods=['GET'])
def opds_auth_root():
    idx = "authorsindex"
    self = "/opds/authorsindex/"
    baseref = self
    upref = "/opds/"
    tag = "tag:root:authors"
    title = "Авторы"
    subtag = "tag:authors:"
    subtitle = "Авторы на "
    data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    print(data)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/authorsindex/<sub>", methods=['GET'])
def opds_auth_sub(sub):
    sub = validate_prefix(sub)
    data = []
    if len(sub) == 3:
        idx = "authorsindex/" + sub
        self = "/opds/authorsindex/" + sub
        baseref = "/opds/author/"
        upref = "/opds/authorsindex/"
        tag = "tag:authors:" + sub
        title = "Авторы на '" + sub + "'"
        subtag = "tag:authors:"
        subtitle = "Авторы на "
        data = auth_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    elif len(sub) == 1:
        idx = "authorsindex/" + sub
        self = "/opds/authorsindex/" + sub
        upref = "/opds/authorsindex/"
        baseref = "/opds/authorsindex/"
        tag = "tag:authors:" + sub
        title = "Авторы на '" + sub + "'"
        subtag = "tag:author:"
        subtitle = ""
        data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<sub1>/<sub2>/<id>", methods=['GET'])
def opds_author(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    baseref = ""
    self = "/opds/" + idx
    upref = "/opds/authorsindex/"
    tag = "tag:root:author:" + id
    title = "Автор "
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    data = main_author(idx, tag, title, self, upref, authref, seqref, id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<sub1>/<sub2>/<id>/sequences", methods=['GET'])
def opds_author_seqs(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/opds/" + idx
    baseref = self + "/"
    upref = "/opds/authorsindex/"
    tag = "tag:root:author:" + id
    title = "Серии автора "
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    subtag = "tag:author:" + id + ":sequence:"
    data = author_seqs(idx, tag, title, baseref, self, upref, authref, seqref, subtag, id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')
