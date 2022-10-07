# -*- coding: utf-8 -*-

import json
import logging
import glob

from pathlib import Path

from .data import seqs_in_data, nonseq_from_data
from .strings import get_genres, get_genres_meta, get_genres_replace, unicode_upper
from .strings import genres_replace, id2path, id2pathonly

MAX_PASS_LENGTH = 1000

book_idx = {}
book_cnt = 0
seq_idx = {}
seq_cnt = 0
seq_processed = {}
auth_idx = {}
auth_cnt = 0
auth_processed = {}


def process_list_books(fd, booklist):
    global book_cnt
    with open(booklist) as lst:
        data = json.load(lst)
    for book in data:
        book["genres"] = genres_replace(book["genres"])
        # fd.send(book)
        fd.write(json.dumps(book, ensure_ascii=False))
        fd.write("\n")
        book_cnt = book_cnt + 1
        if book["sequences"] is not None:
            for seq in book["sequences"]:
                seq_id = seq.get("id")
                if seq_id is not None:
                    seq_name = seq["name"]
                    if seq_id in seq_idx:
                        s = seq_idx[seq_id]
                        count = s["cnt"]
                        count = count + 1
                        s["cnt"] = count
                        seq_idx[seq_id] = s
                    else:
                        s = {"name": seq_name, "id": seq_id, "cnt": 1}
                        seq_idx[seq_id] = s
        if book["authors"] is not None:
            for auth in book["authors"]:
                auth_id = auth.get("id")
                if auth_id is not None:
                    if auth_id not in auth_idx:
                        auth_name = auth["name"]
                        s = {"name": auth_name, "id": auth_id}
                        auth_idx[auth_id] = s


def make_global_indexes(zipdir, pagesdir):
    global seq_cnt
    global auth_cnt

    logging.info("Preprocessing lists...")
    get_genres_meta()
    get_genres()  # official genres from genres.list
    get_genres_replace()  # replacement for unofficial genres from genres_replace.list

    Path(pagesdir).mkdir(parents=True, exist_ok=True)
    bookindex = pagesdir + "/allbooks.json"
    with open(bookindex, "w") as fd_idx:
        i = 0
        logging.info("Collecting books to united index...")
        for booklist in glob.glob(zipdir + '/*.zip.list'):
            logging.info("[" + str(i) + "] " + booklist)
            process_list_books(fd_idx, booklist)
            i = i + 1
    with open(pagesdir + "/allbookcnt.json", 'w') as idx:
        json.dump(book_cnt, idx, indent=2, ensure_ascii=False)
    seqindex = pagesdir + "/allsequences.json"
    logging.info("Writing sequences index...")
    with open(seqindex, "w") as fd:
        for seq in seq_idx:
            fd.write(json.dumps(seq_idx[seq], ensure_ascii=False))
            fd.write("\n")
            seq_cnt = seq_cnt + 1

    with open(pagesdir + "/allsequencecnt.json", 'w') as idx:
        json.dump(seq_cnt, idx, indent=2, ensure_ascii=False)
    authindex = pagesdir + "/allauthors.json"
    logging.info("Writing authors index...")
    with open(authindex, "w") as fd:
        for auth in auth_idx:
            fd.write(json.dumps(auth_idx[auth], ensure_ascii=False))
            fd.write("\n")
            auth_cnt = auth_cnt + 1
    with open(pagesdir + "/allauthorcnt.json", 'w') as idx:
        json.dump(auth_cnt, idx, indent=2, ensure_ascii=False)


def make_auth_data(pagesdir):
    auth_data = {}
    booksindex = pagesdir + "/allbooks.json"
    with open(booksindex) as f:
        for b in f:
            book = json.loads(b)
            if book["authors"] is not None:
                for auth in book["authors"]:
                    auth_id = auth.get("id")
                    auth_name = auth.get("name")
                    if auth_id not in auth_processed:
                        if auth_id in auth_data:
                            s = auth_data[auth_id]["books"]
                            s.append(book)
                            auth_data[auth_id]["books"] = s
                        elif len(auth_data) < MAX_PASS_LENGTH:
                            s = {"name": auth_name, "id": auth_id}
                            b = []
                            b.append(book)
                            s["books"] = b
                            auth_data[auth_id] = s
    for auth_id in auth_data:
        data = auth_data[auth_id]
        data["sequences"] = seqs_in_data(auth_data[auth_id]["books"])
        data["nonseq_book_ids"] = nonseq_from_data(auth_data[auth_id]["books"])
        workdir = pagesdir + "/authors/" + id2pathonly(auth_id)
        workfile = pagesdir + "/authors/" + id2path(auth_id) + ".json"
        Path(workdir).mkdir(parents=True, exist_ok=True)
        with open(workfile, 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        auth_processed[auth_id] = 1


def make_auth_subindexes(zipdir, pagesdir):
    auth_base = "/authorsindex/"
    auth_names = {}
    auth_root = {}
    auth_subroot = {}
    booksindex = pagesdir + "/allbooks.json"
    with open(booksindex) as f:
        for b in f:
            book = json.loads(b)
            if book["authors"] is not None:
                for auth in book["authors"]:
                    auth_id = auth.get("id")
                    auth_name = auth.get("name")
                    if auth_id not in auth_processed:
                        if auth_id not in auth_names:
                            auth_names[auth_id] = auth_name
    for auth in auth_names:
        name = auth_names[auth]
        first = unicode_upper(name[:1])
        three = unicode_upper(name[:3])
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
    logging.debug(" - partial names index tree...")
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
                auth_name = auth_names[auth_id]
                auth = {"id": auth_id, "name": auth_name}
                out.append(auth)
            with open(wpath + "/index.json", 'w') as idx:
                json.dump(out, idx, indent=2, ensure_ascii=False)
    workpath = pagesdir + auth_base
    data = []
    for s in auth_root:
        data.append(s)
    logging.debug(" - saving main authors index...")
    with open(workpath + "/index.json", 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)


def make_seq_data(pagesdir):
    seq_idx = {}
    seq_data = {}
    booksindex = pagesdir + "/allbooks.json"
    with open(booksindex) as f:
        for b in f:
            book = json.loads(b)
            if book["sequences"] is not None:
                for seq in book["sequences"]:
                    seq_id = seq.get("id")
                    if seq_id is not None:
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
    for seq_id in seq_data:
        data = seq_data[seq_id]
        data["sequences"] = seqs_in_data(seq_data[seq_id]["books"])
        data["nonseq_book_ids"] = nonseq_from_data(seq_data[seq_id]["books"])
        workdir = pagesdir + "/sequences/" + id2pathonly(seq_id)
        workfile = pagesdir + "/sequences/" + id2path(seq_id) + ".json"
        Path(workdir).mkdir(parents=True, exist_ok=True)
        with open(workfile, 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        seq_processed[seq_id] = 1


def make_seq_subindexes(zipdir, pagesdir):
    seq_base = "/sequencesindex/"
    seq_names = {}
    seq_root = {}
    seq_subroot = {}
    seqindex = pagesdir + "/allsequences.json"
    with open(seqindex) as f:
        for s in f:
            seq = json.loads(s)
            seq_id = seq["id"]
            seq_name = seq["name"]
            seq_names[seq_id] = seq_name
    for seq in seq_names:
        name = seq_names[seq]
        first = unicode_upper(name[:1])
        three = unicode_upper(name[:3])
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
    logging.debug(" - partial names index tree...")
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
                seq_name = seq_names[seq_id]
                seq = {"id": seq_id, "name": seq_name}
                out.append(seq)
            with open(wpath + "/index.json", 'w') as idx:
                json.dump(out, idx, indent=2, ensure_ascii=False)
    workpath = pagesdir + seq_base
    data = []
    for s in seq_root:
        data.append(s)
    logging.debug(" - saving main sequences index...")
    with open(workpath + "/index.json", 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)
