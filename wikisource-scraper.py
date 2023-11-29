#!/usr/bin/env python3

import sys
import re
import logging
import requests
from bs4 import BeautifulSoup, UnicodeDammit
from wikitextparser import remove_markup, parse

logLevel = logging.INFO

log = logging.getLogger('wikisource-scraper')
log.setLevel(logLevel)
ch = logging.StreamHandler()
ch.setLevel(logLevel)
ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
log.addHandler(ch)

wikisource_url_rex = re.compile(r'^(?:https?://)?[a-z]{2}\.wikisource\.org/wiki/(.*)$')

def get_filename_base(url: str) -> str:
    return url.strip().replace('/','-')

def convert_from_url(url: str):
    match = wikisource_url_rex.match(url)
    if not match :
        log.error("Failed to validate url: " + url)
        return None
    res = requests.get(url)
    try:
        res.raise_for_status()
    except HTTPError as exc:
        log.error("Failed to get " + url + ": " + exc)
        res.close()
        return None
    
    document = BeautifulSoup(res.text, features='lxml')
    text_area = document.body.find('div', id='mw-content-text')
    output_text = text_area.select('div p')
    text = ""
    for p in output_text :
        text += parse(str(p)).plain_text()

    filename_base = match.group(1).strip().replace('/', '-')
    filename = filename_base + ".txt"
    with open(filename, "w") as f:
        f.write(text)
    return filename

if __name__ == '__main__':
    urls = sys.argv[1:]
    for url in urls:
        log.info("Starting conversion for: " + url)
        result = convert_from_url(url)
        if result:
            log.info("Converted " + url + " to text file: " + result)
        else:
            log.warning("Conversion failed for " + url)
    sys.exit(0)
