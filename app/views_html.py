# -*- coding: utf-8 -*-

from flask import Blueprint, Response, render_template
from .opds import main_opds, opds_str, opds_seq_cnt, opds_books
from .validate import validate_prefix, validate_id

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


@html.route("/html/sequencesindex", methods=['GET'])
@html.route("/html/sequencesindex/", methods=['GET'])
def html_seq_root():
    idx = "sequencesindex"
    self = "/html/sequencesindex/"
    baseref = self
    upref = "/html/"
    tag = "tag:root:sequences"
    title = "Серии книг"
    subtag = "tag:sequences:"
    subtitle = "Книги на "
    data = opds_str(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/sequencesindex/<sub>", methods=['GET'])
def html_seq_sub(sub):
    sub = validate_prefix(sub)
    data = []
    if len(sub) == 3:
        idx = "sequencesindex/" + sub
        self = "/html/sequencesindex/" + sub
        baseref = "/html/sequence/"
        upref = "/html/sequencesindex/"
        tag = "tag:sequences:" + sub
        title = "Серии книг"
        subtag = "tag:sequences:"
        subtitle = "Книги на "
        data = opds_seq_cnt(idx, tag, title, baseref, self, upref, subtag, subtitle)
    elif len(sub) == 1:
        idx = "sequencesindex/" + sub
        self = "/html/sequencesindex/" + sub
        upref = "/html/sequencesindex/"
        baseref = "/html/sequencesindex/"
        tag = "tag:sequences:" + sub
        title = "Серии на '" + sub + "'"
        subtag = "tag:sequence:"
        subtitle = "Серия "
        data = opds_str(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/sequence/<sub1>/<sub2>/<id>", methods=['GET'])
def html_seq(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "sequence/%s/%s/%s" % (sub1, sub2, id)
    baseref = ""
    self = "/html/" + idx
    upref = "/html/"
    tag = "tag:root:sequence:" + id
    title = "Серия "
    authref = "/html/author/"
    seqref = "/html/sequence/"
    data = opds_books(idx, tag, title, self, upref, authref, seqref, id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')
