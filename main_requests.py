#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from pprint import pprint
from bs4 import BeautifulSoup

url = 'https://www.google.es/'
page_response = requests.get(url)

soup = BeautifulSoup(page_response.text)
scripts = [ elem.get('src') for elem in soup.find_all('script') if elem.get('src') != None ]
links = [ link.get('href') for link in soup.find_all('link') ]
imgs_urls = [ img.get('src') for img in soup.find_all('img') ]

refs = scripts + links + imgs_urls
refs = [ elem for elem in refs if "ens" in elem]
pprint(refs)