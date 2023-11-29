#!/usr/bin/env python3

import sys
import re
import logging
import requests
from bs4 import BeautifulSoup, UnicodeDammit
from wikitextparser import remove_markup, parse
import os

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
    title = document.find('title').string
    if title:
        print(title)
    else:
        print("No title found")
        return None
    text_area = document.body.find('div', id='mw-content-text')
    output_text = text_area.select('div p')
    text = 'Title: "' + title.split(" - Wikisource")[0] + '"\n\n'
    skip = ["talk page"]
    stop = ["public domain"]
    for p in output_text :
        if any(x in p.get_text().lower() for x in stop):
            break
        elif any(x in p.get_text().lower() for x in skip):
            continue
        text += p.get_text()
    if not text:
        print("No text found")
        return None
    filename = title.replace(" ","_") + ".txt"
    with open(os.path.join("outputs",filename), "w") as f:
        f.write(text)
    return filename

if __name__ == '__main__':
    urls = sys.argv[1:]
    if len(urls) == 0:
        while True:
            log.info("No urls provided; pulling random page from wikisource")
            result = convert_from_url("https://en.wikisource.org/wiki/Special:RandomRootpage/Main")
            if result:
                log.info("Converted random page to text file: " + result)
                break
            else:
                log.warning("Conversion failed for random page")
    for url in urls:
        log.info("Starting conversion for: " + url)
        result = convert_from_url(url)
        if result:
            log.info("Converted " + url + " to text file: " + result)
    if not result:
        log.warning("Conversion failed for " + url)
    sys.exit(0)
