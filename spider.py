# -*- coding: utf-8 -*-
from config import setting
from tool import tool
import requests
from bs4 import BeautifulSoup
import random
import time
from lxml import etree
import json
import data_process, son_data_process
import csv

class Spider(object):

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
            tool.tools.save_fail_url(url)

class GetProduct(Spider):

    def detail(self, file):
        pro_num = 1
        urls = tool.tools.get_url(file)
        for url in urls:
            self.resolution(url)
            print(">>" + str(pro_num) + "------product-over--------")
            ProductCheck = tool.tools.ProductCheck(url)
            if ProductCheck == 0:
                time.sleep(random.choice(range(5, 10)))
            pro_num += 1
            #break
        print('all-products----over')

    def resolution(self, url):
        c = super(GetProduct, self).parse(url)
        html = c[0]
        status = c[1]
        ProductCheck = tool.tools.ProductCheck(url)
        if ProductCheck == 0:
            if status == 200:
                tree = etree.HTML(html)
                pid = tool.tools.get_id(url)[0]
                cid = tool.tools.get_id(url)[1]
                title = tree.xpath("//div[@class='goodsd-right col-sm-5']//h4/text()")
                title = "".join(title).strip()
                price = tool.tools.get_price(pid)[0]
                orig_price = tool.tools.get_price(pid)[1]
                description = tree.xpath("//div[@class='goodsd-right col-sm-5']//div[@class='kv']/div//text()")
                description = [x.strip() for x in description if x != '\n          ']
                description = [x for x in description if x != '']
                description = "\n".join(description)

                size_fits = tree.xpath("//table[@class='kv']")[0]
                del size_fits.attrib['class']
                for size_fit in size_fits:
                    del size_fit.attrib['class']
                    for i in size_fit:
                        # keys(1)
                        del i.attrib['class']
                        i.set('valign', '321')
                        del i.attrib['valign']
                        i.set('colspan', '321')
                        del i.attrib['colspan']
                    # print(size_fit)
                    # list_size.append(size_fit)

                size_fits = etree.tostring(size_fits)
                size_fits = size_fits.decode().replace('\n', '')
                sku = tree.xpath("//div[@class='summary']/span[@class='sku']/text()")
                sku = "".join(sku).replace(' ', '').replace('\n', '').replace('SKU:', '')
                review = tree.xpath("//div[@class='comments']/a/span/text()")
                review = "".join(review).strip('\n').replace(' ', '')
                sizes = tool.tools.get_size(pid)
                if review == '':
                    review = 0

                img_urls = tree.xpath("//div[@class='swiper-wrapper']/div/img/@data-src")

                # img_counts = tree.xpath("//div[@class='vertical-wrap']/img/@data-src")
                color_urls = tree.xpath("//div[@class='opt-color']/a/@href")
                color_imgs = tree.xpath("//div[@class='opt-color']/a/@style")
                # 判断是否有相同的id
                ProductCheckSku = tool.tools.ProductCheck(sku)
                if ProductCheckSku == 0:
                    # 判断是否有多个颜色
                    this_url = url
                    if color_urls:
                        color_urls = color_urls[1:]
                        for color_url in color_urls:
                            color_url = color_url + ''
                            # color_url = str(color_url.encode('UTF-8'))
                            self.son_resolution(color_url, pid)
                    data_process.get_data(pid, cid, this_url, title, price, orig_price, description, size_fits, sku,
                                          review, img_urls, color_urls, color_imgs, sizes)

        else:
             print("-----Parent-url-repetition-----")

    def son_resolution(self, color_url, parent_pid):
        url = tool.tools.add_url(color_url)
        c = super(GetProduct, self).parse(url)
        html = c[0]
        status = c[1]
        ProductCheck = tool.tools.ProductCheck(url)
        if ProductCheck == 0:
            if status == 200:
                tree = etree.HTML(html)
                parent_id = int(parent_pid)
                pid = tool.tools.get_id(url)[0]
                cid = tool.tools.get_id(url)[1]
                title = tree.xpath("//div[@class='goodsd-right col-sm-5']//h4/text()")
                title = "".join(title).strip()
                price = tool.tools.get_price(pid)[0]
                orig_price = tool.tools.get_price(pid)[1]
                sku = tree.xpath("//div[@class='summary']/span[@class='sku']/text()")
                sku = "".join(sku).replace(' ', '').replace('\n', '').replace('SKU:', '')
                review = tree.xpath("//div[@class='comments']/a/span/text()")
                review = "".join(review).replace('\n', '').replace(' ', '')
                if review == '':
                    review = 0
                img_urls = tree.xpath("//div[@class='swiper-wrapper']/div/img/@data-src")
                sizes = tool.tools.get_size(pid)
                ProductCheckSku = tool.tools.ProductCheck(sku)
                if ProductCheckSku == 0:
                    son_data_process.get_data(parent_id, pid, cid, url, title, price, orig_price, sku, review, img_urls,
                                              sizes)
        else:
            print("-----son-url-repetition-----")


class GetTag(Spider):

    def pro_list(self, TagName, url, pages):
        url_list = []
        for i in range(1, pages):
            page_urls = url + "&page=" + str(i)
            c = super(GetTag, self).parse(page_urls)
            html = c[0]
            status = c[1]

            if status == 200:
                tree = etree.HTML(html)
                products = tree.xpath("//div[@class='gds-li-ratiowrap']/a/@href")
                # print(products)
                url_list.append(products)
        url_list = [y for x in url_list for y in x]
        self.getData(url_list, TagName)

    def getData(self, url_list, TagName):
        for each in url_list:
            each = each + ' '
            TagName = str(TagName)
            TagName = "".join(TagName).strip()

            pid = tool.tools.get_id(each)[0]
            pid = int(pid)
            url = tool.tools.add_url(each)
            # 判断产品表中是否存在tag的产品，如果不存在，就将其写入products
            # 如果存在, 判断是否存在parent_id = 0
            ProductCheckPid = tool.tools.ProductCheckPid(pid)
            if ProductCheckPid == False:
                pro_spider = GetProduct()
                pro_spider.resolution(url)
            elif ProductCheckPid != 0:
                pid = str(ProductCheckPid)
                url = tool.tools.relace_pid(pid, url)

            if tool.tools.TagNameCheck(TagName, pid) == True:
                self.saveData(TagName, pid, url)
                # print("kaishi")
            else:
                print('---tag----repetition---')
        print(TagName + 'cate---over')

    def saveData(self, TagName, pid, url):
        table = "m2b_tags"
        db = tool.tools.connect_mysql()
        cursor = db.cursor()

        sql = 'INSERT INTO {table} ' \
              'VALUES ("%s", "%s", "%s")'.format(table=table) % (TagName, pid, url)

        try:
            cursor.execute(sql)
            db.commit()
            print("tag---------ok")
        except Exception as e:
            db.rollback()
            print("----MYSQL--failed-------" + url, e)
            self.failed_urls.append(url)
            print(self.failed_urls)

        db.close()

    def getTag(self, pages, tag):
        with open(tag + '.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                TagName = row[0]
                cate_url = row[1]
                self.pro_list(TagName, cate_url, pages)
                # print(row)

            print("all over")

c = GetTag()
c.getTag(pages=2, tag='tag')

