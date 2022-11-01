# -*- coding: utf-8 -*-

import zipfile
import lxml.etree as ET
from bs4 import BeautifulSoup
import io
from flask import current_app

xslt = ''
transform = ''


def init_xslt(xsltfile):
    global xslt
    global transform
    xslt = ET.parse(xsltfile)
    transform = ET.XSLT(xslt)


def fb2_out(zip_file: str, filename: str):
    zipdir = current_app.config['ZIPS']
    zippath = zipdir + "/" + zip_file
    try:
        data = ""
        with zipfile.ZipFile(zippath) as z:
            with z.open(filename) as fb2:
                data = io.BytesIO(fb2.read())
        return data
    except Exception as e:
        print(e)
        return None


def html_out(zip_file: str, filename: str):
    zipdir = current_app.config['ZIPS']
    zippath = zipdir + "/" + zip_file
    try:
        with zipfile.ZipFile(zippath) as z:
            with z.open(filename) as fb2:
                data = io.BytesIO(fb2.read())
                bs = BeautifulSoup(data, 'xml')
                doc = bs.prettify()
                dom = ET.fromstring(bytes(doc, encoding='utf8'))
                html = transform(dom)
                return str(html)
    except Exception as e:
        print(e)
        return None
