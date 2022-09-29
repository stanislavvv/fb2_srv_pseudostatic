# -*- coding: utf-8 -*-

from flask import current_app
import json
import logging


def main_opds():
    rootdir = current_app.config['STATIC']
    try:
        with open(rootdir + "/index.json") as jsfile:
            data = json.load(jsfile)
        return data
    except Exception as e:
        logging.error(e)
        return None
