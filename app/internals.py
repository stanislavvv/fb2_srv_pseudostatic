# -*- coding: utf-8 -*-

import datetime
import urllib


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


# DUMMY, ToDo: rewrite with unicode_upper and some other
# true if sub in s
def is_substr(sub, s):
    if sub in s:
        return True
    return False
