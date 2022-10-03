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


def str_list(idx, tag, title, baseref, self, upref, subtag, subtitle):
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


def seq_cnt_list(idx, tag, title, baseref, self, upref, subtag, subtitle):
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
        if os.path.isdir(workdir):
            with open(workdir + "/index.json") as jsfile:
                data = json.load(jsfile)
        else:
            with open(workdir + ".json") as jsfile:
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
                "id": subtag + urllib.parse.quote(id),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": str(cnt) + " книг(и) в серии"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(id2path(id)),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def auth_list(idx, tag, title, baseref, self, upref, subtag, subtitle):
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
        if os.path.isdir(workdir):
            with open(workdir + "/index.json") as jsfile:
                data = json.load(jsfile)
        else:
            with open(workdir + ".json") as jsfile:
                data = json.load(jsfile)
    except Exception as e:
        logging.error(e)
        return ret
    for d in sorted(data, key = lambda s: s["name"] or -1):
        name = d["name"]
        id = d["id"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(id),
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


def books_list(idx, tag, title, self, upref, authref, seqref, seq_id, timeorder=False):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    workdir = rootdir + "/" + idx
    if os.path.isdir(workdir):
        namefile = workdir + "/name.json"
        listfile = workdir + "/index.json"
    else:
        namefile = workdir + ".name.json"
        listfile = workdir + ".json"
    try:
        with open(namefile) as nm:
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
    try:
        with open(listfile) as jsfile:
            data = json.load(jsfile)
    except Exception as e:
        logging.error(e)
        return ret
    if seq_id is not None and not timeorder:
        dfix = []
        for d in data:
            seq_num = -1
            if d["sequences"] is not None:
                for s in d["sequences"]:
                    if s["id"] == seq_id:
                        seq_num = int(s["num"])
            d["seq_num"] = seq_num
            dfix.append(d)
        data = sorted(dfix, key=lambda s: s["seq_num"] or -1)
    elif timeorder:
        data = sorted(data, key=lambda s: s["date_time"])
    else:
        data = sorted(data, key=lambda s: s["book_title"])
    for d in data:
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

        if d["sequences"] is not None:
            for seq in d["sequences"]:
                links.append(get_seq_link(approot, seqref, id2path(seq["id"]), seq["name"]))
                if seq_id is not None:
                    seq_name = seq["name"]
                    seq_num = seq.get("num")
                    if seq_num is None:
                        seq_num = "0"

        links.append(get_book_link(approot, zipfile, filename, 'dl'))
        links.append(get_book_link(approot, zipfile, filename, 'read'))

        if seq_id is not None:
            annotext = """
            <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
            размер: %s<br/>Серия: %s, номер: %s<br/>
            """ % (annotation, sizeof_fmt(size), seq_name, seq_num)
        else:
            annotext = """
            <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
            размер: %s<br/>
            """ % (annotation, sizeof_fmt(size))
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    return ret


def main_author(idx, tag, title, self, upref, authref, seqref, auth_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    workdir = rootdir + "/" + idx
    try:
        with open(workdir + "/name.json") as nm:
            auth_name = json.load(nm)
            auth_name = "'" + auth_name + "'"
    except Exception as e:
        logging.error(e)
        auth_name = ""
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title + auth_name
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
    ret["feed"]["entry"] = [
                {
                    "updated": dtiso,
                    "id": "tag:author:bio:" + auth_id,
                    "title": "Об авторе",
                    "link": [
                        {
                            "@href": approot + "/opds/author/" + id2path(auth_id) + "/sequences",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Books of author by sequences",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        },
                        {
                            "@href": approot + "/opds/author/" + id2path(auth_id) + "/sequenceless",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Sequenceless books of author",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    ],
                    "content": {
                        "@type": "text/html",
                        "#text": "<p><span style=\"font-weight:bold\">" + auth_name + "</span></p>"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequences",
                    "title": "По сериям",
                    "link": {
                        "@href": approot + "/opds/author/" + id2path(auth_id) + "/sequences",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequenceless",
                    "title": "Вне серий",
                    "link": {
                        "@href": approot + "/opds/author/" + id2path(auth_id) + "/sequenceless",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":alphabet",
                    "title": "По алфавиту",
                    "link": {
                        "@href": approot + "/opds/author/" + id2path(auth_id) + "/alphabet",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":time",
                    "title": "По дате добавления",
                    "link": {
                        "@href": approot + "/opds/author/" + id2path(auth_id) + "/time",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            ]
    return ret


def author_seqs(idx, tag, title, baseref, self, upref, authref, seqref, subtag, auth_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    workdir = rootdir + "/" + idx
    try:
        with open(workdir + "/name.json") as nm:
            auth_name = json.load(nm)
            auth_name = "'" + auth_name + "'"
    except Exception as e:
        logging.error(e)
        auth_name = ""
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title + auth_name
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
    workfile = rootdir + "/" + idx + "/sequences.json"
    try:
        with open(workfile) as jsfile:
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
                "id": subtag + urllib.parse.quote(id),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": str(cnt) + " книг(и) в серии"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(id),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def get_main_name(idx):
    ret = ""
    rootdir = current_app.config['STATIC']
    workfile = rootdir + "/" + idx + "/name.json"
    try:
        with open(workfile) as jsfile:
            data = json.load(jsfile)
    except Exception as e:
        logging.error(e)
        return ret
    return data


# for [{name: ..., id: ...}, ...]
def name_list(idx, tag, title, baseref, self, upref, subtag, subtitle):
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
        if os.path.isdir(workdir):
            with open(workdir + "/index.json") as jsfile:
                data = json.load(jsfile)
        else:
            with open(workdir + ".json") as jsfile:
                data = json.load(jsfile)
    except Exception as e:
        logging.error(e)
        return ret
    for d in sorted(data, key = lambda s: s["name"] or -1):
        name = d["name"]
        id = d["id"]
        print(d)
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(str(id)),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": name
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(str(id)),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret
