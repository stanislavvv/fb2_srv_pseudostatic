# -*- coding: utf-8 -*-

from flask import current_app
from bs4 import BeautifulSoup
import logging
import datetime
import urllib
import json
import os
import unicodedata as ud

genre_names = {}


# custom UPPER + normalize for sqlite and other
def unicode_upper(s: str):
    ret = ud.normalize('NFKD', s)
    ret = ret.upper()
    ret = ret.replace('Ё', 'Е')
    ret = ret.replace('Й', 'И')
    ret = ret.replace('Ъ', 'Ь')
    return ret


def get_dtiso():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def id2path(id: str):
    first = id[:2]
    second = id[2:4]
    return first + "/" + second + "/" + id


def get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext):
    ret = {
        "updated": date_time,
        "id": "tag:book:" + book_id,
        "title": book_title,
        "author": authors,
        "link": links,
        "category": category,
        "dc:language": lang,
        "dc:format": "fb2",
        "content": {
            "@type": "text/html",
            "#text": annotext
        }
    }
    return ret


# 123456 -> 123k, 1234567 -> 1.23M
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_seq_link(approot, seqref, seq_id, seq_name):
    ret = {
        "@href": approot + seqref + seq_id,
        "@rel": "related",
        "@title": "Серия '" + seq_name + "'",
        "@type": "application/atom+xml"
    }
    return ret


# ctype == 'dl' for download
def get_book_link(approot, zipfile, filename, ctype):
    title = "Читать онлайн"
    book_ctype = "text/html"
    rel = "alternate"
    href = approot + "/read/" + zipfile + "/" + url_str(filename)
    if ctype == 'dl':
        title = "Скачать"
        book_ctype = "application/fb2+zip"
        rel = "http://opds-spec.org/acquisition/open-access"
        href = approot + "/fb2/" + zipfile + "/" + url_str(filename)
    ret = {
        "@href": href,
        "@rel": rel,
        "@title": title,
        "@type": book_ctype
    }
    return ret


# urlencode string (quote + replace some characters to %NN)
def url_str(s):
    tr = {
        '"': '%22',
        "'": '%27',
        # '.': '%2E',
        # '/': '%2F'
    }
    ret = ''
    if s is not None:
        for c in s:
            if c in tr:
                c = tr[c]
            ret = ret + c
    return urllib.parse.quote(ret, encoding='utf-8')


# true if sub in s
def is_substr(sub, s):
    sub_up = unicode_upper(sub)
    s_up = unicode_upper(s)
    if sub_up in s_up:
        return True
    return False


def get_seq_name(seq_id):
    ret = ""
    rootdir = current_app.config['STATIC']
    seqidx = rootdir + "/allsequences.json"
    with open(seqidx) as f:
        for line in f:
            seq = json.loads(line)
            if seq["id"] == seq_id:
                ret = seq["name"]
                break
    return ret


def load_genres(pagesdir):
    global genre_names
    genidx = pagesdir + "/allgenres.json"
    if os.path.exists(genidx):
        try:
            with open(genidx) as f:
                for g in f:
                    genre = json.loads(g)
                    genre_names[genre["id"]] = genre["name"]
        except Exception as e:
            logging.error(e)


def paginate_array(data, page: int):
    pagesize = int(current_app.config['PAGE_SIZE'])
    begin = page * pagesize
    end = (page + 1)*pagesize
    ret = data[begin:end]
    next = page + 1
    if len(ret) < pagesize:
        next = None
    return ret, next


# ToDo: mostly close tags
def html_refine(txt):
    ht = BeautifulSoup(txt, 'html.parser')
    ret = ht.prettify()
    return ret


def pubinfo_anno(pubinfo):
    ret = ""
    if pubinfo["isbn"] is not None:
        ret = ret + "<p><b>Данные публикации:</b></p><p>ISBN: %s</p>" % pubinfo["isbn"]
    if pubinfo["year"] is not None:
        ret = ret + "<p>Год: %s</p>" % pubinfo["year"]
    if pubinfo["publisher"] is not None:
        ret = ret + "<p>Издательство: %s</p>" % pubinfo["publisher"]
    return ret
