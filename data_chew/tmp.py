# -*- coding: utf-8 -*-

def make_authors(pagesdir):
    auth_base = "/authorsindex/"  # for author indexes
    auth_data_base = "/author/"
    auth_names = {}
    auth_idx = {}
    auth_root = {}
    auth_subroot = {}
    auth_data = {}
    allbookscnt = 0
    logging.debug(" - processing books...")
    for book in book_idx:
        bdata = book_idx[book]
        allbookscnt = allbookscnt + 1
        if bdata["authors"] is not None:
            for auth in bdata["authors"]:
                auth_id = auth.get("id")
                if auth_id is not None:
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
    logging.debug(" - saving global indexes...")
    with open(pagesdir + "/allbooks.json", 'w') as idx:
        json.dump({"data": book_idx}, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allauthors.json", 'w') as idx:
        json.dump({"data": auth_idx}, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allbookscnt.json", 'w') as idx:
        json.dump(allbookscnt, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allauthorcnt.json", 'w') as idx:
        json.dump(len(auth_names), idx, indent=2, ensure_ascii=False)
    logging.debug(" - processing author names...")
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
    logging.debug(" - saving partial indexes...")
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
    logging.debug(" - saving main authors index...")
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
    logging.debug(" - processing books...")
    for book in book_idx:
        bdata = book_idx[book]
        if bdata["sequences"] is not None:
            for seq in bdata["sequences"]:
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
    seq_cnt = 0
    logging.debug(" - processing sequences names")
    for seq in seq_names:
        seq_cnt = seq_cnt + 1
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
        workpath = pagesdir + seq_data_base + id2path(seq)
        Path(workpath).mkdir(parents=True, exist_ok=True)
        data = seq_data[seq]
        with open(workpath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        with open(workpath + "/name.json", 'w') as idx:
            json.dump(name, idx, indent=2, ensure_ascii=False)
    logging.debug(" - saving global indexes...")
    with open(pagesdir + "/allsequences.json", 'w') as idx:
        json.dump({"data": seq_idx}, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allsequencecnt.json", 'w') as idx:
        json.dump(seq_cnt, idx, indent=2, ensure_ascii=False)
    logging.debug(" - saving partial indexes...")
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
    Path(workpath).mkdir(parents=True, exist_ok=True)
    data = []
    for s in seq_root:
        data.append(s)
    logging.debug(" - saving sequence root index...")
    with open(workpath + "/index.json", 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)


def make_genres(pagesdir):
    gen_base = "/genresindex/"  # for genre indexes
    gen_data_base = "/genre/"  # for genre data
    gen_names = {}
    gen_idx = {}
    gen_root = {}
    gen_data = {}

    workpath = pagesdir + gen_base
    genpath_base = pagesdir + gen_data_base

    logging.debug(" - processing books...")
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
    logging.debug(" - processing genres names...")
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
    logging.debug(" - processing genres metas...")
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
    logging.debug(" - saving main genres index...")
    with open(workpath + "/index.json", 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)
