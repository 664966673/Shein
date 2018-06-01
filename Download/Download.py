# -*- coding: utf-8 -*-
from config import setting
from bs4 import BeautifulSoup
from tool.tools import Tools
import requests

class Download(object):

    def __init__(self):
        self.header = setting.headers
        self.failed_urls = []

    def parse(self, url):
        try:
            response = requests.get(url=url, headers = self.header)
            status = response.status_code
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            html = soup.prettify()
            return html, status
        except Exception as e:
            print(url, e)
            print("-----son-url----------failed-----")
            self.failed_urls.append(url)
            Tools.save_fail_url(url)
