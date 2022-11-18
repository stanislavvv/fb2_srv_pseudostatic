# -*- coding: utf-8 -*-

import os
import zipfile
import xmltodict
import json
import logging

from bs4 import BeautifulSoup
from datetime import datetime

from .strings import get_genres, get_genres_meta, get_genres_replace

from .data import get_genre, get_author_struct, get_sequence, get_lang, get_title
from .data import get_struct_by_key, make_id, get_replace_list, replace_book
from .data import get_pub_info

from .inpx import get_inpx_meta

from .idx import auth_processed, seq_processed, gen_processed  # vars
from .idx import make_global_indexes, make_auth_data, make_auth_subindexes
from .idx import make_seq_data, make_seq_subindexes
from .idx import make_gen_data, make_gen_subindexes

READ_SIZE = 20480  # description in 20kb...
INPX = "flibusta_fb2_local.inpx"  # filename of metadata indexes zip


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
    zip_file = str(os.path.basename(z.filename))
    fb2dt = datetime(*file_info.date_time)
    date_time = fb2dt.strftime("%F_%H:%M")
    size = file_info.file_size
    if size < 1000:
        return None, None
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
        logging.error("not fb2: %s/%s " % (zip_file, filename))
        return None, None
    fb2data = get_struct_by_key('FictionBook', data)  # data['FictionBook']
    descr = get_struct_by_key('description', fb2data)  # fb2data['description']
    info = get_struct_by_key('title-info', descr)  # descr['title-info']
    pubinfo = None
    try:
        pubinfo = get_struct_by_key('publish-info', descr)  # descr['publish-info']
    except:  # get_struct_by_key must return None without stacktrace
        logging.debug("No publish info in %s/%s" % (zip_file, filename))
    if isinstance(pubinfo, list):
        pubinfo = pubinfo[0]
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
        sequence = get_sequence(info['sequence'], zip_file, filename)
    book_title = ''
    if 'book-title' in info and info['book-title'] is not None:
        book_title = get_title(info['book-title'])
    lang = ''
    if 'lang' in info and info['lang'] is not None:
        lang = get_lang(info['lang'])
    annotext = ''
    if 'annotation' in info and info['annotation'] is not None:
        annotext = bs_anno

    isbn, pub_year, publisher = get_pub_info(pubinfo)
    pub_info = {
        "isbn": isbn,
        "year": pub_year,
        "publisher": publisher,
        "publisher_id": make_id(publisher)
    }
    book_path = str(os.path.basename(z.filename)) + "/" + filename
    book_id = make_id(book_path)
    out = {
        "zipfile": zip_file,
        "filename": filename,
        "genres": genre,
        "authors": author,
        "sequences": sequence,
        "book_title": str(book_title),
        "book_id": book_id,
        "lang": str(lang),
        "date_time": date_time,
        "size": str(size),
        "annotation": str(annotext.replace('\n', " ").replace('|', " ")),
        "pub_info": pub_info
    }
    return book_id, out


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
            book_id, res = fb2parse(z, filename, replace_data, inpx_data)
            if res is not None:
                ret.append(res)
    return ret


def process_lists(zipdir, pagesdir, stage):
    get_genres_meta()
    get_genres()
    get_genres_replace()
    if stage == "global":
        make_global_indexes(zipdir, pagesdir)
    elif stage == "authors":
        with open(pagesdir + "/allauthorcnt.json") as f:
            auth_cnt = json.load(f)
        logging.info("Creating authors indexes (total: %d)..." % auth_cnt)
        while(len(auth_processed) < auth_cnt):
            make_auth_data(pagesdir)
            logging.debug(" - processed authors: %d/%d" % (len(auth_processed), auth_cnt))
        make_auth_subindexes(pagesdir)
    elif stage == "sequences":
        with open(pagesdir + "/allsequencecnt.json") as f:
            seq_cnt = json.load(f)
        logging.info("Creating sequences indexes (total: %d)..." % seq_cnt)
        while(len(seq_processed) < seq_cnt):
            make_seq_data(pagesdir)
            logging.debug(" - processed sequences: %d/%d" % (len(seq_processed), seq_cnt))
        make_seq_subindexes(pagesdir)
    elif stage == "genres":
        with open(pagesdir + "/allgenrecnt.json") as f:
            gen_cnt = json.load(f)
        logging.info("Creating genres indexes (total: %s)..." % gen_cnt)
        while(len(gen_processed) < gen_cnt):
            make_gen_data(pagesdir)
            logging.debug(" - processed genres: %d/%d" % (len(gen_processed), gen_cnt))
        make_gen_subindexes(pagesdir)
