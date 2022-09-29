#!/usr/bin/env python3

import sys
import json
import xmltodict
from bs4 import BeautifulSoup

doc = open(sys.argv[1])
# xml_dict = xmltodict.parse(doc)
bs = BeautifulSoup(doc, 'xml')
xml = bs.prettify()
xml_dict = xmltodict.parse(xml)
print(json.dumps(xml_dict, indent=2, ensure_ascii=False))
