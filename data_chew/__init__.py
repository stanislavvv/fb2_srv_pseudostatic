# -*- coding: utf-8 -*-

import os
import zipfile
import xmltodict
# import sqlite3
import json
import logging
import glob

from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

from .strings import get_genres, get_genres_meta, get_genres_replace, genres
from .strings import genres_replace, check_genres, id2path, get_genre_meta, get_meta_name

from .data import get_genre, get_author_struct
from .data import get_sequence, get_lang
from .data import get_struct_by_key, make_id, get_replace_list, replace_book
from .data import get_title, seqs_in_data, seq_from_data, nonseq_from_data
from .inpx import get_inpx_meta

READ_SIZE = 20480  # description in 20kb...
INPX = "flibusta_fb2_local.inpx"  # filename of metadata indexes zip

# start data
ROOT = """
{
  "feed": {
    "@xmlns": "http://www.w3.org/2005/Atom",
    "@xmlns:dc": "http://purl.org/dc/terms/",
    "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
    "@xmlns:opds": "http://opds-spec.org/2010/catalog",
    "id": "tag:root",
    "title": "Home opds directory",
    "updated": "2022-09-29T18:46:35+05:00",
    "icon": "/favicon.ico",
    "link": [
      {
        "@href": "/opds/search?searchTerm={searchTerms}",
        "@rel": "search",
        "@type": "application/atom+xml"
      },
      {
        "@href": "/opds/",
        "@rel": "start",
        "@type": "application/atom+xml;profile=opds-catalog"
      },
      {
        "@href": "/opds/",
        "@rel": "self",
        "@type": "application/atom+xml;profile=opds-catalog"
      }
    ],
    "entry": [
      {
        "updated": "2022-09-29T18:46:35+05:00",
        "id": "tag:root:authors",
        "title": "По авторам",
        "content": {
          "@type": "text",
          "#text": "По авторам"
        },
        "link": {
          "@href": "/opds/authorsindex/",
          "@type": "application/atom+xml;profile=opds-catalog"
        }
      },
      {
        "updated": "2022-09-29T18:46:35+05:00",
        "id": "tag:root:sequences",
        "title": "По сериям",
        "content": {
          "@type": "text",
          "#text": "По сериям"
        },
        "link": {
          "@href": "/opds/sequencesindex/",
          "@type": "application/atom+xml;profile=opds-catalog"
        }
      },
      {
        "updated": "2022-09-29T18:46:35+05:00",
        "id": "tag:root:genre",
        "title": "По жанрам",
        "content": {
          "@type": "text",
          "#text": "По жанрам"
        },
        "link": {
          "@href": "/opds/genres/",
          "@type": "application/atom+xml;profile=opds-catalog"
        }
      },
      {
        "updated": "2022-09-29T18:46:35+05:00",
        "id": "tag:root:random:books",
        "title": "Случайные книги",
        "content": {
          "@type": "text",
          "#text": "Случайные книги"
        },
        "link": {
          "@href": "/opds/random-books/",
          "@type": "application/atom+xml;profile=opds-catalog"
        }
      },
      {
        "updated": "2022-09-29T18:46:35+05:00",
        "id": "tag:root:random:sequences",
        "title": "Случайные серии",
        "content": {
          "@type": "text",
          "#text": "Случайные серии"
        },
        "link": {
          "@href": "/opds/random-sequences/",
          "@type": "application/atom+xml;profile=opds-catalog"
        }
      }
    ]
  }
}
"""

book_idx = {}


def create_booklist(inpx_data, zip_file):
    booklist = zip_file + ".list"
    list = ziplist(inpx_data, zip_file)
    bl = open(booklist, 'w')
    bl.write(json.dumps(list, ensure_ascii=False))
    bl.close()


def update_booklist(inpx_data, zip_file):
    booklist = zip_file + ".list"
    replacelist = zip_file + ".replace"
    if os.path.exists(booklist):
        ziptime = os.path.getmtime(zip_file)
        listtime = os.path.getmtime(booklist)
        replacetime = 0
        if os.path.exists(replacelist):
            replacetime = os.path.getmtime(replacelist)
        if ziptime < listtime and replacetime < listtime:
            return False
    create_booklist(inpx_data, zip_file)
    return True


# get filename in opened zip (assume filename format as fb2), return book struct
def fb2parse(z, filename, replace_data, inpx_data):
    file_info = z.getinfo(filename)
    fb2dt = datetime(*file_info.date_time)
    date_time = fb2dt.strftime("%F_%H:%M")
    size = file_info.file_size
    if size < 1000:
        return None
    fb2 = z.open(filename)
    bs = BeautifulSoup(bytes(fb2.read(READ_SIZE)), 'xml')
    bs_descr = bs.FictionBook.description
    tinfo = bs_descr.find("title-info")
    bs_anno = str(tinfo.annotation)
    bs_anno = bs_anno.replace("<annotation>", "").replace("</annotation>", "")
    doc = bs.prettify()
    data = xmltodict.parse(doc)
    if 'FictionBook' not in data:  # parse with namespace
        data = xmltodict.parse(
            doc,
            process_namespaces=True,
            namespaces={'http://www.gribuser.ru/xml/fictionbook/2.0': None}
        )
    if 'FictionBook' not in data:  # not fb2
        logging.error("not fb2: %s " % filename)
        return None
    fb2data = get_struct_by_key('FictionBook', data)  # data['FictionBook']
    descr = get_struct_by_key('description', fb2data)  # fb2data['description']
    info = get_struct_by_key('title-info', descr)  # descr['title-info']
    if isinstance(info, list):
        # see f.fb2-513034-516388.zip/513892.fb2
        info = info[0]
    if inpx_data is not None and filename in inpx_data:
        info = replace_book(filename, info, inpx_data)
    if replace_data is not None and filename in replace_data:
        info = replace_book(filename, info, replace_data)

    if "date_time" in info and info["date_time"] is not None:
        date_time = str(info["date_time"])
    if 'genre' in info and info['genre'] is not None:
        genre = get_genre(info['genre'])
    else:
        genre = ""
    author = [{"name": '--- unknown ---', "id": make_id('--- unknown ---')}]
    if 'author' in info and info['author'] is not None:
        author = get_author_struct(info['author'])
    sequence = None
    if 'sequence' in info and info['sequence'] is not None:
        sequence = get_sequence(info['sequence'])
    book_title = ''
    if 'book-title' in info and info['book-title'] is not None:
        book_title = get_title(info['book-title'])
    lang = ''
    if 'lang' in info and info['lang'] is not None:
        lang = get_lang(info['lang'])
    annotext = ''
    if 'annotation' in info and info['annotation'] is not None:
        annotext = bs_anno
    book_path = str(os.path.basename(z.filename)) + "/" + filename
    book_id = make_id(book_path)
    out = {
        "zipfile": str(os.path.basename(z.filename)),
        "filename": filename,
        "genres": genre,
        "authors": author,
        "sequences": sequence,
        "book_title": str(book_title),
        "book_id": book_id,
        "lang": str(lang),
        "date_time": date_time,
        "size": str(size),
        "annotation": str(annotext.replace('\n', " ").replace('|', " "))
    }
    return out


# iterate over files in zip, return array of book struct
def ziplist(inpx_data, zip_file):
    logging.info(zip_file)
    ret = []
    z = zipfile.ZipFile(zip_file)
    replace_data = get_replace_list(zip_file)
    inpx_data = get_inpx_meta(inpx_data, zip_file)
    for filename in z.namelist():
        if not os.path.isdir(filename):
            logging.debug(zip_file + "/" + filename + "             ")
            res = fb2parse(z, filename, replace_data, inpx_data)
            if res is not None:
                ret.append(res)
    return ret


def make_root(pagesdir):
    logging.info("Making root...")
    Path(pagesdir).mkdir(parents=False, exist_ok=True)
    with open(pagesdir + "/index.json", "w") as idx:
        idx.write(ROOT)


def process_list(booklist):
    with open(booklist) as lst:
        data = json.load(lst)
    for book in data:
        book_id = book["book_id"]
        book_idx[book_id] = book


def make_authors(pagesdir):
    auth_base = "/authorsindex/"  # for author indexes
    auth_data_base = "/author/"
    auth_names = {}
    auth_idx = {}
    auth_root = {}
    auth_subroot = {}
    auth_data = {}
    allbooks = []
    for book in book_idx:
        bdata = book_idx[book]
        allbooks.append(bdata)
        if bdata["authors"] is not None:
            for auth in bdata["authors"]:
                auth_id = auth["id"]
                auth_name = auth["name"]
                auth_names[auth_id] = auth_name
                if auth_id not in auth_idx:
                    s = {"name": auth_name, "id": auth_id}
                    auth_idx[auth_id] = s
                if auth_id in auth_data:
                    s = auth_data[auth_id]
                    s.append(bdata)
                    auth_data[auth_id] = s
                else:
                    s = []
                    s.append(bdata)
                    auth_data[auth_id] = s
    with open(pagesdir + "/allbooks.json", 'w') as idx:
        json.dump(allbooks, idx, indent=2, ensure_ascii=False)
    for auth in auth_names:
        name = auth_names[auth]
        first = name[:1]
        three = name[:3]
        auth_root[first] = 1
        if first in auth_subroot:
            s = auth_subroot[first]
            if three in s:
                s[three].append(auth)
            else:
                s[three] = []
                s[three].append(auth)
            auth_subroot[first] = s
        else:
            s = {}
            s[three] = []
            s[three].append(auth)
            auth_subroot[first] = s
        workpath = pagesdir + auth_data_base + id2path(auth)
        Path(workpath).mkdir(parents=True, exist_ok=True)
        data = auth_data[auth]
        with open(workpath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        with open(workpath + "/name.json", 'w') as idx:
            json.dump(name, idx, indent=2, ensure_ascii=False)
        nonseqs = nonseq_from_data(auth_data[auth])
        with open(workpath + "/sequenceless.json", 'w') as idx:
            json.dump(nonseqs, idx, indent=2, ensure_ascii=False)
        seqs = seqs_in_data(auth_data[auth])
        with open(workpath + "/sequences.json", 'w') as idx:
            json.dump(seqs, idx, indent=2, ensure_ascii=False)
        for seq in seqs:
            auth_seq = seq_from_data(seq["id"], auth_data[auth])
            listfile = "/%s.json" % seq["id"]
            namefile = "/%s.name.json" % seq["id"]
            with open(workpath + listfile, 'w') as idx:
                json.dump(auth_seq, idx, indent=2, ensure_ascii=False)
            with open(workpath + namefile, 'w') as idx:
                json.dump(seq['name'], idx, indent=2, ensure_ascii=False)
    for first in sorted(auth_root.keys()):
        workpath = pagesdir + auth_base + first
        Path(workpath).mkdir(parents=True, exist_ok=True)
        data = []
        for d in auth_subroot[first]:
            data.append(d)
        with open(workpath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        for three in auth_subroot[first]:
            s = auth_subroot[first]
            wpath = pagesdir + auth_base + three
            Path(wpath).mkdir(parents=True, exist_ok=True)
            out = []
            for auth_id in s[three]:
                auth = auth_idx[auth_id]
                out.append(auth)
            with open(wpath + "/index.json", 'w') as idx:
                json.dump(out, idx, indent=2, ensure_ascii=False)
    workpath = pagesdir + auth_base
    data = []
    for s in auth_root:
        data.append(s)
    with open(workpath + "/index.json", 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)


def make_sequences(pagesdir):
    seq_base = "/sequencesindex/"  # for sequence indexes
    seq_data_base = "/sequence/"  # for sequence data
    seq_names = {}
    seq_idx = {}
    seq_root = {}
    seq_subroot = {}
    seq_data = {}
    for book in book_idx:
        bdata = book_idx[book]
        if bdata["sequences"] is not None:
            for seq in bdata["sequences"]:
                seq_id = seq["id"]
                seq_name = seq["name"]
                seq_names[seq_id] = seq_name
                if seq_id in seq_idx:
                    s = seq_idx[seq_id]
                    count = s["cnt"]
                    count = count + 1
                    s["cnt"] = count
                    seq_idx[seq_id] = s
                else:
                    s = {"name": seq_name, "id": seq_id, "cnt": 1}
                    seq_idx[seq_id] = s
                if seq_id in seq_data:
                    s = seq_data[seq_id]
                    s.append(bdata)
                    seq_data[seq_id] = s
                else:
                    s = []
                    s.append(bdata)
                    seq_data[seq_id] = s
    allseqs = []
    for seq in seq_names:
        allseqs.append(seq_idx[seq])
        name = seq_names[seq]
        first = name[:1]
        three = name[:3]
        seq_root[first] = 1
        if first in seq_subroot:
            s = seq_subroot[first]
            if three in s:
                s[three].append(seq)
            else:
                s[three] = []
                s[three].append(seq)
            seq_subroot[first] = s
        else:
            s = {}
            s[three] = []
            s[three].append(seq)
            seq_subroot[first] = s
        workpath = pagesdir + seq_data_base + id2path(seq)
        Path(workpath).mkdir(parents=True, exist_ok=True)
        data = seq_data[seq]
        with open(workpath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        with open(workpath + "/name.json", 'w') as idx:
            json.dump(name, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allsequences.json", 'w') as idx:
        json.dump(allseqs, idx, indent=2, ensure_ascii=False)
    for first in sorted(seq_root.keys()):
        workpath = pagesdir + seq_base + first
        Path(workpath).mkdir(parents=True, exist_ok=True)
        data = []
        for d in seq_subroot[first]:
            data.append(d)
        with open(workpath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        for three in seq_subroot[first]:
            s = seq_subroot[first]
            wpath = pagesdir + seq_base + three
            Path(wpath).mkdir(parents=True, exist_ok=True)
            out = []
            for seq_id in s[three]:
                seq = seq_idx[seq_id]
                out.append(seq)
            with open(wpath + "/index.json", 'w') as idx:
                json.dump(out, idx, indent=2, ensure_ascii=False)
    workpath = pagesdir + seq_base
    data = []
    for s in seq_root:
        data.append(s)
    with open(workpath + "/index.json", 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)


def make_genres(pagesdir):
    gen_base = "/genresindex/"  # for genre indexes
    gen_data_base = "/genre/"  # for genre data
    gen_names = {}
    gen_idx = {}
    gen_root = {}
    gen_subroot = {}
    gen_data = {}

    workpath = pagesdir + gen_base
    genpath_base = pagesdir + gen_data_base

    for book in book_idx:
        bdata = book_idx[book]
        if bdata["genres"] is not None:
            for gen in bdata["genres"]:
                gen_id = gen
                gen_name = gen
                if gen in genres:
                    gen_name = genres[gen]["descr"]
                gen_names[gen_id] = gen_name
                if gen_id in gen_idx:
                    s = gen_idx[gen_id]
                    count = s["cnt"]
                    count = count + 1
                    s["cnt"] = count
                    gen_idx[gen_id] = s
                else:
                    s = {"name": gen_name, "id": gen_id, "cnt": 1}
                    gen_idx[gen_id] = s
                if gen_id in gen_data:
                    s = gen_data[gen_id]
                    s.append(bdata)
                    gen_data[gen_id] = s
                else:
                    s = []
                    s.append(bdata)
                    gen_data[gen_id] = s
    for gen in gen_names:
        name = gen_names[gen]
        meta_id = get_genre_meta(gen)
        if meta_id not in gen_root:
            gen_root[meta_id] = []
        gen_root[meta_id].append({"name": name, "id": gen})
        genpath = genpath_base + gen
        Path(genpath).mkdir(parents=True, exist_ok=True)
        data = gen_data[gen]
        with open(genpath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        with open(genpath + "/name.json", 'w') as idx:
            json.dump(name, idx, indent=2, ensure_ascii=False)
        meta_name = get_meta_name(meta_id)
    for meta in gen_root:
        metapath = workpath + "/" + str(meta)
        Path(metapath).mkdir(parents=True, exist_ok=True)
        data = gen_root[meta]
        with open(metapath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        meta_name = get_meta_name(meta_id)
        with open(metapath + "/name.json", 'w') as idx:
            json.dump(meta_name, idx, indent=2, ensure_ascii=False)
        meta_name = get_meta_name(meta_id)
    data = []
    for meta_id in gen_root:
        meta_name = get_meta_name(meta_id)
        s = {"name": meta_name, "id": meta_id}
        data.append(s)
    with open(workpath + "/index.json", 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)


def process_lists(zipdir, pagesdir):
    logging.info("Prerocessing lists...")
    get_genres_meta()
    get_genres()  # official genres from genres.list
    get_genres_replace()  # replacement for unofficial genres from genres_replace.list

    i = 0
    for booklist in glob.glob(zipdir + '/*.zip.list'):
        logging.info("[" + str(i) + "] ")
        process_list(booklist)
        i = i + 1
    make_sequences(pagesdir)
    make_authors(pagesdir)
    make_genres(pagesdir)
