# -*- coding: utf-8 -*-

from flask import current_app
from .internals import get_dtiso, id2path, get_book_entry, sizeof_fmt, get_seq_link
from .internals import get_book_link, url_str

import json
import logging
import urllib
import os


def ret_hdr():  # python does not have constants
    return {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:authors",
            "updated": "0000-00-00_00:00",
            "title": "Books by authors",
            "icon": "/favicon.ico",
            "link": [
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/search?searchTerm={searchTerms}",
                    "@rel": "search",
                    "@type": "application/atom+xml"
                },
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }


def main_opds():
    rootdir = current_app.config['STATIC']
    try:
        with open(rootdir + "/index.json") as jsfile:
            data = json.load(jsfile)
        return data
    except Exception as e:
        logging.error(e)
        return None


def opds_str(idx, tag, title, baseref, self, upref, subtag, subtitle):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    workdir = rootdir + "/" + idx
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    try:
        with open(workdir + "/index.json") as jsfile:
            data = json.load(jsfile)
    except Exception as e:
        logging.error(e)
        return ret
    for d in sorted(data):
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(d),
                "title": d,
                "content": {
                    "@type": "text",
                    "#text": subtitle + "'" + d + "'"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(d),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def opds_seq_cnt(idx, tag, title, baseref, self, upref, subtag, subtitle):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    workdir = rootdir + "/" + idx
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    try:
        with open(workdir + "/index.json") as jsfile:
            data = json.load(jsfile)
    except Exception as e:
        logging.error(e)
        return ret
    for d in sorted(data, key = lambda s: s["name"] or -1):
        name = d["name"]
        id = d["id"]
        cnt = d["cnt"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(name),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": subtitle + "'" + name + "'"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(id2path(id)),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def opds_books(idx, tag, title, self, upref, authref, seqref, seq_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    workdir = rootdir + "/" + idx
    try:
        with open(workdir + "/name.json") as nm:
            name = json.load(nm)
            name = "'" + name + "'"
    except Exception as e:
        logging.error(e)
        name = ""
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title + name
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    filename = workdir
    if os.path.isdir(workdir):
        filename = workdir + "/index.json"
    try:
        with open(filename) as jsfile:
            data = json.load(jsfile)
    except Exception as e:
        logging.error(e)
        return ret
    for d in data:
        print(d)
        book_title = d["book_title"]
        book_id = d["book_id"]
        lang = d["lang"]
        annotation = d["annotation"]
        size = int(d["size"])
        date_time = d["date_time"]
        zipfile = d["zipfile"]
        filename = d["filename"]

        authors = []
        links = []
        category = []
        seq_name = ""
        seq_num = ""
        for author in d["authors"]:
            authors.append(
                {
                    "uri": approot + authref + id2path(author["id"]),
                    "name": author["name"]
                }
            )
            links.append(
                {
                    "@href": approot + authref + id2path(author["id"]),
                    "@rel": "related",
                    "@title": author["name"],
                    "@type": "application/atom+xml"
                }
            )

        for seq in d["sequences"]:
            links.append(get_seq_link(approot, seqref, id2path(seq["id"]), seq["name"]))

        links.append(get_book_link(approot, zipfile, filename, 'dl'))
        links.append(get_book_link(approot, zipfile, filename, 'read'))

        annotext = """
        <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
        размер: %s<br/>Серия: %s, номер: %s<br/>
        """ % (annotation, sizeof_fmt(size), seq_name, seq_num)
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    return ret
