# -*- coding: utf-8 -*-

from flask import Blueprint, Response, render_template, request
from .opds import main_opds, str_list, seq_cnt_list, books_list, auth_list, main_author
from .opds import author_seqs, get_main_name, name_list, random_data
from .opds import search_main, search_term
from .validate import validate_prefix, validate_id, validate_genre_meta, validate_genre, validate_search
from .internals import id2path

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
    data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
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
        data = seq_cnt_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    elif len(sub) == 1:
        idx = "sequencesindex/" + sub
        self = "/html/sequencesindex/" + sub
        upref = "/html/sequencesindex/"
        baseref = "/html/sequencesindex/"
        tag = "tag:sequences:" + sub
        title = "Серии на '" + sub + "'"
        subtag = "tag:sequence:"
        subtitle = "Серия "
        data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
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
    self = "/html/" + idx
    upref = "/html/"
    tag = "tag:root:sequence:" + id
    title = "Серия "
    authref = "/html/author/"
    seqref = "/html/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/authorsindex", methods=['GET'])
@html.route("/html/authorsindex/", methods=['GET'])
def html_auth_root():
    idx = "authorsindex"
    self = "/html/authorsindex/"
    baseref = self
    upref = "/html/"
    tag = "tag:root:authors"
    title = "Авторы"
    subtag = "tag:authors:"
    subtitle = "Авторы на "
    data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/authorsindex/<sub>", methods=['GET'])
def html_auth_sub(sub):
    sub = validate_prefix(sub)
    data = []
    if len(sub) == 3:
        idx = "authorsindex/" + sub
        self = "/html/authorsindex/" + sub
        baseref = "/html/author/"
        upref = "/html/authorsindex/"
        tag = "tag:authors:" + sub
        title = "Авторы на '" + sub + "'"
        subtag = "tag:authors:"
        subtitle = "Авторы на "
        data = auth_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    elif len(sub) == 1:
        idx = "authorsindex/" + sub
        self = "/html/authorsindex/" + sub
        upref = "/html/authorsindex/"
        baseref = "/html/authorsindex/"
        tag = "tag:authors:" + sub
        title = "Авторы на '" + sub + "'"
        subtag = "tag:author:"
        subtitle = ""
        data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<sub1>/<sub2>/<id>", methods=['GET'])
def html_author(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/html/" + idx
    upref = "/html/authorsindex/"
    tag = "tag:root:author:" + id
    title = "Автор "
    authref = "/html/author/"
    seqref = "/html/sequence/"
    data = main_author(idx, tag, title, self, upref, authref, seqref, id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_main.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<sub1>/<sub2>/<id>/sequences", methods=['GET'])
def html_author_seqs(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/html/" + idx
    baseref = self + "/"
    upref = "/html/authorsindex/"
    tag = "tag:root:author:" + id
    title = "Серии автора "
    authref = "/html/author/"
    seqref = "/html/sequence/"
    subtag = "tag:author:" + id + ":sequence:"
    data = author_seqs(idx, tag, title, baseref, self, upref, authref, seqref, subtag, id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<sub1>/<sub2>/<id>/<seq_id>", methods=['GET'])
def html_author_seq(sub1, sub2, id, seq_id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    seq_id = validate_id(seq_id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/html/" + idx
    upref = "/html/author/%s/%s/%s" % (sub1, sub2, id)
    tag = "tag:root:author:" + id + ":sequence:" + seq_id
    idx2 = "author/%s/%s/%s" % (sub1, sub2, id)
    title = "Автор '" + get_main_name(idx2) + "', серия "
    authref = "/html/author/"
    seqref = "/html/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, seq_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<sub1>/<sub2>/<id>/sequenceless", methods=['GET'])
def html_author_nonseq(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/html/" + idx
    upref = "/html/author/" + id2path(id)
    tag = "tag:root:author:" + id
    idx2 = "author/%s/%s/%s" % (sub1, sub2, id)
    title = "Книги вне серий автора '" + get_main_name(idx2) + "'"
    authref = "/html/author/"
    seqref = "/html/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, None)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<sub1>/<sub2>/<id>/alphabet", methods=['GET'])
def html_author_alphabet(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/html/" + idx
    upref = "/html/author/" + id2path(id)
    tag = "tag:root:author:" + id + ":alphabet"
    title = "Книги по алфавиту автора "
    authref = "/html/author/"
    seqref = "/html/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, '')
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<sub1>/<sub2>/<id>/time", methods=['GET'])
def html_author_time(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = "/html/" + idx
    upref = "/html/author/" + id2path(id)
    tag = "tag:root:author:" + id + ":time"
    title = "Книги по дате добавления, автор "
    authref = "/html/author/"
    seqref = "/html/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, None, True)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/genresindex", methods=['GET'])
@html.route("/html/genresindex/", methods=['GET'])
def html_gen_root():
    idx = "genresindex"
    self = "/html/genresindex/"
    baseref = self
    upref = "/html/"
    tag = "tag:root:genres"
    title = "Группы жанров"
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/genresindex/<sub>", methods=['GET'])
def html_gen_meta(sub):
    sub = validate_genre_meta(sub)
    data = []
    idx = "genresindex/" + sub
    self = "/html/genresindex/" + sub
    baseref = "/html/genre/"
    upref = "/html/genresindex/"
    tag = "tag:genres:" + sub
    title = "Жанры"
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/genre/<id>", methods=['GET'])
@html.route("/html/genre/<id>/<int:page>", methods=['GET'])
def html_genre(id, page=0):
    id = validate_genre(id)
    idx = "genre/%s" % (id)
    self = "/html/" + idx
    upref = "/html/"
    tag = "tag:root:genre:" + id
    title = "Жанр "
    authref = "/html/author/"
    seqref = "/html/sequence/"
    data = books_list(idx, tag, title, self, upref, authref, seqref, '', False, page, True)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/random-books/", methods=['GET'])
def html_random_books():
    baseref = ""  # not for books
    self = "/html/random-books/"
    upref = "/html/"
    tag = "tag:search:books:random:"
    title = "Поиск случайных книг"
    authref = "/html/author/"
    seqref = "/html/sequence/"
    datafile = "allbooks.json"
    cntfile = "allbookcnt.json"
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/random-sequences/", methods=['GET'])
def html_random_seqs():
    baseref = "/html/"
    self = "/html/random-sequences/"
    upref = "/html/"
    tag = "tag:search:sequences:random:"
    title = "Поиск случайных серий"
    authref = "/html/author/"
    seqref = "/html/sequence/"
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search", methods=['GET'])
def html_search():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    baseref = "/html/"
    self = "/html/search"
    upref = "/html/"
    tag = "tag:search::"
    title = "Поиск по '" + s_term + "'"
    data = search_main(s_term, tag, title, baseref, self, upref)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search-authors", methods=['GET'])
def html_search_authors():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    idx = "allauthors.json"
    baseref = "/html/author/"
    self = "/html/search-authors"
    upref = "/html/"
    tag = "tag:search:authors:"
    subtag = "tag:author:"
    title = "Поиск среди авторов по '" + s_term + "'"
    data = search_term(s_term, idx, tag, title, baseref, self, upref, subtag, "auth")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search-sequences", methods=['GET'])
def html_search_sequences():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    idx = "allsequences.json"
    baseref = "/html/sequence/"
    self = "/html/search-sequences"
    upref = "/html/"
    tag = "tag:search:sequences:"
    subtag = "tag:sequence:"
    title = "Поиск среди серий по '" + s_term + "'"
    data = search_term(s_term, idx, tag, title, baseref, self, upref, subtag, "seq")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search-books", methods=['GET'])
def html_search_books():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    idx = "allbooks.json"
    baseref = "/html/book/"
    self = "/html/search-books"
    upref = "/html/"
    tag = "tag:search:books:"
    subtag = "tag:book:"
    title = "Поиск среди книг по '" + s_term + "'"
    data = search_term(s_term, idx, tag, title, baseref, self, upref, subtag, "book")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')
