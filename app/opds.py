# -*- coding: utf-8 -*-

from flask import current_app
from .internals import get_dtiso, id2path, get_book_entry, sizeof_fmt, get_seq_link
from .internals import get_book_link, url_str, get_seq_name, genre_names
from .internals import paginate_array, unicode_upper, html_refine, pubinfo_anno, search_words
from .internals import custom_alphabet_sort

import json
# import ijson
import logging
import urllib
import os
import random


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
    approot = current_app.config['APPLICATION_ROOT']
    dtiso = get_dtiso()

    # start data
    data = """
    {
      "feed": {
        "@xmlns": "http://www.w3.org/2005/Atom",
        "@xmlns:dc": "http://purl.org/dc/terms/",
        "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
        "@xmlns:opds": "http://opds-spec.org/2010/catalog",
        "id": "tag:root",
        "title": "Home opds directory",
        "updated": "%s",
        "icon": "/favicon.ico",
        "link": [
          {
            "@href": "%s/opds/search?searchTerm={searchTerms}",
            "@rel": "search",
            "@type": "application/atom+xml"
          },
          {
            "@href": "%s/opds/",
            "@rel": "start",
            "@type": "application/atom+xml;profile=opds-catalog"
          },
          {
            "@href": "%s/opds/",
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
          }
        ],
        "entry": [
          {
            "updated": "%s",
            "id": "tag:root:authors",
            "title": "По авторам",
            "content": {
              "@type": "text",
              "#text": "По авторам"
            },
            "link": {
              "@href": "%s/opds/authorsindex/",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:sequences",
            "title": "По сериям",
            "content": {
              "@type": "text",
              "#text": "По сериям"
            },
            "link": {
              "@href": "%s/opds/sequencesindex/",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:genre",
            "title": "По жанрам",
            "content": {
              "@type": "text",
              "#text": "По жанрам"
            },
            "link": {
              "@href": "%s/opds/genresindex/",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:random:books",
            "title": "Случайные книги",
            "content": {
              "@type": "text",
              "#text": "Случайные книги"
            },
            "link": {
              "@href": "%s/opds/random-books/",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:random:sequences",
            "title": "Случайные серии",
            "content": {
              "@type": "text",
              "#text": "Случайные серии"
            },
            "link": {
              "@href": "%s/opds/random-sequences/",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        ]
      }
    }
    """ % (
        dtiso, approot, approot, approot,
        dtiso, approot,
        dtiso, approot,
        dtiso, approot,
        dtiso, approot,
        dtiso, approot
    )
    return json.loads(data)


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
    for d in custom_alphabet_sort(data):
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
    for d in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
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
    for d in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
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


def books_list(idx, tag, title, self, upref, authref, seqref, seq_id, timeorder=False, page=0, paginate=False):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    workfile = rootdir + "/" + idx + ".json"
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
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
        with open(workfile) as nm:
            data = json.load(nm)
        if seq_id is not None and seq_id != '':
            name = "'" + get_seq_name(seq_id) + "'"
        else:
            name = "'" + data["name"] + "'"
    except Exception as e:
        logging.error(e)
        return ret
    ret["feed"]["title"] = title + name
    data = data["books"]
    if seq_id is not None and seq_id != '' and not timeorder:
        dfix = []
        for d in data:
            seq_num = -1
            if d["sequences"] is not None:
                for s in d["sequences"]:
                    if s.get("id") == seq_id:
                        snum = s.get("num")
                        if snum is not None:
                            seq_num = int(snum)
                        d["seq_num"] = seq_num
                        dfix.append(d)
        data = sorted(dfix, key=lambda s: s["seq_num"] or -1)
    elif timeorder:
        data = sorted(data, key=lambda s: unicode_upper(s["date_time"]))
    elif seq_id is not None and seq_id == '':
        data = sorted(data, key=lambda s: unicode_upper(s["book_title"]))
    else:  # seq_id == None
        dfix = []
        for d in data:
            if d["sequences"] is None:
                dfix.append(d)
        data = sorted(dfix, key=lambda s: unicode_upper(s["book_title"]))
    if paginate:
        data, next = paginate_array(data, page)
        prev = page - 1
        if prev >= 0:
            ret["feed"]["link"].append(
                {
                    "@href": approot + self + "/" + str(prev),
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        if next is not None:
            ret["feed"]["link"].append(
                {
                    "@href": approot + self + "/" + str(next),
                    "@rel": "next",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
    for d in data:
        book_title = d["book_title"]
        book_id = d["book_id"]
        lang = d["lang"]
        annotation = html_refine(d["annotation"])
        size = int(d["size"])
        date_time = d["date_time"]
        zipfile = d["zipfile"]
        filename = d["filename"]
        genres = d["genres"]

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
        for gen in genres:
            category.append(
                {
                    "@label": genre_names[gen],
                    "@term": gen
                }
            )
        if d["sequences"] is not None and d["sequences"] != '-':
            for seq in d["sequences"]:
                s_id = seq.get("id")
                if s_id is not None:
                    links.append(get_seq_link(approot, seqref, id2path(s_id), seq["name"]))
                    if seq_id is not None and seq_id == s_id:
                        seq_name = seq["name"]
                        seq_num = seq.get("num")
                        if seq_num is None:
                            seq_num = "0"

        links.append(get_book_link(approot, zipfile, filename, 'dl'))
        links.append(get_book_link(approot, zipfile, filename, 'read'))

        if seq_id is not None and seq_id != '':
            annotext = """
            <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
            размер: %s<br/>Серия: %s, номер: %s<br/>
            """ % (annotation, sizeof_fmt(size), seq_name, seq_num)
        else:
            annotext = """
            <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
            размер: %s<br/>
            """ % (annotation, sizeof_fmt(size))
        if "pub_info" in d:
            annotext = annotext + pubinfo_anno(d["pub_info"])
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    return ret


def main_author(idx, tag, title, self, upref, authref, seqref, auth_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    workfile = rootdir + "/" + idx + ".json"
    try:
        with open(workfile) as nm:
            auth_data = json.load(nm)
            auth_name = "'" + auth_data["name"] + "'"
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
    workfile = rootdir + "/" + idx + ".json"
    auth_data = {}
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
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
        with open(workfile) as nm:
            auth_data = json.load(nm)
            auth_name = "'" + auth_data["name"] + "'"
    except Exception as e:
        logging.error(e)
        return ret

    ret["feed"]["title"] = title + auth_name
    data = auth_data["sequences"]
    for d in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
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
    workfile = rootdir + "/" + idx + ".json"
    try:
        with open(workfile) as jsfile:
            data = json.load(jsfile)["name"]
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
    for d in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
        name = d["name"]
        id = d["id"]
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


def get_randoms(num, maxrand: int):
    ret = []
    random.seed()
    for i in range(1, num):
        ret.append(random.randint(0, maxrand))
    return ret


# read items with num in nums
def read_data(idx, nums):
    ret = []
    num = 0
    try:
        with open(idx, "rb") as f:
            for b in f:
                if num in nums:
                    d = json.loads(b)
                    ret.append(d)
                num = num + 1
    except Exception as e:
        logging.error(e)
    return ret


def random_data(
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
            books
        ):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    rootdir = current_app.config['STATIC']
    count = current_app.config['PAGE_SIZE']
    workdir = rootdir + "/"
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
    cnt = 0
    cntf = workdir + cntfile
    try:
        with open(cntf) as jsfile:
            cnt = json.load(jsfile)
        randoms = get_randoms(count - 1, cnt)
        dataf = workdir + datafile
        data = read_data(dataf, randoms)
        if books:
            for d in data:
                book_title = d["book_title"]
                book_id = d["book_id"]
                lang = d["lang"]
                annotation = html_refine(d["annotation"])
                size = int(d["size"])
                date_time = d["date_time"]
                zipfile = d["zipfile"]
                filename = d["filename"]
                genres = d["genres"]

                authors = []
                links = []
                category = []
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
                for gen in genres:
                    category.append(
                        {
                            "@label": genre_names[gen],
                            "@term": gen
                        }
                    )

                if d["sequences"] is not None:
                    for seq in d["sequences"]:
                        if seq.get("id") is not None:
                            links.append(get_seq_link(approot, seqref, id2path(seq["id"]), seq["name"]))

                links.append(get_book_link(approot, zipfile, filename, 'dl'))
                links.append(get_book_link(approot, zipfile, filename, 'read'))

                annotext = """
                <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
                размер: %s<br/>
                """ % (annotation, sizeof_fmt(size))
                if "pub_info" in d:
                    annotext = annotext + pubinfo_anno(d["pub_info"])
                ret["feed"]["entry"].append(
                    get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
                )
        else:
            for d in data:
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
                            "@href": approot + seqref + urllib.parse.quote(id2path(id)),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
    except Exception as e:
        logging.error(e)
    return ret


def search_main(s_term, tag, title, baseref, self, upref):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
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
    if s_term is None:
        ret["feed"]["id"] = tag
    else:
        ret["feed"]["id"] = tag + urllib.parse.quote_plus(s_term)
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:authors::",
            "title": "Поиск в именах авторов",
            "content": {
              "@type": "text",
              "#text": "Поиск в именах авторов"
            },
            "link": {
              "@href": approot + baseref + "search-authors?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:sequences::",
            "title": "Поиск в сериях",
            "content": {
              "@type": "text",
              "#text": "Поиск в сериях"
            },
            "link": {
              "@href": approot + baseref + "search-sequences?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:booktitles::",
            "title": "Поиск в названиях книг",
            "content": {
              "@type": "text",
              "#text": "Поиск в названиях книг"
            },
            "link": {
              "@href": approot + baseref + "search-books?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
    return ret


# restype = (auth|seq|book)
def search_term(s_term, idx, tag, title, baseref, self, upref, subtag, restype):
    idx_titles = "allbooktitles.json"
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
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
    if s_term is None:
        ret["feed"]["id"] = tag
    else:
        s_terms = s_term.split()
        ret["feed"]["id"] = tag + urllib.parse.quote_plus(s_term)
        data = []
        try:
            rootdir = current_app.config['STATIC']
            maxres = current_app.config['MAX_SEARCH_RES']
            workdir = rootdir + "/"
            if restype == "book":
                nums = []
                with open(workdir + idx_titles) as f:
                    book_titles = json.load(f)
                    num = 0
                    i = 0
                    for book_id in book_titles:
                        if search_words(s_terms, book_titles[book_id]):
                            nums.append(num)
                            i = i + 1
                        num = num + 1  # next book No in index
                        if i >= maxres:
                            break
                data = read_data(workdir + idx, nums)
            else:
                with open(workdir + idx, "rb") as f:
                    i = 0
                    for line in f:
                        d = json.loads(line)
                        # dummy if in current searches set:
                        # if restype == "auth" or restype == "seq":
                        if search_words(s_terms, d["name"]):
                            data.append(d)
                            i = i + 1
                        if i >= maxres:
                            break
            if restype == "auth" or restype == "seq":
                data = sorted(data, key=lambda s: unicode_upper(s["name"]) or -1)
            elif restype == "book":
                data = sorted(data, key=lambda s: unicode_upper(s["book_title"]) or -1)
        except Exception as e:
            logging.error(e)
        for d in data:
            if restype == "auth":
                name = d["name"]
                id = d["id"]
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": subtag + urllib.parse.quote(id),
                        "title": name,
                        "content": {
                            "@type": "text",
                            "#text": name
                        },
                        "link": {
                            "@href": approot + baseref + id2path(id),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
            elif restype == "seq":
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
            elif restype == "book":
                book_title = d["book_title"]
                book_id = d["book_id"]
                lang = d["lang"]
                annotation = html_refine(d["annotation"])
                size = int(d["size"])
                date_time = d["date_time"]
                zipfile = d["zipfile"]
                filename = d["filename"]
                genres = d["genres"]

                authors = []
                links = []
                category = []
                for author in d["authors"]:
                    authors.append(
                        {
                            "uri": approot + baseref + id2path(author["id"]),
                            "name": author["name"]
                        }
                    )
                    links.append(
                        {
                            "@href": approot + baseref + id2path(author["id"]),
                            "@rel": "related",
                            "@title": author["name"],
                            "@type": "application/atom+xml"
                        }
                    )

                for gen in genres:
                    category.append(
                        {
                            "@label": genre_names[gen],
                            "@term": gen
                        }
                    )
                if d["sequences"] is not None:
                    for seq in d["sequences"]:
                        if seq.get("id") is not None:
                            links.append(get_seq_link(approot, baseref, id2path(seq["id"]), seq["name"]))

                links.append(get_book_link(approot, zipfile, filename, 'dl'))
                links.append(get_book_link(approot, zipfile, filename, 'read'))

                annotext = """
                <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
                размер: %s<br/>
                """ % (annotation, sizeof_fmt(size))
                if "pub_info" in d:
                    annotext = annotext + pubinfo_anno(d["pub_info"])
                ret["feed"]["entry"].append(
                    get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
                )
    return ret
