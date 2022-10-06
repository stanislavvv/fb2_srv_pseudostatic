# -*- coding: utf-8 -*-

from flask import Blueprint, Response
from .opds import main_opds, str_list, seq_cnt_list, books_list, auth_list, main_author
from .opds import author_seqs, get_main_name, name_list, random_data
from .validate import validate_prefix, validate_id, validate_genre_meta, validate_genre
from .internals import id2path

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
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<sub1>/<sub2>/<id>/<seq_id>", methods=['GET'])
def opds_author_seq(sub1, sub2, id, seq_id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    seq_id = validate_id(seq_id)
    idx = "author/%s/%s/%s/%s" % (sub1, sub2, id, seq_id)
    self = "/opds/" + idx
    upref = "/opds/author/%s/%s/%s" % (sub1, sub2, id)
    tag = "tag:root:author:" + id + ":sequence:" + seq_id
    idx2 = "author/%s/%s/%s" % (sub1, sub2, id)
    title = "Автор '" + get_main_name(idx2) + "', серия "
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, seq_id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<sub1>/<sub2>/<id>/sequenceless", methods=['GET'])
def opds_author_nonseq(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s/%s" % (sub1, sub2, id, "sequenceless")
    self = "/opds/" + idx
    upref = "/opds/author/" + id2path(id)
    tag = "tag:root:author:" + id
    idx2 = "author/%s/%s/%s" % (sub1, sub2, id)
    title = "Книги вне серий автора '" + get_main_name(idx2) + "'"
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, None)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<sub1>/<sub2>/<id>/alphabet", methods=['GET'])
def opds_author_alphabet(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/opds/" + idx
    upref = "/opds/author/" + id2path(id)
    tag = "tag:root:author:" + id + ":alphabet"
    title = "Книги по алфавиту автора "
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, None)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<sub1>/<sub2>/<id>/time", methods=['GET'])
def opds_author_time(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/opds/" + idx
    upref = "/opds/author/" + id2path(id)
    tag = "tag:root:author:" + id + ":time"
    title = "Книги по дате добавления, автор "
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, None, True)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/genresindex", methods=['GET'])
@opds.route("/opds/genresindex/", methods=['GET'])
def opds_gen_root():
    idx = "genresindex"
    self = "/opds/genresindex/"
    baseref = self
    upref = "/opds/"
    tag = "tag:root:genres"
    title = "Группы жанров"
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/genresindex/<sub>", methods=['GET'])
def opds_gen_meta(sub):
    sub = validate_genre_meta(sub)
    data = []
    idx = "genresindex/" + sub
    self = "/opds/genresindex/" + sub
    baseref = "/opds/genre/"
    upref = "/opds/genresindex/"
    tag = "tag:genres:" + sub
    title = "Жанры"
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/genre/<id>", methods=['GET'])
def opds_genre(id):
    id = validate_genre(id)
    idx = "genre/%s" % (id)
    self = "/opds/" + idx
    upref = "/opds/"
    tag = "tag:root:genre:" + id
    title = "Серия "
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/random-books/", methods=['GET'])
def opds_random_books():
    baseref = ""  # not for books
    self = "/opds/random-books/"
    upref = "/opds/"
    tag = "tag:search:books:random:"
    title = "Поиск случайных книг"
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    datafile = "allbooks.json"
    cntfile = "allbookscnt.json"
    subtag = ""  # not for books
    data = random_data(
                datafile,
                cntfile,
                tag,
                title,
                baseref,
                self,
                upref,
                authref,
                seqref,
                subtag,
                True)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/random-sequences/", methods=['GET'])
def opds_random_seqs():
    baseref = "/opds/"
    self = "/opds/random-sequences/"
    upref = "/opds/"
    tag = "tag:search:sequences:random:"
    title = "Поиск случайных серий"
    authref = "/opds/author/"
    seqref = "/opds/sequence/"
    datafile = "allsequences.json"
    cntfile = "allsequencecnt.json"
    subtag = "tag:sequence:"
    data = random_data(
                datafile,
                cntfile,
                tag,
                title,
                baseref,
                self,
                upref,
                authref,
                seqref,
                subtag,
                False)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')
