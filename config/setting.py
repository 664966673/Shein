# -*- coding: utf-8 -*-
import random
version = random.choice(
            ['31', '32', '33', '34', '35', '36', '37', '38', '39', '51', '52', '53', '54', '55', '56', '57', '58',
             '59'])
browsers = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.' + version + ' (KHTML, like Gecko) Chrome/59.0.30' + version + '.115 Safari/537.' + version,
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:55.' + version + ') Gecko/201' + version + '101 Firefox/55.' + version]

headers = {'User-Agent': random.choice(browsers)}